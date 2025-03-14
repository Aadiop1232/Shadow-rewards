"""
db.py - MongoDB-based database module for Shadow Rewards Bot

This module uses PyMongo to connect to a MongoDB instance.
Make sure your config.py includes:
    MONGO_URI and MONGO_DB_NAME, along with other settings.
"""

import config
from pymongo import MongoClient
from datetime import datetime

# For debugging: print the connection URI (ensure it’s the Atlas URI)
print("MONGO_URI:", config.MONGO_URI)

# Establish MongoDB connection
client = MongoClient(config.MONGO_URI)
db = client[config.MONGO_DB_NAME]

# Collections
users_collection = db.users
referrals_collection = db.referrals
platforms_collection = db.platforms
reviews_collection = db.reviews
admin_logs_collection = db.admin_logs
channels_collection = db.channels
admins_collection = db.admins
keys_collection = db.keys
configurations_collection = db.configurations

def init_db():
    """
    Dummy init_db function.
    MongoDB connection is established when this module is imported.
    """
    pass

# -----------------------
# User Functions
# -----------------------

def add_user(telegram_id, username, join_date, pending_referrer=None):
    """
    Add a new user document if one doesn't exist.
    Default points: 20, referrals: 0, banned: False.
    """
    user = get_user(telegram_id)
    if user is None:
        new_user = {
            "telegram_id": telegram_id,
            "username": username,
            "join_date": join_date,
            "points": 20,
            "referrals": 0,
            "banned": False,
            "pending_referrer": pending_referrer,
            "last_checkin": None
        }
        users_collection.insert_one(new_user)
    return get_user(telegram_id)

def get_user(telegram_id):
    """Fetch a user document by telegram_id."""
    return users_collection.find_one({"telegram_id": telegram_id})

def update_user_pending_referral(telegram_id, pending_referrer):
    users_collection.update_one(
        {"telegram_id": telegram_id},
        {"$set": {"pending_referrer": pending_referrer}}
    )

def clear_pending_referral(telegram_id):
    users_collection.update_one(
        {"telegram_id": telegram_id},
        {"$set": {"pending_referrer": None}}
    )

def update_user_points(telegram_id, new_points):
    users_collection.update_one(
        {"telegram_id": telegram_id},
        {"$set": {"points": new_points}}
    )

def ban_user(telegram_id):
    users_collection.update_one(
        {"telegram_id": telegram_id},
        {"$set": {"banned": True}}
    )

def unban_user(telegram_id):
    users_collection.update_one(
        {"telegram_id": telegram_id},
        {"$set": {"banned": False}}
    )

# -----------------------
# Referral Functions
# -----------------------

def add_referral(referrer_id, referred_id):
    """
    Inserts a referral document if one doesn't already exist.
    Increments the referrer's points and referral count.
    """
    existing = referrals_collection.find_one({"referred_id": referred_id})
    if existing:
        return
    referrals_collection.insert_one({
        "referrer_id": referrer_id,
        "referred_id": referred_id,
        "timestamp": datetime.now()
    })
    bonus = get_referral_bonus()
    users_collection.update_one(
        {"telegram_id": referrer_id},
        {"$inc": {"points": bonus, "referrals": 1}}
    )

# -----------------------
# Review Functions
# -----------------------

def add_review(user_id, review_text):
    reviews_collection.insert_one({
        "user_id": user_id,
        "review": review_text,
        "timestamp": datetime.now()
    })

# -----------------------
# Admin Logs Functions
# -----------------------

def log_admin_action(admin_id, action):
    admin_logs_collection.insert_one({
        "admin_id": admin_id,
        "action": action,
        "timestamp": datetime.now()
    })

# -----------------------
# Key Functions
# -----------------------

def get_key(key_str):
    return keys_collection.find_one({"key": key_str})

def claim_key_in_db(key_str, telegram_id):
    key_doc = keys_collection.find_one({"key": key_str})
    if not key_doc:
        return "Key not found."
    if key_doc.get("claimed", False):
        return "Key already claimed."
    points_awarded = key_doc.get("points", 0)
    keys_collection.update_one(
        {"key": key_str},
        {"$set": {"claimed": True, "claimed_by": telegram_id, "claimed_at": datetime.now()}}
    )
    users_collection.update_one(
        {"telegram_id": telegram_id},
        {"$inc": {"points": points_awarded}}
    )
    return f"Key redeemed successfully. You've been awarded {points_awarded} points."

def add_key(key_str, key_type, points):
    keys_collection.insert_one({
        "key": key_str,
        "type": key_type,
        "points": points,
        "claimed": False,
        "claimed_by": None,
        "timestamp": datetime.now()
    })

def get_keys():
    return list(keys_collection.find())

# -----------------------
# Dynamic Configuration Functions
# -----------------------

def set_config_value(key, value):
    configurations_collection.update_one(
        {"key": key},
        {"$set": {"value": value}},
        upsert=True
    )

def get_config_value(key):
    doc = configurations_collection.find_one({"key": key})
    if doc:
        return doc.get("value")
    return None

def set_account_claim_cost(cost):
    set_config_value("account_claim_cost", cost)

def get_account_claim_cost():
    cost = get_config_value("account_claim_cost")
    return cost if cost is not None else config.DEFAULT_ACCOUNT_CLAIM_COST

def set_referral_bonus(bonus):
    set_config_value("referral_bonus", bonus)

def get_referral_bonus():
    bonus = get_config_value("referral_bonus")
    return bonus if bonus is not None else config.DEFAULT_REFERRAL_BONUS

# -----------------------
# Additional Functions
# -----------------------

def get_leaderboard(limit=10):
    cursor = users_collection.find({}, {"telegram_id": 1, "username": 1, "points": 1}).sort("points", -1).limit(limit)
    return list(cursor)

def get_admin_dashboard():
    total_users = users_collection.count_documents({})
    banned_users = users_collection.count_documents({"banned": True})
    pipeline = [{"$group": {"_id": None, "total_points": {"$sum": "$points"}}}]
    result = list(users_collection.aggregate(pipeline))
    total_points = result[0]["total_points"] if result else 0
    return total_users, banned_users, total_points

if __name__ == '__main__':
    test_user = get_user("123456")
    print("Test user:", test_user)
