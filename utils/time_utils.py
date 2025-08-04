"""
Time utility functions for WorkBuddy app.
Provides helper functions for time formatting and conversion.
"""

from datetime import datetime, timedelta
from typing import Tuple


def seconds_to_hms(seconds: int) -> Tuple[int, int, int]:
    """Convert seconds to hours, minutes, seconds."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return hours, minutes, secs


def format_duration(seconds: int, short_format: bool = False) -> str:
    """Format duration in a human-readable way."""
    if seconds < 60:
        return f"{seconds}s" if short_format else f"{seconds} seconds"
    
    hours, minutes, secs = seconds_to_hms(seconds)
    
    if short_format:
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m {secs}s" if secs > 0 else f"{minutes}m"
    else:
        parts = []
        if hours > 0:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes > 0:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        if secs > 0 and hours == 0:  # Only show seconds if less than an hour
            parts.append(f"{secs} second{'s' if secs != 1 else ''}")
        
        if len(parts) == 0:
            return "0 seconds"
        elif len(parts) == 1:
            return parts[0]
        elif len(parts) == 2:
            return f"{parts[0]} and {parts[1]}"
        else:
            return f"{', '.join(parts[:-1])}, and {parts[-1]}"


def format_time_for_display(dt: datetime) -> str:
    """Format datetime for display purposes."""
    return dt.strftime("%H:%M:%S")


def format_date_for_display(dt: datetime) -> str:
    """Format date for display purposes."""
    return dt.strftime("%Y-%m-%d")


def get_time_period_label(start_time: datetime, end_time: datetime = None) -> str:
    """Get a human-readable label for a time period."""
    if end_time is None:
        end_time = datetime.now()
    
    duration = end_time - start_time
    
    if duration.total_seconds() < 3600:  # Less than 1 hour
        return "Short session"
    elif duration.total_seconds() < 14400:  # Less than 4 hours
        return "Medium session"
    else:
        return "Long session"


def is_same_day(dt1: datetime, dt2: datetime) -> bool:
    """Check if two datetimes are on the same day."""
    return dt1.date() == dt2.date()


def get_start_of_day(dt: datetime = None) -> datetime:
    """Get the start of day (00:00:00) for a given datetime."""
    if dt is None:
        dt = datetime.now()
    return datetime.combine(dt.date(), datetime.min.time())


def get_end_of_day(dt: datetime = None) -> datetime:
    """Get the end of day (23:59:59) for a given datetime."""
    if dt is None:
        dt = datetime.now()
    return datetime.combine(dt.date(), datetime.max.time())


def minutes_until_time(target_time_str: str) -> int:
    """Calculate minutes until a specific time (HH:MM format)."""
    try:
        now = datetime.now()
        target_time = datetime.strptime(target_time_str, "%H:%M").time()
        target_datetime = datetime.combine(now.date(), target_time)
        
        # If target time has passed today, calculate for tomorrow
        if target_datetime <= now:
            target_datetime += timedelta(days=1)
        
        diff = target_datetime - now
        return int(diff.total_seconds() / 60)
    except ValueError:
        return 0


def time_ago(dt: datetime) -> str:
    """Get a human-readable 'time ago' string."""
    now = datetime.now()
    diff = now - dt
    
    seconds = int(diff.total_seconds())
    
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    else:
        days = seconds // 86400
        return f"{days} day{'s' if days != 1 else ''} ago"


def get_productivity_score(total_work_time: int, total_break_time: int) -> float:
    """Calculate a simple productivity score based on work/break ratio."""
    if total_work_time == 0:
        return 0.0
    
    # Ideal ratio is around 80% work, 20% breaks
    total_time = total_work_time + total_break_time
    work_percentage = total_work_time / total_time
    
    # Score is best when work percentage is around 0.8
    ideal_ratio = 0.8
    score = 1.0 - abs(work_percentage - ideal_ratio) / ideal_ratio
    return max(0.0, min(1.0, score))


def get_work_day_bounds() -> Tuple[datetime, datetime]:
    """Get typical work day start and end times for today."""
    today = datetime.now().date()
    work_start = datetime.combine(today, datetime.strptime("09:00", "%H:%M").time())
    work_end = datetime.combine(today, datetime.strptime("17:00", "%H:%M").time())
    return work_start, work_end


def is_weekend() -> bool:
    """Check if today is weekend (Saturday or Sunday)."""
    return datetime.now().weekday() >= 5


def get_next_workday() -> datetime:
    """Get the next workday (Monday if today is Friday, tomorrow otherwise)."""
    today = datetime.now()
    
    # If it's Friday (4), next workday is Monday (+3 days)
    # If it's Saturday (5), next workday is Monday (+2 days)  
    # If it's Sunday (6), next workday is Monday (+1 day)
    if today.weekday() == 4:  # Friday
        return today + timedelta(days=3)
    elif today.weekday() == 5:  # Saturday
        return today + timedelta(days=2)
    elif today.weekday() == 6:  # Sunday
        return today + timedelta(days=1)
    else:  # Monday-Thursday
        return today + timedelta(days=1)


if __name__ == "__main__":
    # Test the utility functions
    print("Testing time utility functions:")
    
    # Test duration formatting
    print(f"3661 seconds = {format_duration(3661)}")
    print(f"3661 seconds (short) = {format_duration(3661, short_format=True)}")
    
    # Test time formatting
    now = datetime.now()
    print(f"Current time: {format_time_for_display(now)}")
    print(f"Current date: {format_date_for_display(now)}")
    
    # Test time ago
    past_time = now - timedelta(hours=2, minutes=30)
    print(f"Time ago: {time_ago(past_time)}")
    
    # Test productivity score
    score = get_productivity_score(7200, 1800)  # 2 hours work, 30 min break
    print(f"Productivity score: {score:.2f}")
    
    print("\nAll tests completed!") 