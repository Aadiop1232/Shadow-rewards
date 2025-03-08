# db.py
import sqlite3

DATABASE = "bot.db"

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT,
            join_date TEXT,
            points INTEGER DEFAULT 0,
            referrals INTEGER DEFAULT 0,
            banned INTEGER DEFAULT 0,
            pending_referrer TEXT
        )
    ''')
    
    # Referrals table
    c.execute('''
        CREATE TABLE IF NOT EXISTS referrals (
            user_id TEXT,
            referred_id TEXT,
            PRIMARY KEY (user_id, referred_id)
        )
    ''')
    
    # Platforms table
    c.execute('''
        CREATE TABLE IF NOT EXISTS platforms (
            platform_name TEXT PRIMARY KEY,
            stock TEXT
        )
    ''')
    
    # Reviews table
    c.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            review TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Admin logs table
    c.execute('''
        CREATE TABLE IF NOT EXISTS admin_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id TEXT,
            action TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Channels table
    c.execute('''
        CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_link TEXT
        )
    ''')
    
    # Admins table
    c.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            user_id TEXT PRIMARY KEY,
            username TEXT,
            role TEXT,
            banned INTEGER DEFAULT 0
        )
    ''')
    
    # Keys table
    c.execute('''
        CREATE TABLE IF NOT EXISTS keys (
            key TEXT PRIMARY KEY,
            type TEXT,
            points INTEGER,
            claimed INTEGER DEFAULT 0,
            claimed_by TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def add_user(user_id, username, join_date, pending_referrer=None):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username, join_date, pending_referrer) VALUES (?, ?, ?, ?)",
              (user_id, username, join_date, pending_referrer))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def update_user_pending_referral(user_id, pending_referrer):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("UPDATE users SET pending_referrer=? WHERE user_id=?", (pending_referrer, user_id))
    conn.commit()
    conn.close()

def clear_pending_referral(user_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("UPDATE users SET pending_referrer=NULL WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def add_referral(referrer_id, referred_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM referrals WHERE referred_id=?", (referred_id,))
    if c.fetchone():
        conn.close()
        return
    c.execute("INSERT INTO referrals (user_id, referred_id) VALUES (?, ?)", (referrer_id, referred_id))
    c.execute("UPDATE users SET points = points + 4, referrals = referrals + 1 WHERE user_id=?", (referrer_id,))
    conn.commit()
    conn.close()

def add_review(user_id, review):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("INSERT INTO reviews (user_id, review) VALUES (?, ?)", (user_id, review))
    conn.commit()
    conn.close()

def log_admin_action(admin_id, action):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("INSERT INTO admin_logs (admin_id, action) VALUES (?, ?)", (admin_id, action))
    conn.commit()
    conn.close()

# --- Key Claim Functions ---
def get_key(key):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT key, type, points, claimed FROM keys WHERE key=?", (key,))
    result = c.fetchone()
    conn.close()
    return result

def claim_key_in_db(key, user_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT claimed, type, points FROM keys WHERE key=?", (key,))
    row = c.fetchone()
    if not row:
        conn.close()
        return "Key not found."
    if row[0] != 0:
        conn.close()
        return "Key already claimed."
    points = row[2]
    c.execute("UPDATE keys SET claimed=1, claimed_by=? WHERE key=?", (user_id, key))
    c.execute("UPDATE users SET points = points + ? WHERE user_id=?", (points, user_id))
    conn.commit()
    conn.close()
    return f"Key claimed successfully. You've been awarded {points} points."
