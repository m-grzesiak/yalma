from datetime import datetime


def convert_string_to_time(date: str) -> datetime.time:
    return datetime.strptime(date, '%Y-%m-%dT%H:%M:%S').time()


def convert_string_to_date(date: str) -> datetime.date:
    return datetime.strptime(date, '%Y-%m-%dT%H:%M:%S').date()


def make_date_human_ready(date: datetime.date) -> str:
    return date.strftime("%d.%m.%Y")


def make_time_human_ready(date: datetime.date) -> str:
    return date.strftime("%H:%M")
