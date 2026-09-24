"""SQLite storage for tasks."""
import os
import sqlite3


def get_db_path():
    """Default database location (override with the PLANNER_PRO_DB env var)."""
    override = os.environ.get("PLANNER_PRO_DB")
    if override:
        return override

    if os.name == "nt":
        base_dir = os.path.join(
            os.environ.get("APPDATA", os.path.expanduser("~")), "PlannerPro"
        )
    else:
        base_dir = os.path.join(os.path.expanduser("~"), ".planner_pro")
    os.makedirs(base_dir, exist_ok=True)
    return os.path.join(base_dir, "planner.db")


class Database:
    """Thin wrapper around the `tasks` table.

    Dates are stored as ISO strings (``yyyy-MM-dd``, Gregorian) and times as
    ``HH:mm`` so they sort correctly as text.
    """

    def __init__(self, path=None):
        self.path = path or get_db_path()
        self.conn = sqlite3.connect(self.path)
        self._init_schema()

    def _init_schema(self):
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                title TEXT,
                done INTEGER,
                start_time TEXT,
                end_time TEXT
            )
            """
        )
        # Migration: older databases have no "notified" column.
        columns = [row[1] for row in cur.execute("PRAGMA table_info(tasks)")]
        if "notified" not in columns:
            cur.execute("ALTER TABLE tasks ADD COLUMN notified INTEGER DEFAULT 0")
        self.conn.commit()

    def close(self):
        self.conn.close()

    # ---- reading -------------------------------------------------------
    def tasks_on(self, date_str):
        """Rows of (id, title, done, start_time, end_time) for one day."""
        cur = self.conn.execute(
            "SELECT id, title, done, start_time, end_time FROM tasks "
            "WHERE date=? ORDER BY start_time",
            (date_str,),
        )
        return cur.fetchall()

    def get_task(self, task_id):
        """(title, start_time, end_time) or None."""
        cur = self.conn.execute(
            "SELECT title, start_time, end_time FROM tasks WHERE id=?", (task_id,)
        )
        return cur.fetchone()

    def day_stats(self, date_str):
        """(done_count, total_count) for one day."""
        cur = self.conn.execute(
            "SELECT COALESCE(SUM(done), 0), COUNT(*) FROM tasks WHERE date=?",
            (date_str,),
        )
        done, total = cur.fetchone()
        return int(done), int(total)

    def search(self, text, limit=50):
        """Rows of (date, title, start_time, end_time, done), newest first."""
        text = text.strip()
        if text:
            cur = self.conn.execute(
                "SELECT date, title, start_time, end_time, done FROM tasks "
                "WHERE title LIKE ? ORDER BY date DESC, start_time",
                (f"%{text}%",),
            )
        else:
            cur = self.conn.execute(
                "SELECT date, title, start_time, end_time, done FROM tasks "
                "ORDER BY date DESC, start_time LIMIT ?",
                (limit,),
            )
        return cur.fetchall()

    # ---- writing -------------------------------------------------------
    def add_task(self, date_str, title, start_time, end_time):
        cur = self.conn.execute(
            "INSERT INTO tasks(date, title, done, start_time, end_time, notified) "
            "VALUES(?, ?, 0, ?, ?, 0)",
            (date_str, title, start_time, end_time),
        )
        self.conn.commit()
        return cur.lastrowid

    def update_task(self, task_id, title, start_time, end_time):
        """Edit a task; its reminder is re-armed."""
        self.conn.execute(
            "UPDATE tasks SET title=?, start_time=?, end_time=?, notified=0 WHERE id=?",
            (title, start_time, end_time, task_id),
        )
        self.conn.commit()

    def set_done(self, task_id, done):
        self.conn.execute(
            "UPDATE tasks SET done=? WHERE id=?", (1 if done else 0, task_id)
        )
        self.conn.commit()

    def delete_task(self, task_id):
        self.conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        self.conn.commit()

    # ---- reminders -----------------------------------------------------
    def pending_reminders(self, date_str):
        """(id, title, start_time) of unfinished, not-yet-notified tasks."""
        cur = self.conn.execute(
            "SELECT id, title, start_time FROM tasks "
            "WHERE date=? AND done=0 AND (notified IS NULL OR notified=0)",
            (date_str,),
        )
        return cur.fetchall()

    def mark_notified(self, task_id):
        self.conn.execute("UPDATE tasks SET notified=1 WHERE id=?", (task_id,))
        self.conn.commit()
