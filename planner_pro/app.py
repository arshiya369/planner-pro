"""Application entry point."""
import logging
import sys

from PyQt6.QtWidgets import QApplication

from .db import Database
from .window import PlannerWindow


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    app = QApplication(sys.argv)
    app.setApplicationName("Planner Pro")
    # Keep running in the system tray when the window is closed.
    app.setQuitOnLastWindowClosed(False)

    db = Database()
    app.aboutToQuit.connect(db.close)

    window = PlannerWindow(db)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
