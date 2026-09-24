"""Application-wide Qt style sheet (dark theme)."""

APP_STYLESHEET = """
QWidget{
    background:#0e1318;
    color:#e8eef4;
    font-size:14px;
    font-family: 'Segoe UI', Arial, sans-serif;
}
QPushButton{
    background: #22303c;
    color:#e8eef4;
    padding:8px 14px;
    border-radius:8px;
    font-weight:600;
    border:1px solid #2e3d4d;
}
QPushButton:hover{
    background: #2a3a4a;
    border-color:#8fa0b2;
}
QPushButton:disabled {
    background: #182029;
    color: #4a5a68;
    border-color:#22303c;
}
QPushButton:checked {
    background: #8b5cf6;
    color:#0e1318;
    border: 1px solid #a684ff;
}
QPushButton[primary="true"] {
    background: #3a2d63;
    border: 1px solid #8b5cf6;
    color: #e8eef4;
}
QPushButton[primary="true"]:hover {
    background: #47387a;
}
QPushButton[danger="true"] {
    border: 1px solid #f87171;
    color: #ffd3d3;
}
QPushButton[danger="true"]:hover {
    background: #3a2222;
}
QListWidget{
    background:#182029;
    border-radius:12px;
    border:1px solid #2e3d4d;
    font-family: 'Cascadia Code', Consolas, monospace;
    font-size:16px;
    padding:6px;
}
QListWidget::item{
    border-radius:8px;
    padding:12px 8px;
    margin:4px 0;
    background: #22303c;
    border: 1px solid #2e3d4d;
}
QListWidget::item:selected{
    background:#2a3a4a;
    border: 1px solid #8b5cf6;
}
QListWidget::indicator{
    width:22px;
    height:22px;
}
QListWidget::indicator:unchecked {
    border:2px solid #2e3d4d;
    border-radius:5px;
    background:#0e1318;
}
QListWidget::indicator:checked {
    border:2px solid #34d399;
    border-radius:5px;
    background:#34d399;
}
QGroupBox{
    border:1px solid #2e3d4d;
    border-radius:12px;
    margin:5px;
    padding:8px;
    background-color:#182029;
    font-family: 'Cascadia Code', Consolas, monospace;
}
QGroupBox::title {
    color: #8fa0b2;
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 4px;
}
QLabel{
    font-size:14px;
}
QProgressBar{
    height:16px;
    border-radius:6px;
    text-align:center;
    background:#0e1318;
    border:1px solid #2e3d4d;
    color: #e8eef4;
    font-size: 11px;
}
QProgressBar::chunk{
    background: #2dd4bf;
    border-radius:6px;
}
QTimeEdit, QLineEdit{
    background:#182029;
    color:#e8eef4;
    padding:6px;
    border-radius:8px;
    border:1px solid #2e3d4d;
    font-family: 'Cascadia Code', Consolas, monospace;
}
QTimeEdit:focus, QLineEdit:focus {
    border: 1px solid #60a5fa;
}
QTabWidget::pane {
    border: 1px solid #2e3d4d;
    border-radius: 12px;
    background: #0e1318;
}
QTabBar::tab {
    background: transparent;
    color: #8fa0b2;
    padding: 10px 20px;
    margin: 5px;
    border-radius: 8px;
    border: 1px solid transparent;
}
QTabBar::tab:selected {
    background: #22303c;
    color: #e8eef4;
    border: 1px solid #8b5cf6;
}
QTabBar::tab:hover {
    background: #182029;
}
QScrollBar:vertical {
    background: #0e1318;
    width: 10px;
}
QScrollBar::handle:vertical {
    background: #2e3d4d;
    border-radius: 5px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover {
    background: #3a4d5f;
}
QMessageBox {
    background: #0e1318;
}
"""
