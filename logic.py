# logic.py
import sqlite3
from datetime import datetime, timedelta

DB_PATH = "data/fitrack.db"


# -----------------------------
# Workout Data Retrieval
# -----------------------------
def get_user_workouts(user_id):
    """
    Fetch all workout dates for a user.
    Returns a list of datetime.date objects.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT date FROM WorkoutLog WHERE user_id=? ORDER BY date ASC", (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [datetime.strptime(row[0], "%Y-%m-%d").date() for row in rows]


# -----------------------------
# Streak Calculation
# -----------------------------
def calculate_streak(user_id):
    """
    Calculate consecutive days of workouts up to today.
    """
    workouts = get_user_workouts(user_id)
    if not workouts:
        return 0

    workouts.sort(reverse=True)
    streak = 0
    today = datetime.today().date()

    for day in workouts:
        if (today - day).days == streak:
            streak += 1
        else:
            break
    return streak


# -----------------------------
# Inactivity Detection
# -----------------------------
def detect_inactivity(user_id, days_threshold=3):
    """
    Detect if the user has been inactive for `days_threshold` or more days.
    Returns True if inactive.
    """
    workouts = get_user_workouts(user_id)
    if not workouts:
        return True

    last_workout = max(workouts)
    today = datetime.today().date()
    days_missed = (today - last_workout).days

    return days_missed >= days_threshold


# -----------------------------
# Performance Tracking
# -----------------------------
def average_duration(user_id, last_n_days=7):
    """
    Compute average workout duration over the last n days.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cutoff_date = (datetime.today() - timedelta(days=last_n_days)).date()
    cursor.execute(
        """
        SELECT duration FROM WorkoutLog 
        WHERE user_id=? AND date>=?
    """,
        (user_id, cutoff_date),
    )
    durations = [row[0] for row in cursor.fetchall()]
    conn.close()

    if durations:
        return sum(durations) / len(durations)
    return 0


def performance_trend(user_id, last_n_days=14):
    """
    Compare average durations over two consecutive periods.
    Returns a dict with previous vs current averages.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    today = datetime.today().date()
    cutoff_current = today - timedelta(days=last_n_days // 2)
    cutoff_previous = today - timedelta(days=last_n_days)

    # Current period
    cursor.execute(
        """
        SELECT duration FROM WorkoutLog
        WHERE user_id=? AND date>?
    """,
        (user_id, cutoff_current),
    )
    current = [row[0] for row in cursor.fetchall()]

    # Previous period
    cursor.execute(
        """
        SELECT duration FROM WorkoutLog
        WHERE user_id=? AND date<=? AND date>?
    """,
        (user_id, cutoff_current, cutoff_previous),
    )
    previous = [row[0] for row in cursor.fetchall()]
    conn.close()

    avg_current = sum(current) / len(current) if current else 0
    avg_previous = sum(previous) / len(previous) if previous else 0

    return {"previous": avg_previous, "current": avg_current}


# -----------------------------
# Helper Functions
# -----------------------------
def weekly_summary(user_id):
    """
    Returns a summary of workouts per week.
    Output: list of tuples (week_number, workout_count)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT strftime('%W', date) AS week, COUNT(*) 
        FROM WorkoutLog WHERE user_id=? 
        GROUP BY week
    """,
        (user_id,),
    )
    summary = cursor.fetchall()
    conn.close()
    return summary


# -----------------------------
# Performance Comparison
# -----------------------------
def compare_performance(user_id, last_n_days=14):
    """
    Compare user's performance between two consecutive periods.
    Returns a string: "Improving", "Declining", or "Stable".
    """
    trend = performance_trend(user_id, last_n_days)
    prev = trend["previous"]
    curr = trend["current"]

    if curr > prev:
        return "Improving"
    elif curr < prev:
        return "Declining"
    else:
        return "Stable"


def daily_summary(user_id):
    """
    Returns a summary of workouts per day.
    Output: list of tuples (date, workout_count)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT date, COUNT(*) FROM WorkoutLog
        WHERE user_id=?
        GROUP BY date ORDER BY date ASC
    """,
        (user_id,),
    )
    summary = cursor.fetchall()
    conn.close()
    return summary
