from datetime import datetime
from math import ceil

FREE_MINUTES = 15
HOURLY_RATE = 8
DAILY_CAP = 80


def parse_datetime(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)


def calculate_fee(entry_time, exit_time):
    started_at = parse_datetime(entry_time)
    ended_at = parse_datetime(exit_time)
    minutes = max(0, (ended_at - started_at).total_seconds() / 60)

    if minutes <= FREE_MINUTES:
        return {
            "duration_hours": round(minutes / 60, 2),
            "amount": 0,
            "free_minutes": FREE_MINUTES,
            "rate": HOURLY_RATE,
        }

    billable_hours = ceil((minutes - FREE_MINUTES) / 60)
    days = billable_hours // 24
    remaining_hours = billable_hours % 24
    amount = days * DAILY_CAP + min(remaining_hours * HOURLY_RATE, DAILY_CAP)

    return {
        "duration_hours": round(minutes / 60, 2),
        "amount": round(amount, 2),
        "free_minutes": FREE_MINUTES,
        "rate": HOURLY_RATE,
    }
