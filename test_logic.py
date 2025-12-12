from logic import calculate_streak, detect_inactivity, compare_performance, weekly_summary
from database import insert_user, insert_workout
from datetime import datetime, timedelta

# For testing, let's create a test user
user_name = "TestUser"
goal_desc = "Stay fit"
join_date = datetime.today().strftime("%Y-%m-%d")

# Insert test user (uncomment if you haven't inserted in DB yet)
# user_id = insert_user(user_name, goal_desc, join_date)

# For this example, assume the user_id is 1
user_id = 1

# Optional: Insert sample workouts (uncomment if you want fresh test data)
# today = datetime.today().date()
# sample_workouts = [
#     (user_id, today - timedelta(days=6), "Running", 30, "Medium"),
#     (user_id, today - timedelta(days=5), "Cycling", 45, "High"),
#     (user_id, today - timedelta(days=3), "Yoga", 20, "Low"),
#     (user_id, today - timedelta(days=1), "Weights", 40, "High"),
# ]
# for w in sample_workouts:
#     insert_workout(*w)

# Test 1: Streak Calculation
streak = calculate_streak(user_id)
print(f"Current longest streak for user {user_id}: {streak} days")

# Test 2: Inactivity Detection
inactive = detect_inactivity(user_id)
print(f"Is user {user_id} inactive? {'Yes' if inactive else 'No'}")

# Test 3: Performance Comparison
performance_diff = compare_performance(user_id)
if performance_diff is not None:
    print(f"Performance change (last week vs previous week) for user {user_id}: {performance_diff}")
else:
    print(f"Not enough data to compare performance for user {user_id}")

# Test 4: Weekly Summary
summary = weekly_summary(user_id)
print(f"Weekly summary for user {user_id}:\n{summary}")
