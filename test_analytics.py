from analytics import user_weekly_summary, user_daily_summary, user_performance_trend, user_average_duration

user_id = 1

print("Weekly summary:", user_weekly_summary(user_id))
print("Daily summary:", user_daily_summary(user_id))
print("Performance trend:", user_performance_trend(user_id))
print("Average duration (7 days):", user_average_duration(user_id))
