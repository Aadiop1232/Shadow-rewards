# handlers/account_info.py
from db import get_user, add_user
from datetime import datetime

def send_account_info(bot, update):
    if hasattr(update, "data"):
        user_obj = update.from_user
        chat_id = update.message.chat.id
    else:
        user_obj = update.from_user
        chat_id = update.chat.id

    telegram_id = str(user_obj.id)
    user = get_user(telegram_id)
    if not user:
        add_user(
            telegram_id,
            user_obj.username or user_obj.first_name,
            datetime.now().strftime("%Y-%m-%d")
        )
        user = get_user(telegram_id)
    
    # Updated to use:
    # user[0]: telegram_id, user[1]: username, user[2]: join_date, user[3]: points, user[4]: referrals
    text = (
        f"<b>👤 Account Info 😁</b>\n"
        f"• <b>Username:</b> {user[1]}\n"
        f"• <b>User ID:</b> {user[0]}\n"
        f"• <b>Join Date:</b> {user[2]}\n"
        f"• <b>Balance:</b> {user[3]} points\n"
        f"• <b>Total Referrals:</b> {user[4]}"
    )
    bot.send_message(chat_id, text, parse_mode="HTML")
    
