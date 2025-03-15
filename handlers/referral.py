# handlers/referral.py
import telebot
import config
from db import get_user, clear_pending_referral, add_referral
from handlers.logs import log_event

def extract_referral_code(message):
    """
    Extracts a referral code from the message text.
    Expected format: ref_<referrer_id>
    """
    if message.text and "ref_" in message.text:
        for part in message.text.split():
            if part.startswith("ref_"):
                return part[len("ref_"):]
    return None

def process_verified_referral(telegram_id, bot_instance):
    """
    After a user is verified, this function checks if they have a pending referral.
    If so, it processes the referral:
      - Adds a referral record.
      - Awards the referrer bonus points.
      - Clears the pending referral flag.
      - Notifies the referrer and logs the event.
    """
    user = get_user(str(telegram_id))
    if user and user.get("pending_referrer"):
        referrer_id = user.get("pending_referrer")
        add_referral(referrer_id, user.get("telegram_id"))
        clear_pending_referral(str(telegram_id))
        try:
            bot_instance.send_message(referrer_id, "🎉 Referral completed! You earned bonus points!", parse_mode="HTML")
        except Exception as e:
            print(f"Error notifying referrer: {e}")
        log_event(bot_instance, "referral", f"User {referrer_id} referred user {user.get('telegram_id')}.")

def send_referral_menu(bot, message):
    """
    Sends the referral menu to the user. This includes a button to get their referral link.
    """
    telegram_id = str(message.from_user.id)
    text = "🔗 Referral System\nYour referral link is below."
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("🌟 Get Referral Link", callback_data="get_ref_link"))
    markup.add(telebot.types.InlineKeyboardButton("🔙 Back", callback_data="back_main"))
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="HTML")

def get_referral_link(telegram_id):
    """
    Returns the referral link for the user.
    """
    return f"https://t.me/{config.BOT_USERNAME}?start=ref_{telegram_id}"
