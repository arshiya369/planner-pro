import os

# Run Qt without a display (CI / headless machines).
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
