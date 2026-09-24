"""Convenience launcher (also the entry script for PyInstaller)."""
import sys

from planner_pro.app import main

if __name__ == "__main__":
    sys.exit(main())
