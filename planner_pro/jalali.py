"""Helpers for working with Jalali (Persian) dates."""
import jdatetime
from PyQt6.QtCore import QDate

PERSIAN_MONTHS = [
    "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند",
]

# The Persian week starts on Saturday.
PERSIAN_WEEKDAYS = [
    "شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه",
]


def jalali_days_in_month(year, month):
    """Number of days in a Jalali month (Esfand has 30 days in leap years)."""
    if month <= 6:
        return 31
    if month <= 11:
        return 30
    return 30 if jdatetime.date(year, 1, 1).isleap() else 29


def qdate_to_jdate(qdate):
    return jdatetime.date.fromgregorian(
        year=qdate.year(), month=qdate.month(), day=qdate.day()
    )


def jdate_to_qdate(jdate):
    g = jdate.togregorian()
    return QDate(g.year, g.month, g.day)


def shift_month(year, month, offset):
    """Return (year, month) moved by `offset` months (works for negatives)."""
    total = year * 12 + (month - 1) + offset
    return total // 12, total % 12 + 1
