"""Headless smoke test: build the window, switch language, use the views."""
import pytest

pytest.importorskip("PyQt6")

from PyQt6.QtCore import QDate, Qt  # noqa: E402
from PyQt6.QtWidgets import QApplication  # noqa: E402

from planner_pro.db import Database  # noqa: E402
from planner_pro.i18n import Language, language  # noqa: E402
from planner_pro.window import PlannerWindow  # noqa: E402


@pytest.fixture(scope="session")
def qapp():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def window(qapp, tmp_path):
    language.set(Language.ENGLISH)
    db = Database(str(tmp_path / "planner.db"))
    win = PlannerWindow(db)
    yield win
    win._really_quit = True
    win.close()
    db.close()
    language.set(Language.ENGLISH)


def test_add_toggle_and_delete_flow(window):
    today = QDate.currentDate().toString("yyyy-MM-dd")
    tid = window.db.add_task(today, "write tests", "09:00", "10:00")
    window.refresh()

    assert window.list_tasks.count() == 1
    item = window.list_tasks.item(0)
    assert item.data(Qt.ItemDataRole.UserRole) == tid

    item.setCheckState(Qt.CheckState.Checked)          # triggers save_done_state
    assert window.db.day_stats(today) == (1, 1)

    window.db.delete_task(tid)
    window.refresh()
    assert window.list_tasks.count() == 0


def test_language_switch_roundtrip(window):
    today = QDate.currentDate().toString("yyyy-MM-dd")
    window.db.add_task(today, "کلاس Data Science", "09:00", "13:00")

    window.change_language(Language.PERSIAN)
    assert window.tabs.tabText(0) == "روزانه"
    assert window.week_layout.count() == 7
    assert window.list_tasks.count() == 1

    window.change_language(Language.ENGLISH)
    assert window.tabs.tabText(0) == "Daily"
    assert window.week_layout.count() == 7


def test_week_and_month_navigation(window):
    for lang in (Language.ENGLISH, Language.PERSIAN):
        window.change_language(lang)
        first_week = window.current_week_start
        window.change_week(1)
        assert window.current_week_start == first_week.addDays(7)
        window.change_week(-1)
        for _ in range(14):        # cross a year boundary in both directions
            window.change_month(1)
        for _ in range(28):
            window.change_month(-1)
        assert window.month_layout.count() >= 29


def test_due_reminder_is_fired_once(window, monkeypatch):
    fired = []
    monkeypatch.setattr("planner_pro.window.notify", lambda t, b: fired.append(b) or True)

    today = QDate.currentDate().toString("yyyy-MM-dd")
    window.db.add_task(today, "due now", "00:00", "00:30")   # start time already passed
    window.check_reminders()
    window.check_reminders()

    assert len(fired) == 1
