from datetime import datetime


def convert_date(date: str) -> datetime:
    return datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %Z")
