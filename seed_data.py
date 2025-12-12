from database import insert_workout, insert_user
from datetime import datetime

# Create a user
user_id = insert_user(
    "Shahriar", "Build consistent workout habits", datetime.now().strftime("%Y-%m-%d")
)

# Add workouts
insert_workout(user_id, "2025-01-10", "Running", 30, "Medium")
insert_workout(user_id, "2025-01-11", "Cycling", 45, "High")
insert_workout(user_id, "2025-01-13", "Yoga", 20, "Low")

print("Data inserted successfully!")
