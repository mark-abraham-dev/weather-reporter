from datetime import datetime, timezone, timedelta


def get_utc_now() -> datetime:
    """Get current time in UTC"""
    return datetime.now(timezone.utc)


def format_iso_datetime(dt: datetime) -> str:
    """Format datetime to ISO format"""
    return dt.isoformat()


def get_day_start(dt: datetime) -> datetime:
    """Get the start of the day for given datetime"""
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def get_time_range(days: int) -> tuple[datetime, datetime]:
    """Get a time range from now to N days ago"""
    now = get_utc_now()
    past = now - timedelta(days=days)
    return past, now
