# Planner Pro

A dark-themed desktop planner for **Windows** with a full **English / Persian (فارسی)** interface,
a **Jalali (Shamsi) calendar**, daily / weekly / monthly views and task reminders.

<!-- Add a screenshot of your own (with no personal tasks in it):
![Weekly view](docs/weekly.png)
-->

## Features

- **Daily view** – calendar + checklist of the day's tasks, add / edit / delete with start and end times
- **Weekly view** – seven day columns with task cards and a progress bar per day
- **Monthly view** – one box per day, colour-coded from red to green by completion
- **English and Persian** – switch at any time; the Persian mode uses the Jalali calendar, a Saturday-first week and right-to-left layout
- **Reminders** – Windows toast notification and a sound when a task's start time arrives
- **Runs in the tray** – closing the window keeps reminders alive; use *Quit* in the tray menu to exit
- **Search** – find a task by title and jump straight to its day
- Data is stored locally in a SQLite database – no account, no network

## Installation

Requires Python 3.9+.

```bash
git clone https://github.com/arshiya369/planner-pro.git
cd planner-pro
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

## Run

```bash
python -m planner_pro
```

Your tasks are stored in `%APPDATA%\PlannerPro\planner.db`
(`~/.planner_pro/planner.db` on Linux/macOS). Set the `PLANNER_PRO_DB` environment variable
to use a different file.

## Build a standalone .exe

```bash
pip install -r requirements-dev.txt
pyinstaller --noconsole --name PlannerPro run.py
```

The finished program is in `dist/PlannerPro/`. Zip that folder to share it.

## Development

```bash
pip install -r requirements-dev.txt
python -m pytest
```

Project layout:

```
planner_pro/
├── app.py                # entry point
├── window.py             # main window: daily / weekly / monthly views, tray, reminders
├── calendar_widgets.py   # Gregorian and Jalali month-grid calendars
├── dialogs.py            # add/edit task dialog, search dialog
├── db.py                 # SQLite storage (Database class)
├── i18n.py               # language state and all UI strings
├── jalali.py             # Jalali date helpers
├── notifications.py      # sound + Windows toast
├── icons.py              # icons drawn in code
└── styles.py             # dark theme stylesheet
tests/                    # database, date helper and headless UI tests
```

## Notes

- Notifications and the alarm sound are Windows-only; on other systems the app falls back to a tray message.
- Built with [PyQt6](https://pypi.org/project/PyQt6/) (GPL v3 / commercial licence) – keep that in mind if you plan to distribute closed-source builds.

## License

[MIT](LICENSE) for this project's source code.
