# messages.py
from logic import calculate_streak, detect_inactivity, performance_trend
from datetime import date
from database import save_message
import random

# -----------------------------
# Predefined Motivational Messages
# -----------------------------
INACTIVITY_MESSAGES = [
    "The couch is winning. Take 5 minutes to stretch and challenge that score!",
    "20 minutes can reset your focus and burn enough energy to sleep better tonight.",
    "Hey! It's been a while. Let's get moving today!",
    "Don't let a few days off stop your progress. Start your workout now!",
    "Every session counts. Time to break the inactivity streak!",
]

STREAK_MESSAGES = [
    "Your future self will thank you for maintaining this",
    "Amazing! You've kept a {streak}-day streak alive!",
    "Keep the momentum! {streak} days in a row – you rock!",
    "Consistency is key. {streak} consecutive days of workouts. Keep it up!",
]

PERFORMANCE_MESSAGES = [
    "You're improving! Your average duration increased from {previous} to {current} minutes.",
    "Great work! You've maintained your performance over the last week.",
    "Noticeable improvement! Keep pushing and watch your results grow.",
]

GENERAL_ENCOURAGEMENT = [
    "20 minutes can be the best mental health break you get all day.",
    "Not every workout needs to be a monster. Consistency is the true powerhouse.",
    "Move, breathe, and feel the difference. You deserve this energy boost."
    "Remember, consistency beats intensity. Keep moving!",
    "Fitness is a journey, not a sprint. Every workout counts.",
]


# -----------------------------
# Determine Trigger Type
# -----------------------------
def get_trigger_type(user_id):
    """
    Identifies why a message is being generated.
    """
    if detect_inactivity(user_id):
        return "Inactivity"

    streak = calculate_streak(user_id)
    if streak > 1:
        return "Streak"

    trend = performance_trend(user_id)
    if trend["current"] > trend["previous"]:
        return "Performance"

    return "General"


# -----------------------------
# Generate + Save Motivational Message
# -----------------------------
def get_motivational_message(user_id):
    """
    Generates a motivational message AND saves it to MessageHistory.
    """

    trigger = get_trigger_type(user_id)

    # Pick the correct message
    if trigger == "Inactivity":
        message = random.choice(INACTIVITY_MESSAGES)

    elif trigger == "Streak":
        streak = calculate_streak(user_id)
        template = random.choice(STREAK_MESSAGES)
        message = template.format(streak=streak)

    elif trigger == "Performance":
        trend = performance_trend(user_id)
        template = random.choice(PERFORMANCE_MESSAGES)
        message = template.format(previous=trend["previous"], current=trend["current"])

    else:  # General
        message = random.choice(GENERAL_ENCOURAGEMENT)

    # Store message in database
    save_message(
        user_id=user_id,
        date_sent=str(date.today()),
        message_text=message,
        trigger_type=trigger,
    )

    return message
