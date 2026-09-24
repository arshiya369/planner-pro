"""Main application window: daily, weekly and monthly views."""
import logging

import jdatetime
from PyQt6.QtCore import Qt, QDate, QSize, QTime, QTimer
from PyQt6.QtGui import QAction, QColor, QFont
from PyQt6.QtWidgets import (
    QApplication, QFrame, QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QMenu, QMessageBox, QProgressBar,
    QPushButton, QScrollArea, QSizePolicy, QSystemTrayIcon, QTabWidget,
    QVBoxLayout, QWidget,
)

from .calendar_widgets import EnglishCalendarWidget, PersianCalendarWidget
from .dialogs import SearchDialog, TaskDialog
from .i18n import ENGLISH_WEEKDAYS_SHORT, Language, language, tr
from .icons import make_app_icon, make_icon
from .jalali import (
    PERSIAN_MONTHS, PERSIAN_WEEKDAYS, jalali_days_in_month, jdate_to_qdate,
    qdate_to_jdate, shift_month,
)
from .notifications import notify
from .styles import APP_STYLESHEET

logger = logging.getLogger(__name__)

REMINDER_INTERVAL_MS = 20 * 1000
ISO_DATE = "yyyy-MM-dd"


def _clear_layout(layout):
    """Remove and delete every widget in `layout`."""
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.setParent(None)
            widget.deleteLater()


def percent_color(percent):
    """Colour from red (0%) through amber to green (100%)."""
    if percent <= 0:
        return QColor("#f87171")
    if percent >= 100:
        return QColor("#34d399")
    if percent <= 50:
        ratio = percent / 50
        return QColor(248, int(113 + (191 - 113) * ratio), int(113 - (113 - 36) * ratio))
    ratio = (percent - 50) / 50
    return QColor(int(251 - (251 - 52) * ratio),
                  int(191 + (211 - 191) * ratio),
                  int(36 + (153 - 36) * ratio))


class PlannerWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self._really_quit = False

        self.setWindowIcon(make_app_icon())
        self.resize(1250, 750)

        main_layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        self.tabs.setIconSize(QSize(18, 18))
        main_layout.addWidget(self.tabs)

        self._build_language_menu()
        self.tabs.setCornerWidget(self.menu_widget, Qt.Corner.TopRightCorner)

        self._build_daily_tab()
        self._build_week_tab()
        self._build_month_tab()
        self.setStyleSheet(APP_STYLESHEET)

        self._build_tray()
        self.retranslate()
        self.refresh()
        self._start_reminder_timer()

    # ==================================================================
    # UI construction
    # ==================================================================
    def _build_language_menu(self):
        self.menu_widget = QWidget()
        layout = QHBoxLayout(self.menu_widget)
        layout.setContentsMargins(8, 2, 8, 2)
        layout.setSpacing(6)

        globe = QLabel()
        globe.setPixmap(make_icon("globe", size=18).pixmap(18, 18))
        layout.addWidget(globe)

        self.search_btn = QPushButton()
        self.search_btn.setIcon(make_icon("search"))
        self.search_btn.setFixedWidth(36)
        self.search_btn.clicked.connect(self.open_search_dialog)
        layout.addWidget(self.search_btn)

        self.eng_btn = QPushButton("English")
        self.eng_btn.setCheckable(True)
        self.eng_btn.setChecked(language.is_english())
        self.eng_btn.setFixedWidth(90)
        self.eng_btn.clicked.connect(lambda: self.change_language(Language.ENGLISH))
        layout.addWidget(self.eng_btn)

        self.per_btn = QPushButton("فارسی")
        self.per_btn.setCheckable(True)
        self.per_btn.setChecked(language.is_persian())
        self.per_btn.setFixedWidth(90)
        self.per_btn.clicked.connect(lambda: self.change_language(Language.PERSIAN))
        layout.addWidget(self.per_btn)

    def _build_daily_tab(self):
        daily_tab = QWidget()
        layout = QHBoxLayout(daily_tab)

        # left: date banner + calendar
        left_container = QWidget()
        left_container.setFixedWidth(400)
        self.left_layout = QVBoxLayout(left_container)
        self.left_layout.setContentsMargins(0, 0, 10, 0)

        self.today_label = QLabel()
        self.today_label.setFont(QFont("Cascadia Code", 14, QFont.Weight.Bold))
        self.today_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.today_label.setStyleSheet("""
            QLabel {
                background: #182029;
                color: #e8eef4;
                border-radius: 12px;
                padding: 10px;
                margin-bottom: 10px;
                border: 1px solid #2e3d4d;
                border-left: 3px solid #8b5cf6;
            }
        """)
        self.left_layout.addWidget(self.today_label)

        self.calendar = EnglishCalendarWidget()
        self.calendar.setFixedHeight(450)
        self.calendar.selectionChanged.connect(self.refresh)
        self.left_layout.addWidget(self.calendar)
        self.left_layout.addStretch()
        layout.addWidget(left_container)

        # right: task list + buttons
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)

        self.daily_header = QLabel()
        self.daily_header.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.daily_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.daily_header.setStyleSheet("""
            QLabel {
                background: #182029;
                color: #f59e0b;
                border-radius: 10px;
                padding: 8px;
                margin-bottom: 10px;
                border: 1px solid #2e3d4d;
                border-left: 3px solid #f59e0b;
                letter-spacing: 0.04em;
                text-transform: uppercase;
            }
        """)
        right_layout.addWidget(self.daily_header)

        self.list_tasks = QListWidget()
        self.list_tasks.itemDoubleClicked.connect(self.edit_task)
        self.list_tasks.itemChanged.connect(self.save_done_state)
        self.list_tasks.itemSelectionChanged.connect(self.update_button_states)
        self.list_tasks.setStyleSheet("""
            QListWidget {
                background: #182029;
                border-radius: 12px;
                border: 1px solid #2e3d4d;
                font-family: 'Cascadia Code', Consolas, monospace;
                font-size: 16px;
                padding: 6px;
                margin-bottom: 10px;
            }
        """)
        right_layout.addWidget(self.list_tasks)

        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)

        self.add_btn = QPushButton()
        self.add_btn.setIcon(make_icon("plus"))
        self.add_btn.setProperty("primary", True)
        self.add_btn.setMinimumHeight(40)
        self.add_btn.clicked.connect(self.add_task)
        btn_layout.addWidget(self.add_btn)

        self.edit_btn = QPushButton()
        self.edit_btn.setIcon(make_icon("edit"))
        self.edit_btn.setMinimumHeight(40)
        self.edit_btn.setEnabled(False)
        self.edit_btn.clicked.connect(self.edit_selected_task)
        btn_layout.addWidget(self.edit_btn)

        self.delete_btn = QPushButton()
        self.delete_btn.setIcon(make_icon("trash"))
        self.delete_btn.setProperty("danger", True)
        self.delete_btn.setMinimumHeight(40)
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self.delete_selected_task)
        btn_layout.addWidget(self.delete_btn)

        btn_layout.addStretch()
        right_layout.addWidget(btn_container)
        layout.addWidget(right_container)

        self.tabs.addTab(daily_tab, make_icon("list"), "")

    def _build_week_tab(self):
        week_tab = QWidget()
        vlayout = QVBoxLayout(week_tab)

        nav_layout = QHBoxLayout()
        self.prev_week_btn = QPushButton()
        self.prev_week_btn.setIcon(make_icon("chevron-left"))
        self.prev_week_btn.clicked.connect(lambda: self.change_week(-1))
        self.next_week_btn = QPushButton()
        self.next_week_btn.setIcon(make_icon("chevron-right"))
        self.next_week_btn.clicked.connect(lambda: self.change_week(1))
        nav_layout.addWidget(self.prev_week_btn)
        nav_layout.addWidget(self.next_week_btn)
        nav_layout.addStretch()
        vlayout.addLayout(nav_layout)

        self.week_layout = QGridLayout()
        self.week_layout.setSpacing(8)
        vlayout.addLayout(self.week_layout)

        self.current_week_start = self._current_week_start()
        self.tabs.addTab(week_tab, make_icon("calendar-range"), "")

    def _build_month_tab(self):
        month_tab = QWidget()
        vlayout = QVBoxLayout(month_tab)

        self.month_banner = QLabel()
        self.month_banner.setFont(QFont("Cascadia Code", 16, QFont.Weight.Bold))
        self.month_banner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.month_banner.setStyleSheet("""
            QLabel {
                background: #182029;
                color: #e8eef4;
                padding: 10px;
                border-radius: 12px;
                border: 1px solid #2e3d4d;
                border-left: 3px solid #8b5cf6;
                margin: 0px 10px 10px 10px;
            }
        """)
        vlayout.addWidget(self.month_banner)

        nav_layout = QHBoxLayout()
        self.prev_month_btn = QPushButton()
        self.prev_month_btn.setIcon(make_icon("chevron-left"))
        self.prev_month_btn.clicked.connect(lambda: self.change_month(-1))
        self.next_month_btn = QPushButton()
        self.next_month_btn.setIcon(make_icon("chevron-right"))
        self.next_month_btn.clicked.connect(lambda: self.change_month(1))
        nav_layout.addWidget(self.prev_month_btn)
        nav_layout.addWidget(self.next_month_btn)
        nav_layout.addStretch()
        vlayout.addLayout(nav_layout)

        self.month_layout = QGridLayout()
        vlayout.addLayout(self.month_layout)

        self.current_month = QDate.currentDate()
        self.current_persian_month = jdatetime.date.today()
        self.tabs.addTab(month_tab, make_icon("calendar-days"), "")

    def _build_tray(self):
        self.tray_icon = QSystemTrayIcon(make_app_icon(), self)
        self.tray_icon.setToolTip("Planner Pro")

        self.tray_menu = QMenu(self)
        self.tray_open_action = QAction(self)
        self.tray_open_action.triggered.connect(self.show_from_tray)
        self.tray_menu.addAction(self.tray_open_action)
        self.tray_quit_action = QAction(self)
        self.tray_quit_action.triggered.connect(self.quit_app)
        self.tray_menu.addAction(self.tray_quit_action)

        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    # ==================================================================
    # Language
    # ==================================================================
    def retranslate(self):
        """Apply the current language to every piece of static text."""
        self.setWindowTitle(tr("app_title"))
        self.tabs.setTabText(0, tr("tab_daily"))
        self.tabs.setTabText(1, tr("tab_weekly"))
        self.tabs.setTabText(2, tr("tab_monthly"))

        self.search_btn.setToolTip(tr("search_tooltip"))
        self.daily_header.setText(tr("daily_header"))
        self.add_btn.setText(" " + tr("btn_add"))
        self.edit_btn.setText(" " + tr("btn_edit"))
        self.delete_btn.setText(" " + tr("btn_delete"))

        self.prev_week_btn.setText(tr("prev_week"))
        self.next_week_btn.setText(tr("next_week"))
        self.prev_month_btn.setText(tr("prev_month"))
        self.next_month_btn.setText(tr("next_month"))

        self.tray_open_action.setText(tr("tray_open"))
        self.tray_quit_action.setText(tr("tray_quit"))

    def change_language(self, lang):
        language.set(lang)
        self.eng_btn.setChecked(language.is_english())
        self.per_btn.setChecked(language.is_persian())
        self.retranslate()
        self._replace_calendar()
        self.refresh()

    def _replace_calendar(self):
        old = self.calendar
        new = PersianCalendarWidget() if language.is_persian() else EnglishCalendarWidget()
        new.setFixedHeight(450)
        new.setSelectedDate(old.selectedDate())
        new.selectionChanged.connect(self.refresh)

        self.left_layout.replaceWidget(old, new)
        old.hide()
        old.deleteLater()
        self.calendar = new

    # ==================================================================
    # Dates
    # ==================================================================
    def selected_date(self):
        return self.calendar.selectedDate()

    def get_display_date(self, qdate):
        if language.is_persian():
            jdate = qdate_to_jdate(qdate)
            weekday = PERSIAN_WEEKDAYS[jdate.weekday()]
            return f"{weekday} {jdate.day} {PERSIAN_MONTHS[jdate.month - 1]} {jdate.year}"
        return qdate.toString("dddd, MMMM d, yyyy")

    def _weekday_name(self, index):
        if language.is_persian():
            return PERSIAN_WEEKDAYS[index]
        return ENGLISH_WEEKDAYS_SHORT[index]

    def _current_week_start(self):
        """First day of this week (Saturday in Persian, Monday in English)."""
        today = QDate.currentDate()
        if language.is_persian():
            return today.addDays(-qdate_to_jdate(today).weekday())
        return today.addDays(-today.dayOfWeek() + 1)

    # ==================================================================
    # Refreshing the views
    # ==================================================================
    def refresh(self):
        """Reload the daily list, then the weekly and monthly views."""
        self.current_week_start = self._current_week_start()
        self.daily_header.setText(tr("daily_header"))

        date = self.selected_date()
        self.today_label.setText(self.get_display_date(date))

        self.list_tasks.blockSignals(True)
        try:
            self.list_tasks.clear()
            for tid, title, done, start, end in self.db.tasks_on(date.toString(ISO_DATE)):
                item = QListWidgetItem(f"{start}-{end} — {title}")
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Checked if done else Qt.CheckState.Unchecked)
                item.setData(Qt.ItemDataRole.UserRole, tid)
                item.setFont(QFont("Cascadia Code", 15))
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
                self.list_tasks.addItem(item)
        finally:
            self.list_tasks.blockSignals(False)

        self.load_week()
        self.load_month()
        self.update_button_states()

    def update_button_states(self):
        has_selection = bool(self.list_tasks.selectedItems())
        self.edit_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)

    # ---- weekly view --------------------------------------------------
    def load_week(self):
        _clear_layout(self.week_layout)
        is_fa = language.is_persian()

        for col in range(7):
            day = self.current_week_start.addDays(col)

            if is_fa:
                display_text = f"{self._weekday_name(col)} {qdate_to_jdate(day).day:02d}"
                grid_col = 6 - col  # right-to-left
            else:
                display_text = day.toString("ddd dd")
                grid_col = col

            rows = self.db.tasks_on(day.toString(ISO_DATE))
            done_count = sum(1 for r in rows if r[2])
            total = len(rows)
            percent = int(done_count / total * 100) if total else 0
            edge = percent_color(percent).name() if total else "#2e3d4d"

            box = QGroupBox(display_text)
            box.setObjectName("weekBox")
            box.setStyleSheet(f"""
                QGroupBox#weekBox {{
                    background: #182029;
                    border:1px solid {edge};
                    border-radius:12px;
                    margin:8px 2px 2px 2px;
                    padding:6px;
                }}
            """)
            # equal-width columns that never push the window wider than the screen
            box.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)
            box.setMinimumWidth(0)
            self.week_layout.setColumnStretch(grid_col, 1)

            layout = QVBoxLayout(box)
            layout.setSpacing(6)
            layout.addWidget(self._make_week_task_list(rows, is_fa), 1)

            bar = QProgressBar()
            bar.setValue(percent)
            bar.setFormat(f"{percent}%")
            layout.addWidget(bar)

            self.week_layout.addWidget(box, 0, grid_col)

    def _make_week_task_list(self, rows, is_fa):
        """Scrollable column of task cards for one day."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background:#182029; border:none; }")
        scroll.viewport().setStyleSheet("background:#182029;")

        inner = QWidget()
        inner.setObjectName("weekInner")
        inner.setStyleSheet("#weekInner { background:#182029; }")
        inner_layout = QVBoxLayout(inner)
        inner_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout.setSpacing(6)

        for _tid, title, done, start, end in rows:
            inner_layout.addWidget(self._make_week_card(title, done, start, end, is_fa))

        inner_layout.addStretch()
        scroll.setWidget(inner)
        return scroll

    def _make_week_card(self, title, done, start, end, is_fa):
        card = QFrame()
        card.setObjectName("weekCard")
        card.setStyleSheet(
            "#weekCard { background:#22303c; border:1px solid #2e3d4d; border-radius:8px; }"
            "QLabel { background:transparent; border:none; }"
        )
        if is_fa:
            card.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(6, 5, 6, 5)
        layout.setSpacing(6)

        icon_lbl = QLabel()
        icon_lbl.setFixedSize(14, 14)
        icon_lbl.setPixmap(make_icon(
            "check-circle" if done else "circle",
            color="#34d399" if done else "#8fa0b2", size=14,
        ).pixmap(14, 14))
        layout.addWidget(icon_lbl, 0, Qt.AlignmentFlag.AlignTop)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)

        time_lbl = QLabel(f"{start} – {end}")
        time_lbl.setFont(QFont("Cascadia Code", 8))
        time_lbl.setStyleSheet("color:#8fa0b2;")
        text_col.addWidget(time_lbl)

        title_lbl = QLabel(title)
        title_lbl.setWordWrap(True)
        title_font = QFont("Segoe UI", 10)
        title_font.setStrikeOut(bool(done))
        title_lbl.setFont(title_font)
        title_lbl.setStyleSheet("color:#8fa0b2;" if done else "color:#e8eef4;")
        text_col.addWidget(title_lbl)

        layout.addLayout(text_col, 1)
        return card

    def change_week(self, offset):
        self.current_week_start = self.current_week_start.addDays(7 * offset)
        self.load_week()

    # ---- monthly view -------------------------------------------------
    def load_month(self):
        _clear_layout(self.month_layout)

        if language.is_persian():
            year = self.current_persian_month.year
            month = self.current_persian_month.month
            self.month_banner.setText(f"{PERSIAN_MONTHS[month - 1]} {year}")
            days = [
                (i, jdate_to_qdate(jdatetime.date(year, month, i)))
                for i in range(1, jalali_days_in_month(year, month) + 1)
            ]
        else:
            year, month = self.current_month.year(), self.current_month.month()
            self.month_banner.setText(self.current_month.toString("MMMM yyyy"))
            days = [
                (i, QDate(year, month, i))
                for i in range(1, QDate(year, month, 1).daysInMonth() + 1)
            ]

        for index, (number, qdate) in enumerate(days):
            done, total = self.db.day_stats(qdate.toString(ISO_DATE))
            self.month_layout.addWidget(
                self._make_month_box(f"{number:02d}", done, total),
                index // 7, index % 7,
            )

    @staticmethod
    def _make_month_box(label, done, total):
        percent = int(done / total * 100) if total else 0
        border = percent_color(percent).name() if total else "#2e3d4d"

        box = QGroupBox(label)
        box.setStyleSheet(f"""
            QGroupBox {{
                background: #182029;
                border:1px solid {border};
                border-radius:12px;
                padding:6px;
            }}
        """)
        layout = QVBoxLayout(box)

        summary = QLabel(f"{done}/{total}" if total else "")
        summary.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if total:
            summary.setFont(QFont("Cascadia Code", 11, QFont.Weight.Bold))
            summary.setStyleSheet("color:#e8eef4;border:none;background:transparent;")
        else:
            summary.setFixedHeight(18)
            summary.setStyleSheet("background:transparent; border:none;")
        layout.addWidget(summary)

        percent_lbl = QLabel(f"{percent}%")
        percent_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        percent_lbl.setFont(QFont("Cascadia Code", 10))
        percent_lbl.setStyleSheet(
            "color:#8fa0b2;font-weight:bold;border:none;background:transparent;"
        )
        layout.addWidget(percent_lbl)
        return box

    def change_month(self, offset):
        if language.is_persian():
            year, month = shift_month(
                self.current_persian_month.year,
                self.current_persian_month.month,
                offset,
            )
            self.current_persian_month = jdatetime.date(year, month, 1)
        else:
            self.current_month = self.current_month.addMonths(offset)
        self.load_month()

    # ==================================================================
    # Task actions
    # ==================================================================
    def save_done_state(self, item):
        tid = item.data(Qt.ItemDataRole.UserRole)
        self.db.set_done(tid, item.checkState() == Qt.CheckState.Checked)
        self.load_week()
        self.load_month()

    def add_task(self):
        dlg = TaskDialog(parent=self)
        if dlg.exec():
            title, start, end = dlg.get_data()
            if title:
                self.db.add_task(self.selected_date().toString(ISO_DATE), title, start, end)
                self.refresh()

    def edit_task(self, item):
        tid = item.data(Qt.ItemDataRole.UserRole)
        row = self.db.get_task(tid)
        if not row:
            return
        dlg = TaskDialog(row[0], row[1], row[2], editing=True, parent=self)
        if dlg.exec():
            title, start, end = dlg.get_data()
            if title:
                self.db.update_task(tid, title, start, end)
                self.refresh()

    def edit_selected_task(self):
        items = self.list_tasks.selectedItems()
        if items:
            self.edit_task(items[0])

    def delete_selected_task(self):
        items = self.list_tasks.selectedItems()
        if not items:
            return
        reply = QMessageBox.question(
            self, tr("confirm_delete_title"), tr("confirm_delete_text"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_task(items[0].data(Qt.ItemDataRole.UserRole))
            self.refresh()

    def open_search_dialog(self):
        SearchDialog(self.db, self.jump_to_date, parent=self).exec()

    def jump_to_date(self, qdate):
        self.calendar.setSelectedDate(qdate)
        self.tabs.setCurrentIndex(0)
        self.refresh()

    # ==================================================================
    # Reminders and tray
    # ==================================================================
    def _start_reminder_timer(self):
        self.reminder_timer = QTimer(self)
        self.reminder_timer.setInterval(REMINDER_INTERVAL_MS)
        self.reminder_timer.timeout.connect(self.check_reminders)
        self.reminder_timer.start()
        QTimer.singleShot(2000, self.check_reminders)  # once shortly after start

    def check_reminders(self):
        """Fire a reminder for today's unfinished tasks whose start time has come."""
        try:
            now = QTime.currentTime()
            today = QDate.currentDate().toString(ISO_DATE)
            for tid, title, start_time in self.db.pending_reminders(today):
                start = QTime.fromString(start_time, "HH:mm")
                if start.isValid() and now >= start:
                    self._fire_reminder(title, start_time)
                    self.db.mark_notified(tid)
        except Exception:
            logger.exception("Error while checking reminders")

    def _fire_reminder(self, title, start_time):
        header = tr("reminder_title")
        body = f"{start_time} — {title}"
        if not notify(header, body):
            self.tray_icon.showMessage(
                header, body, QSystemTrayIcon.MessageIcon.Information, 8000
            )

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_from_tray()

    def show_from_tray(self):
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def quit_app(self):
        self._really_quit = True
        QApplication.instance().quit()

    def closeEvent(self, event):
        # Closing the window hides it to the tray so reminders keep working.
        if self._really_quit:
            event.accept()
            return
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Planner Pro", tr("tray_background"),
            QSystemTrayIcon.MessageIcon.Information, 4000,
        )
