from telebot import types
from handlers.admin import is_admin

def send_main_menu(bot, update):
    if hasattr(update, "message") and update.message:
        chat_id = update.message.chat.id
        user = update.message.from_user
    elif hasattr(update, "data"):
        chat_id = update.message.chat.id
        user = update.from_user
    else:
        chat_id = update.chat.id
        user = update.from_user

    markup = types.InlineKeyboardMarkup(row_width=3)
    markup.add(
        types.InlineKeyboardButton("🎉 Rewards", callback_data="menu_rewards"),
        types.InlineKeyboardButton("👥 Info", callback_data="menu_info"),
        types.InlineKeyboardButton("🤝 Referral", callback_data="menu_referral")
    )
    markup.add(
        types.InlineKeyboardButton("📠 Review", callback_data="menu_review"),
    )
    if is_admin(user):
        markup.add(types.InlineKeyboardButton("🔨 Admin Panel", callback_data="menu_admin"))
    bot.send_message(chat_id, "Main Menu\nPlease choose an option:", reply_markup=markup)
    
