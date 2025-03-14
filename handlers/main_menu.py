# handlers/main_menu.py
import telebot
from telebot import types
from handlers.admin import is_admin

def send_main_menu(bot, update):
    """
    Sends the main menu to the user.
    Includes options for Rewards, Account Info, Referral, Review, Report,
    and if the user is an admin, an Admin Panel button.
    """
    # Determine chat_id and user object for both messages and callback queries
    if hasattr(update, "message"):
        chat_id = update.message.chat.id
        user_obj = update.from_user
    elif hasattr(update, "data"):
        chat_id = update.message.chat.id
        user_obj = update.from_user
    else:
        chat_id = update.chat.id
        user_obj = update.from_user

    # Build the inline keyboard with emojis
    markup = types.InlineKeyboardMarkup(row_width=3)
    btn_rewards = types.InlineKeyboardButton("💳 Rewards", callback_data="menu_rewards")
    btn_account = types.InlineKeyboardButton("👤 Account Info", callback_data="menu_account")
    btn_referral = types.InlineKeyboardButton("🔗 Referral", callback_data="menu_referral")
    btn_review = types.InlineKeyboardButton("💬 Review", callback_data="menu_review")
    btn_report = types.InlineKeyboardButton("📝 Report", callback_data="menu_report")
    markup.add(btn_rewards, btn_account, btn_referral, btn_review, btn_report)

    if is_admin(user_obj):
        btn_admin = types.InlineKeyboardButton("🛠 Admin Panel", callback_data="menu_admin")
        markup.add(btn_admin)

    # Optionally send a quick verification message if needed
    bot.send_message(chat_id, "📋 Main Menu\nPlease choose an option:", reply_markup=markup)
