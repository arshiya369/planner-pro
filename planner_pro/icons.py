"""Icons drawn with QPainter, so the app needs no image assets."""
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap

_ICON_CACHE = {}


def _make_pen(color, width):
    pen = QPen(QColor(color))
    pen.setWidthF(width)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    return pen


def _draw_calendar_frame(p, s, m):
    p.drawRoundedRect(QRectF(m * 0.7, m * 1.4, s - m * 1.4, s - m * 2.1), 3, 3)
    p.drawLine(QPointF(m * 0.7, s * 0.46), QPointF(s - m * 0.7, s * 0.46))


def make_icon(kind, color="#e8eef4", size=22, stroke=2.2):
    """Return a cached QIcon for one of the built-in shapes."""
    cache_key = (kind, color, size, stroke)
    if cache_key in _ICON_CACHE:
        return _ICON_CACHE[cache_key]

    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(_make_pen(color, stroke))
    p.setBrush(Qt.BrushStyle.NoBrush)

    s = size
    m = s * 0.2

    if kind == "plus":
        p.drawLine(QPointF(s / 2, m), QPointF(s / 2, s - m))
        p.drawLine(QPointF(m, s / 2), QPointF(s - m, s / 2))
    elif kind == "edit":
        p.drawLine(QPointF(m, s - m), QPointF(s - m, m))
        p.drawLine(QPointF(s - m * 1.6, m * 0.75), QPointF(s - m * 0.75, m * 1.6))
    elif kind == "trash":
        p.drawLine(QPointF(m * 0.8, m * 1.5), QPointF(s - m * 0.8, m * 1.5))
        p.drawRoundedRect(QRectF(m * 1.2, m * 1.5, s - m * 2.4, s - m * 2.3), 2, 2)
        p.drawLine(QPointF(s * 0.4, m), QPointF(s * 0.6, m))
        p.drawLine(QPointF(s * 0.4, m * 2.1), QPointF(s * 0.4, s - m * 1.3))
        p.drawLine(QPointF(s * 0.6, m * 2.1), QPointF(s * 0.6, s - m * 1.3))
    elif kind == "chevron-left":
        p.drawLine(QPointF(s * 0.6, m), QPointF(s * 0.35, s / 2))
        p.drawLine(QPointF(s * 0.35, s / 2), QPointF(s * 0.6, s - m))
    elif kind == "chevron-right":
        p.drawLine(QPointF(s * 0.4, m), QPointF(s * 0.65, s / 2))
        p.drawLine(QPointF(s * 0.65, s / 2), QPointF(s * 0.4, s - m))
    elif kind == "calendar-range":
        _draw_calendar_frame(p, s, m)
        p.drawLine(QPointF(s * 0.35, s * 0.65), QPointF(s * 0.65, s * 0.65))
    elif kind == "calendar-days":
        _draw_calendar_frame(p, s, m)
        for dx in (0.36, 0.5, 0.64):
            p.drawPoint(QPointF(s * dx, s * 0.68))
    elif kind == "check-circle":
        p.drawEllipse(QRectF(m * 0.5, m * 0.5, s - m, s - m))
        p.drawLine(QPointF(s * 0.32, s * 0.52), QPointF(s * 0.45, s * 0.66))
        p.drawLine(QPointF(s * 0.45, s * 0.66), QPointF(s * 0.7, s * 0.36))
    elif kind == "circle":
        p.drawEllipse(QRectF(m * 0.5, m * 0.5, s - m, s - m))
    elif kind == "list":
        for y in (0.32, 0.52, 0.72):
            p.drawLine(QPointF(m * 0.6, s * y), QPointF(s - m * 0.6, s * y))
    elif kind == "search":
        circle_rect = QRectF(m * 0.5, m * 0.5, s * 0.55, s * 0.55)
        p.drawEllipse(circle_rect)
        handle_start = QPointF(circle_rect.right() - s * 0.05,
                               circle_rect.bottom() - s * 0.05)
        p.drawLine(handle_start, QPointF(s - m * 0.4, s - m * 0.4))
    elif kind == "globe":
        p.drawEllipse(QRectF(m * 0.5, m * 0.5, s - m, s - m))
        p.drawLine(QPointF(s / 2, m * 0.5), QPointF(s / 2, s - m * 0.5))
        p.setPen(_make_pen(color, stroke * 0.85))
        p.drawLine(QPointF(m * 0.65, s * 0.38), QPointF(s - m * 0.65, s * 0.38))
        p.drawLine(QPointF(m * 0.65, s * 0.62), QPointF(s - m * 0.65, s * 0.62))
    else:
        p.end()
        raise ValueError(f"Unknown icon kind: {kind!r}")

    p.end()
    icon = QIcon(pix)
    _ICON_CACHE[cache_key] = icon
    return icon


def make_app_icon(size=64):
    """Application icon: a calendar with a check mark."""
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(_make_pen("#8b5cf6", 3.5))
    p.setBrush(Qt.BrushStyle.NoBrush)

    m = size * 0.18
    p.drawRoundedRect(QRectF(m * 0.8, m * 1.6, size - m * 1.6, size - m * 2.3), 6, 6)
    p.drawLine(QPointF(m * 0.8, size * 0.42), QPointF(size - m * 0.8, size * 0.42))
    p.drawLine(QPointF(size * 0.34, m * 0.5), QPointF(size * 0.34, m * 1.8))
    p.drawLine(QPointF(size * 0.66, m * 0.5), QPointF(size * 0.66, m * 1.8))

    p.setPen(_make_pen("#2dd4bf", 4))
    tick_x = size * 0.5
    tick_y = size * 0.62
    p.drawLine(QPointF(tick_x - size * 0.1, tick_y),
               QPointF(tick_x - size * 0.02, tick_y + size * 0.1))
    p.drawLine(QPointF(tick_x - size * 0.02, tick_y + size * 0.1),
               QPointF(tick_x + size * 0.12, tick_y - size * 0.08))

    p.end()
    return QIcon(pix)
