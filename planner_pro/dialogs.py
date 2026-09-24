"""Dialogs: add/edit a task and search tasks."""
from PyQt6.QtCore import Qt, QDate, QTime
from PyQt6.QtWidgets import (
    QDialog, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QPushButton, QTimeEdit, QVBoxLayout,
)

from .i18n import tr
from .icons import make_app_icon, make_icon


class TaskDialog(QDialog):
    """Create a new task, or edit one when initial values are given."""

    def __init__(self, title="", start="12:00", end="13:00", editing=False, parent=None):
        super().__init__(parent)
        self.setWindowIcon(make_app_icon())
        self.setWindowTitle(tr("edit_dialog_title" if editing else "add_dialog_title"))
        self.setFixedSize(350, 220)
        self.setStyleSheet("QDialog { background: #0e1318; color: #e8eef4; }")

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(tr("field_title")))
        self.input_title = QLineEdit(title)
        self.input_title.setPlaceholderText(tr("field_title"))
        layout.addWidget(self.input_title)

        layout.addWidget(QLabel(tr("field_start")))
        self.start_time = self._make_time_edit(start, QTime(12, 0))
        layout.addWidget(self.start_time)

        layout.addWidget(QLabel(tr("field_end")))
        self.end_time = self._make_time_edit(end, QTime(13, 0))
        layout.addWidget(self.end_time)

        btn = QPushButton(tr("btn_save"))
        btn.setProperty("primary", True)
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)

    @staticmethod
    def _make_time_edit(value, fallback):
        edit = QTimeEdit()
        parsed = QTime.fromString(value, "HH:mm")
        edit.setTime(parsed if parsed.isValid() else fallback)
        edit.setDisplayFormat("HH:mm")
        return edit

    def get_data(self):
        """(title, start "HH:mm", end "HH:mm")"""
        return (
            self.input_title.text().strip(),
            self.start_time.time().toString("HH:mm"),
            self.end_time.time().toString("HH:mm"),
        )


class SearchDialog(QDialog):
    """Search tasks by title; double-click a result to jump to its day."""

    def __init__(self, db, on_select, parent=None):
        super().__init__(parent)
        self.db = db
        self.on_select = on_select
        self.setWindowIcon(make_app_icon())
        self.setWindowTitle(tr("search_dialog_title"))
        self.setMinimumSize(440, 480)
        self.setStyleSheet("""
            QDialog { background: #0e1318; color: #e8eef4; }
            QLineEdit {
                background:#182029; color:#e8eef4; padding:8px;
                border-radius:8px; border:1px solid #2e3d4d; font-size:14px;
                font-family: 'Cascadia Code', Consolas, monospace;
            }
            QListWidget {
                background:#182029; border-radius:12px; border:1px solid #2e3d4d;
                padding:4px;
            }
            QListWidget::item { padding:8px; border-radius:8px; color:#e8eef4; }
            QListWidget::item:selected { background:#2a3a4a; border:1px solid #8b5cf6; }
        """)

        layout = QVBoxLayout(self)

        search_row = QHBoxLayout()
        icon_lbl = QLabel()
        icon_lbl.setPixmap(make_icon("search", size=20).pixmap(20, 20))
        search_row.addWidget(icon_lbl)
        self.input = QLineEdit()
        self.input.setPlaceholderText(tr("search_placeholder"))
        self.input.textChanged.connect(self.run_search)
        search_row.addWidget(self.input)
        layout.addLayout(search_row)

        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self.select_result)
        layout.addWidget(self.results_list)

        hint = QLabel(tr("search_hint"))
        hint.setStyleSheet("color:#8fa0b2; font-size:11px;")
        layout.addWidget(hint)

        self.input.setFocus()
        self.run_search("")

    def run_search(self, text):
        self.results_list.clear()
        rows = self.db.search(text)

        for date_str, title, start, end, done in rows:
            item = QListWidgetItem(f"{date_str}   {start}-{end}   {title}")
            item.setIcon(make_icon(
                "check-circle" if done else "circle",
                color="#34d399" if done else "#8fa0b2", size=14,
            ))
            item.setData(Qt.ItemDataRole.UserRole, date_str)
            self.results_list.addItem(item)

        if not rows:
            item = QListWidgetItem(tr("search_empty"))
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.results_list.addItem(item)

    def select_result(self, item):
        date_str = item.data(Qt.ItemDataRole.UserRole)
        if not date_str:
            return
        self.on_select(QDate.fromString(date_str, "yyyy-MM-dd"))
        self.accept()
