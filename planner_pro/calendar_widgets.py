"""Month-grid calendar widgets (Gregorian and Jalali)."""
import jdatetime
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget,
)

from .i18n import ENGLISH_MONTHS
from .icons import make_icon
from .jalali import (
    PERSIAN_MONTHS, jalali_days_in_month, jdate_to_qdate, qdate_to_jdate,
    shift_month,
)

_SELECTED_STYLE = """
    QPushButton {
        background:#8b5cf6; color:#0e1318; border-radius:8px;
        font-weight:bold; border:1px solid #a684ff; padding:0;
    }
"""
_NORMAL_STYLE = """
    QPushButton {
        background:#22303c; color:#e8eef4; border-radius:8px;
        border:1px solid #2e3d4d; padding:0;
    }
    QPushButton:hover { background:#2a3a4a; border-color:#8fa0b2; }
"""


class _MonthGridCalendarBase(QWidget):
    """Shared UI and navigation; subclasses provide the calendar maths."""

    selectionChanged = pyqtSignal()
    WEEKDAY_LABELS = []

    def __init__(self, parent=None):
        super().__init__(parent)
        self._day_buttons = []
        self._build_ui()
        self._init_view()
        self._render_days()

    # ---- to be provided by subclasses ---------------------------------
    def _init_view(self):
        raise NotImplementedError

    def _header_text(self):
        raise NotImplementedError

    def _days_in_view_month(self):
        raise NotImplementedError

    def _first_weekday_col(self):
        raise NotImplementedError

    def _is_selected(self, day):
        raise NotImplementedError

    def _select_day(self, day):
        raise NotImplementedError

    def setSelectedDate(self, qdate):
        raise NotImplementedError

    # ---- shared -------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        nav = QHBoxLayout()
        left_btn = QPushButton()
        left_btn.setFixedWidth(36)
        left_btn.setIcon(make_icon("chevron-left"))
        left_btn.clicked.connect(lambda: self._change_month(-1))
        right_btn = QPushButton()
        right_btn.setFixedWidth(36)
        right_btn.setIcon(make_icon("chevron-right"))
        right_btn.clicked.connect(lambda: self._change_month(1))

        self.header_label = QLabel()
        self.header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header_label.setFont(QFont("Arial", 13, QFont.Weight.Bold))

        nav.addWidget(left_btn)
        nav.addWidget(self.header_label, 1)
        nav.addWidget(right_btn)
        layout.addLayout(nav)

        weekday_row = QHBoxLayout()
        weekday_row.setSpacing(4)
        for name in self.WEEKDAY_LABELS:
            lbl = QLabel(name)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("color:#8b5cf6; font-weight:bold;")
            weekday_row.addWidget(lbl)
        layout.addLayout(weekday_row)

        self.grid = QGridLayout()
        self.grid.setSpacing(4)
        layout.addLayout(self.grid)
        layout.addStretch()

        self.setStyleSheet("""
            QWidget {
                background: #182029;
                border-radius: 12px;
                border: 1px solid #2e3d4d;
            }
        """)

    def _change_month(self, offset):
        self._view_year, self._view_month = shift_month(
            self._view_year, self._view_month, offset
        )
        self._render_days()

    def _render_days(self):
        for btn in self._day_buttons:
            self.grid.removeWidget(btn)
            btn.setParent(None)  # disappear immediately, don't wait for deleteLater
            btn.deleteLater()
        self._day_buttons = []

        self.header_label.setText(self._header_text())

        row, col = 0, self._first_weekday_col()
        for day in range(1, self._days_in_view_month() + 1):
            btn = QPushButton(str(day))
            btn.setFixedSize(46, 40)
            btn.setFont(QFont("Cascadia Code", 12))
            btn.setStyleSheet(_SELECTED_STYLE if self._is_selected(day) else _NORMAL_STYLE)
            btn.clicked.connect(lambda checked, d=day: self._select_day(d))
            self.grid.addWidget(btn, row, col)
            self._day_buttons.append(btn)

            col += 1
            if col > 6:
                col = 0
                row += 1

    def selectedDate(self):
        return self._selected_date


class PersianCalendarWidget(_MonthGridCalendarBase):
    WEEKDAY_LABELS = ["ش", "ی", "د", "س", "چ", "پ", "ج"]

    def _init_view(self):
        self._selected_date = QDate.currentDate()
        jtoday = qdate_to_jdate(self._selected_date)
        self._view_year = jtoday.year
        self._view_month = jtoday.month

    def _header_text(self):
        return f"{PERSIAN_MONTHS[self._view_month - 1]} {self._view_year}"

    def _days_in_view_month(self):
        return jalali_days_in_month(self._view_year, self._view_month)

    def _first_weekday_col(self):
        # jdatetime: Saturday == 0
        return jdatetime.date(self._view_year, self._view_month, 1).weekday()

    def _is_selected(self, day):
        sel = qdate_to_jdate(self._selected_date)
        return (sel.year, sel.month, sel.day) == (self._view_year, self._view_month, day)

    def _select_day(self, day):
        jd = jdatetime.date(self._view_year, self._view_month, day)
        self._selected_date = jdate_to_qdate(jd)
        self._render_days()
        self.selectionChanged.emit()

    def setSelectedDate(self, qdate):
        self._selected_date = qdate
        jdate = qdate_to_jdate(qdate)
        self._view_year = jdate.year
        self._view_month = jdate.month
        self._render_days()


class EnglishCalendarWidget(_MonthGridCalendarBase):
    WEEKDAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    def _init_view(self):
        self._selected_date = QDate.currentDate()
        self._view_year = self._selected_date.year()
        self._view_month = self._selected_date.month()

    def _header_text(self):
        return f"{ENGLISH_MONTHS[self._view_month - 1]} {self._view_year}"

    def _days_in_view_month(self):
        return QDate(self._view_year, self._view_month, 1).daysInMonth()

    def _first_weekday_col(self):
        return QDate(self._view_year, self._view_month, 1).dayOfWeek() - 1

    def _is_selected(self, day):
        d = self._selected_date
        return (d.year(), d.month(), d.day()) == (self._view_year, self._view_month, day)

    def _select_day(self, day):
        self._selected_date = QDate(self._view_year, self._view_month, day)
        self._render_days()
        self.selectionChanged.emit()

    def setSelectedDate(self, qdate):
        self._selected_date = qdate
        self._view_year = qdate.year()
        self._view_month = qdate.month()
        self._render_days()
