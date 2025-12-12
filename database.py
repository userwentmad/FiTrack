import sqlite3
import os
import hashlib

DB_PATH = os.path.join("data", "fitrack.db")


# ================================
# INITIALIZE DATABASE
# ================================
def init_db():
    if not os.path.exists("data"):
        os.makedirs("data")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # -------------------------
    # User Table
    # -------------------------
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS User (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        goal_desc TEXT,
        join_date TEXT
    )
    """
    )

    # -------------------------
    # WorkoutLog Table
    # -------------------------
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS WorkoutLog (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        activity_type TEXT NOT NULL,
        duration INTEGER,
        intensity TEXT,
        calories REAL,
        FOREIGN KEY (user_id) REFERENCES User(user_id)
    )
    """
    )

    # -------------------------
    # MessageHistory Table
    # -------------------------
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS MessageHistory (
        msg_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        date TEXT,
        message TEXT,
        trigger_type TEXT,
        FOREIGN KEY (user_id) REFERENCES User(user_id)
    )
    """
    )

    conn.commit()
    conn.close()
    print("Database initialized correctly!")


# Call initializer
init_db()


# ================================
# INSERT WORKOUT
# ================================
def insert_workout(user_id, date, activity_type, duration, intensity, calories):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO WorkoutLog (user_id, date, activity_type, duration, intensity, calories)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (user_id, date, activity_type, duration, intensity, calories),
    )

    conn.commit()
    conn.close()


# ================================
# INSERT USER PROFILE
# ================================
def insert_user(name, goal_desc, join_date):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO User (name, goal_desc, join_date)
        VALUES (?, ?, ?)
    """,
        (name, goal_desc, join_date),
    )

    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id


# ================================
# SAVE MOTIVATIONAL MESSAGE
# ================================
def save_message(user_id, date_sent, message_text, trigger_type):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO MessageHistory (user_id, date, message, trigger_type)
        VALUES (?, ?, ?, ?)
    """,
        (user_id, date_sent, message_text, trigger_type),
    )

    conn.commit()
    conn.close()


# ================================
# RETRIEVE MESSAGE HISTORY
# ================================
def get_message_history(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT date, message, trigger_type
        FROM MessageHistory
        WHERE user_id = ?
        ORDER BY msg_id DESC
    """,
        (user_id,),
    )

    rows = cursor.fetchall()
    conn.close()
    return rows


# -----------------------------
# Streak Partners support
# -----------------------------
def init_streak_partners_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Partner list
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS StreakPartners (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        partner_name TEXT NOT NULL
    )
    """
    )

    # Partner chat/messages
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS PartnerMessages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        partner_name TEXT NOT NULL,
        sender TEXT NOT NULL,          -- "You" or partner name
        message TEXT NOT NULL,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """
    )

    conn.commit()
    conn.close()


# run initializer (safe to call multiple times)
init_streak_partners_tables()


def add_streak_partner(user_id, partner_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO StreakPartners (user_id, partner_name)
        VALUES (?, ?)
    """,
        (user_id, partner_name),
    )
    conn.commit()
    conn.close()


def get_streak_partners(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, partner_name FROM StreakPartners WHERE user_id=?
    """,
        (user_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows  # list of tuples (id, partner_name)


def add_partner_message(user_id, partner_name, message_text, sender="You"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO PartnerMessages (user_id, partner_name, sender, message)
        VALUES (?, ?, ?, ?)
    """,
        (user_id, partner_name, sender, message_text),
    )

    conn.commit()
    conn.close()


def get_partner_messages(user_id, partner_name=None, limit=100):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if partner_name:
        cursor.execute(
            """
            SELECT sender, message, timestamp
            FROM PartnerMessages
            WHERE user_id=? AND partner_name=?
            ORDER BY id ASC
            LIMIT ?
        """,
            (user_id, partner_name, limit),
        )
    else:
        # return all partner messages for the user
        cursor.execute(
            """
            SELECT partner_name, sender, message, timestamp
            FROM PartnerMessages
            WHERE user_id=?
            ORDER BY id ASC
            LIMIT ?
        """,
            (user_id, limit),
        )

    rows = cursor.fetchall()
    conn.close()
    return rows


def add_auto_partner_alert(user_id, alert_text):
    # add an alert message for all partners of user
    partners = get_streak_partners(user_id)
    for _, pname in partners:
        add_partner_message(
            user_id, pname, alert_text, str(__import__("datetime").date.today())
        )


def delete_partner_and_messages(user_id, partner_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # delete partner record
    cursor.execute(
        """
        DELETE FROM StreakPartners
        WHERE user_id=? AND partner_name=?
    """,
        (user_id, partner_name),
    )

    # delete chat messages for that partner
    cursor.execute(
        """
        DELETE FROM PartnerMessages
        WHERE user_id=? AND partner_name=?
    """,
        (user_id, partner_name),
    )

    conn.commit()
    conn.close()
    return True


# ================================
# AUTH TABLE
# ================================
def init_auth_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS UserAuth (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """
    )

    conn.commit()
    conn.close()


init_auth_table()


# ================================
# HASH PASSWORD
# ================================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ================================
# REGISTER USER
# ================================
def register_user(username, password):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO UserAuth (username, password)
            VALUES (?, ?)
        """,
            (username, hash_password(password)),
        )

        conn.commit()
        conn.close()
        return True, "Account created successfully!"

    except sqlite3.IntegrityError:
        return False, "Username already exists."


# ================================
# LOGIN USER
# ================================
def login_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, password FROM UserAuth WHERE username=?", (username,))
    user = cursor.fetchone()

    conn.close()

    if not user:
        return None

    stored_password = user[1]
    if stored_password == hash_password(password):
        return user[0]  # return user_id

    return None
