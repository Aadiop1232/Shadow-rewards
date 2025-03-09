# main.py
import telebot
import config
from datetime import datetime
from db import init_db, add_user, get_user, claim_key_in_db, update_user_points
from handlers.verification import send_verification_message, handle_verification_callback
from handlers.main_menu import send_main_menu
from handlers.referral import extract_referral_code, process_verified_referral, send_referral_menu, get_referral_link
from handlers.rewards import send_rewards_menu, handle_platform_selection, claim_account
from handlers.account_info import send_account_info
from handlers.review import prompt_review
from handlers.admin import send_admin_menu, admin_callback_handler, is_admin, generate_normal_key, generate_premium_key, add_key
import sys

bot = telebot.TeleBot(config.TOKEN, parse_mode="HTML")
init_db()

@bot.message_handler(commands=["start"])
def start_command(message):
    telegram_id = str(message.from_user.id)
    print(f"DEBUG: /start from telegram id: {telegram_id}")
    pending_ref = extract_referral_code(message)
    user = get_user(telegram_id)
    if not user:
        add_user(
            telegram_id,
            message.from_user.username or message.from_user.first_name,
            datetime.now().strftime("%Y-%m-%d"),
            pending_referrer=pending_ref
        )
    send_verification_message(bot, message)

@bot.message_handler(commands=["gen"])
def gen_command(message):
    telegram_id = str(message.from_user.id)
    if not is_admin(telegram_id):
        bot.reply_to(message, "🚫 You do not have permission to generate keys.")
        return
    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(message, "Usage: /gen <normal|premium> <quantity>")
        return
    key_type = parts[1].lower()
    try:
        qty = int(parts[2])
    except ValueError:
        bot.reply_to(message, "Quantity must be a number.")
        return
    generated = []
    if key_type == "normal":
        for _ in range(qty):
            key = generate_normal_key()
            add_key(key, "normal", 15)
            generated.append(key)
    elif key_type == "premium":
        for _ in range(qty):
            key = generate_premium_key()
            add_key(key, "premium", 35)
            generated.append(key)
    else:
        bot.reply_to(message, "Key type must be either 'normal' or 'premium'.")
        return
    bot.reply_to(message, "Generated keys:\n" + "\n".join(generated))
    for owner in config.OWNERS:
        try:
            bot.send_message(owner, f"🔑 Keys Generated by {message.from_user.username or message.from_user.first_name} ({telegram_id}):\n" + "\n".join(generated))
        except Exception as e:
            print(f"Error notifying owner {owner}: {e}")

@bot.message_handler(commands=["redeem"])
def redeem_command(message):
    telegram_id = str(message.from_user.id)
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "Usage: /redeem <key>")
        return
    key = parts[1].strip()
    result = claim_key_in_db(key, telegram_id)
    bot.reply_to(message, result)
    if "successfully" in result:
        try:
            bot.send_message(config.OWNERS[0], f"🔔 Key redeemed: {key} by {message.from_user.username or message.from_user.first_name} ({telegram_id})")
        except Exception as e:
            print(f"Error notifying owner: {e}")

@bot.message_handler(commands=["lend"])
def lend_command(message):
    telegram_id = str(message.from_user.id)
    if telegram_id not in config.OWNERS:
        bot.reply_to(message, "🚫 Only owners can use this command.")
        return
    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(message, "Usage: /lend <userid> <points>")
        return
    target_internal_id = parts[1].strip()
    try:
        pts = int(parts[2])
    except ValueError:
        bot.reply_to(message, "Points must be a number.")
        return
    from db import get_user, update_user_points
    target = None
    conn = __import__('sqlite3').connect(config.DATABASE)
    c = conn.cursor()
    c.execute("SELECT telegram_id, internal_id, points FROM users WHERE internal_id=?", (target_internal_id,))
    target = c.fetchone()
    conn.close()
    if target is None:
        bot.reply_to(message, "User not found.")
        return
    new_points = target[2] + pts
    update_user_points(target[0], new_points)
    bot.reply_to(message, f"✅ {pts} points added to {target_internal_id}. New balance: {new_points}")
    for owner in config.OWNERS:
        try:
            bot.send_message(owner, f"📣 {message.from_user.username} ({telegram_id}) lent {pts} points to {target_internal_id}.")
        except Exception as e:
            print(f"Error notifying owner: {e}")

