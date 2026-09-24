from planner_pro.jalali import jalali_days_in_month, shift_month


def test_days_in_month():
    assert jalali_days_in_month(1405, 1) == 31
    assert jalali_days_in_month(1405, 7) == 30
    assert jalali_days_in_month(1404, 12) == 29   # common year
    assert jalali_days_in_month(1403, 12) == 30   # leap year


def test_shift_month():
    assert shift_month(1405, 12, 1) == (1406, 1)
    assert shift_month(1405, 1, -1) == (1404, 12)
    assert shift_month(2026, 9, 0) == (2026, 9)
    assert shift_month(2026, 1, -13) == (2024, 12)
