import sqlite3

import pytest

from planner_pro.db import Database


@pytest.fixture
def db(tmp_path):
    database = Database(str(tmp_path / "planner.db"))
    yield database
    database.close()


def test_add_and_list_sorted_by_start_time(db):
    db.add_task("2026-09-24", "late", "15:00", "16:00")
    db.add_task("2026-09-24", "early", "08:00", "09:00")
    db.add_task("2026-09-25", "other day", "08:00", "09:00")

    titles = [row[1] for row in db.tasks_on("2026-09-24")]
    assert titles == ["early", "late"]


def test_done_state_and_day_stats(db):
    a = db.add_task("2026-09-24", "a", "08:00", "09:00")
    db.add_task("2026-09-24", "b", "10:00", "11:00")

    assert db.day_stats("2026-09-24") == (0, 2)
    db.set_done(a, True)
    assert db.day_stats("2026-09-24") == (1, 2)
    db.set_done(a, False)
    assert db.day_stats("2026-09-24") == (0, 2)
    assert db.day_stats("2030-01-01") == (0, 0)


def test_update_rearms_reminder(db):
    tid = db.add_task("2026-09-24", "task", "08:00", "09:00")
    db.mark_notified(tid)
    assert db.pending_reminders("2026-09-24") == []

    db.update_task(tid, "task v2", "09:00", "10:00")
    assert db.get_task(tid) == ("task v2", "09:00", "10:00")
    assert [r[0] for r in db.pending_reminders("2026-09-24")] == [tid]


def test_finished_tasks_do_not_remind(db):
    tid = db.add_task("2026-09-24", "task", "08:00", "09:00")
    db.set_done(tid, True)
    assert db.pending_reminders("2026-09-24") == []


def test_delete(db):
    tid = db.add_task("2026-09-24", "task", "08:00", "09:00")
    db.delete_task(tid)
    assert db.tasks_on("2026-09-24") == []
    assert db.get_task(tid) is None


def test_search(db):
    db.add_task("2026-09-24", "Statistics class", "08:00", "09:30")
    db.add_task("2026-09-25", "Gym", "18:00", "19:00")

    assert [r[1] for r in db.search("stat")] == ["Statistics class"]
    assert len(db.search("")) == 2
    assert db.search("nothing") == []


def test_migrates_old_database_without_notified_column(tmp_path):
    path = str(tmp_path / "old.db")
    raw = sqlite3.connect(path)
    raw.execute(
        "CREATE TABLE tasks(id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, "
        "title TEXT, done INTEGER, start_time TEXT, end_time TEXT)"
    )
    raw.execute("INSERT INTO tasks(date,title,done,start_time,end_time) "
                "VALUES('2026-09-24','legacy',0,'08:00','09:00')")
    raw.commit()
    raw.close()

    db = Database(path)
    try:
        assert [r[1] for r in db.pending_reminders("2026-09-24")] == ["legacy"]
    finally:
        db.close()
