"""Current UI language and all translated strings."""


class Language:
    ENGLISH = "english"
    PERSIAN = "persian"

    def __init__(self):
        self.current = self.ENGLISH

    def set(self, lang):
        if lang not in (self.ENGLISH, self.PERSIAN):
            raise ValueError(f"Unknown language: {lang!r}")
        self.current = lang

    def is_persian(self):
        return self.current == self.PERSIAN

    def is_english(self):
        return self.current == self.ENGLISH


# Shared, application-wide language state.
language = Language()

# key: (English, Persian)
STRINGS = {
    "app_title": ("Planner Pro", "برنامه‌ریز حرفه‌ای"),
    "tab_daily": ("Daily", "روزانه"),
    "tab_weekly": ("Weekly", "هفتگی"),
    "tab_monthly": ("Monthly", "ماهانه"),
    "btn_add": ("Add", "افزودن"),
    "btn_edit": ("Edit", "ویرایش"),
    "btn_delete": ("Delete", "حذف"),
    "prev_week": ("Previous Week", "هفته قبل"),
    "next_week": ("Next Week", "هفته بعد"),
    "prev_month": ("Previous Month", "ماه قبل"),
    "next_month": ("Next Month", "ماه بعد"),
    "search_tooltip": ("Search tasks", "جستجوی فعالیت‌ها"),
    "daily_header": ("Daily Tasks", "فعالیت‌های روزانه"),
    "tray_open": ("Open", "باز کردن"),
    "tray_quit": ("Quit", "خروج کامل"),
    "tray_background": (
        "Planner Pro is still running in the background",
        "برنامه در پس‌زمینه (کنار ساعت) در حال اجراست",
    ),
    "reminder_title": ("Task Reminder", "یادآوری فعالیت"),
    "add_dialog_title": ("Add New Task", "افزودن فعالیت جدید"),
    "edit_dialog_title": ("Edit Task", "ویرایش فعالیت"),
    "field_title": ("Task Title:", "عنوان فعالیت:"),
    "field_start": ("Start Time:", "زمان شروع:"),
    "field_end": ("End Time:", "زمان پایان:"),
    "btn_save": ("Save Task", "ثبت فعالیت"),
    "search_dialog_title": ("Search Tasks", "جستجوی فعالیت‌ها"),
    "search_placeholder": (
        "Type part of a task title...",
        "بخشی از عنوان فعالیت را وارد کنید...",
    ),
    "search_hint": (
        "Double-click a result to jump to that day",
        "برای رفتن به آن روز، دوبار کلیک کنید",
    ),
    "search_empty": ("No matches found", "چیزی پیدا نشد"),
    "confirm_delete_title": ("Confirm Delete", "تایید حذف"),
    "confirm_delete_text": (
        "Are you sure you want to delete this task?",
        "آیا از حذف این فعالیت اطمینان دارید؟",
    ),
}

ENGLISH_WEEKDAYS_SHORT = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
ENGLISH_MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


def tr(key):
    """Translate `key` into the current language."""
    english, persian = STRINGS[key]
    return persian if language.is_persian() else english
