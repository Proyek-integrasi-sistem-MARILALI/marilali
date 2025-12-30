from datetime import datetime, timedelta

def calculate_activity_duration(start_time: datetime, end_time: datetime) -> timedelta:
    return end_time - start_time

def is_activity_overlap(activity1_start, activity1_end, activity2_start, activity2_end) -> bool:
    return activity1_start < activity2_end and activity2_start < activity1_end