@bot.message_handler(commands=["notify"])
def notify_command(message):
    telegram_id = str(message.from_user.id)
    if not is_admin(telegram_id):
        bot.reply_to(message, "🚫 You do not have permission to use /notify.")
        return
    notify_text = message.text.partition(" ")[2]
    if not notify_text:
        bot.reply_to(message, "Usage: /notify <message>")
        return
    recipients = config.OWNERS + config.ADMINS
    for rec in recipients:
        try:
            bot.send_message(rec, f"📢 Notification from {message.from_user.username} ({telegram_id}):\n\n{notify_text}", parse_mode="HTML")
        except Exception as e:
            print(f"Error notifying {rec}: {e}")
    bot.reply_to(message, "Notification sent.")

@bot.message_handler(commands=["tutorial"])
def tutorial_command(message):
    text = (
        "📖 <b>Tutorial</b>\n"
        "1. Every new user starts with 20 points (each account claim costs 2 points).\n"
        "2. To claim an account, go to the Rewards section. If you have at least 2 points, you can claim an account (2 points will be deducted).\n"
        "3. Earn more points by referring friends (each referral gives 4 points) or redeeming keys (/redeem &lt;key&gt;).\n"
        "4. Admins/Owners can generate keys using /gen and lend points using /lend.\n"
        "5. Use /notify to broadcast a message to all owners/admins.\n"
        "6. Your account info always shows your real-time balance and referral count (using your internal User ID).\n"
        "Good luck! 😊"
    )
    bot.send_message(message.chat.id, text, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data == "back_main")
def callback_back_main(call):
    send_main_menu(bot, call.message)

@bot.callback_query_handler(func=lambda call: call.data == "get_ref_link")
def callback_get_ref_link(call):
    ref_link = get_referral_link(call.from_user.id)
    try:
        bot.answer_callback_query(call.id, "Referral link generated!")
    except Exception:
        pass
    bot.send_message(call.message.chat.id, f"Your referral link:\n{ref_link}", parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data == "menu_rewards")
def callback_menu_rewards(call):
    send_rewards_menu(bot, call.message)

@bot.callback_query_handler(func=lambda call: call.data.startswith("reward_"))
def callback_reward(call):
    platform = call.data.split("reward_")[1]
    handle_platform_selection(bot, call, platform)

@bot.callback_query_handler(func=lambda call: call.data.startswith("claim_"))
def callback_claim(call):
    platform = call.data.split("claim_")[1]
    claim_account(bot, call, platform)

@bot.callback_query_handler(func=lambda call: call.data == "menu_account")
def callback_menu_account(call):
    try:
        bot.answer_callback_query(call.id)
    except Exception:
        pass
    send_account_info(bot, call)

@bot.callback_query_handler(func=lambda call: call.data == "menu_referral")
def callback_menu_referral(call):
    send_referral_menu(bot, call.message)

@bot.callback_query_handler(func=lambda call: call.data == "menu_review")
def callback_menu_review(call):
    prompt_review(bot, call.message)

@bot.callback_query_handler(func=lambda call: call.data == "menu_admin")
def callback_menu_admin(call):
    send_admin_menu(bot, call.message)

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin"))
def callback_admin(call):
    admin_callback_handler(bot, call)

@bot.callback_query_handler(func=lambda call: call.data == "verify")
def callback_verify(call):
    handle_verification_callback(bot, call)
    process_verified_referral(call.from_user.id)

bot.polling(none_stop=True)
        
