"""Sound and desktop notifications for task reminders."""
import logging
import os

logger = logging.getLogger(__name__)

try:
    from winotify import Notification, audio

    HAS_WINOTIFY = True
except Exception:  # not installed / not Windows
    HAS_WINOTIFY = False

try:
    import winsound

    HAS_WINSOUND = True
except Exception:  # not Windows
    HAS_WINSOUND = False


def play_alarm():
    """Two short beeps (Windows only; silently skipped elsewhere)."""
    if not HAS_WINSOUND:
        return
    try:
        winsound.Beep(1000, 300)
        winsound.Beep(1300, 300)
    except Exception:
        logger.exception("Could not play alarm sound")


def show_toast(title, body, app_id="Planner Pro"):
    """Show a native Windows toast. Returns True if it was shown."""
    if not (HAS_WINOTIFY and os.name == "nt"):
        return False
    try:
        toast = Notification(app_id=app_id, title=title, msg=body, duration="short")
        try:
            toast.set_audio(audio.Reminder, loop=False)
        except Exception:
            pass
        toast.show()
        return True
    except Exception:
        logger.exception("Could not show Windows toast")
        return False


def notify(title, body):
    """Play the alarm and try a native toast.

    Returns True if a native toast was shown, otherwise the caller should
    fall back to another mechanism (e.g. the tray icon balloon).
    """
    play_alarm()
    return show_toast(title, body)
