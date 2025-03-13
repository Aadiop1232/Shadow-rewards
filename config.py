# config.py
# Configuration file for the bot, including API token, admin and owner details, channels, etc.

# The bot's API token (Replace with your actual bot token)
TOKEN = "7760154469:AAEJxN6o8yOBULqY-5qMMvNCmSlkntJmz7Y"  # Replace this with your actual bot token from BotFather

# The bot's username (Replace with your actual bot username)
BOT_USERNAME = "ShadowRewardsBot"

# List of owner IDs (these users have full control over the bot)
OWNERS = [
    "5822279535",  # Replace with actual user IDs
    "7218606355",
    "7436974867",
    "5933410316"
]

# List of admin IDs (these users can perform administrative tasks)
ADMINS = [
    "1572380763",  # Replace with actual user IDs
    "6061298481"
]

# List of required channels for verification (users must join these channels)
REQUIRED_CHANNELS = [
    "https://t.me/shadowsquad0",  # Replace with your actual channel links
    "https://t.me/Originlabs",
    "https://t.me/Binhub_Originlabs",
    "https://t.me/ShadowsquadHits"
]

# Path to the database (ensure this file exists and is accessible)
DATABASE = "bot.db"  # Use the correct path to your SQLite database file

# Additional settings for verification and other features
VERIFICATION_MESSAGE = "Hey {username}, Welcome to {bot_username}! Please verify yourself by joining the channels below."
VERIFY_BUTTON_TEXT = "✅ Verify"
CHANNEL_JOIN_BUTTON_TEXT = "Join {channel_name}"

