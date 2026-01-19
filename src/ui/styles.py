DARK_THEME = """
QMainWindow, QWidget {
    background-color: #1e1e1e;
    color: #f0f0f0;
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
}
QLabel {
    color: #ffffff;
}
QLabel#dashboardHeader {
    font-size: 26px;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 5px;
}
QLabel#sectionHeader {
    font-size: 16px;
    font-weight: 600;
    color: #bbbbbb;
    margin-bottom: 2px;
}
QPushButton {
    background-color: #333333;
    color: #ffffff;
    border: 1px solid #444444;
    border-radius: 8px;
    padding: 10px 18px;
    font-size: 14px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #404040;
    border-color: #555555;
}
QPushButton:pressed {
    background-color: #2a2a2a;
}
QPushButton#primaryInfo {
    background-color: #0078D4;
    border: none;
}
QPushButton#primaryInfo:hover {
    background-color: #0086ee;
}
QPushButton#primarySuccess {
    background-color: #107c10;
    border: none;
}
QPushButton#primarySuccess:hover {
    background-color: #1a961a;
}
QPushButton#importantError {
    background-color: #d83b01;
    border: none;
}
QPushButton#importantError:hover {
    background-color: #f14402;
}
QGroupBox {
    font-weight: bold;
    border: 1px solid #333333;
    border-radius: 8px;
    margin-top: 15px;
    padding-top: 15px;
    color: #ffffff;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 5px;
    color: #888888;
}
QCheckBox {
    spacing: 8px;
    color: #dddddd;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #555555;
    border-radius: 4px;
    background: #333333;
}
QCheckBox::indicator:unchecked {
    background-color: #333333;
    border: 1px solid #555555;
}
QCheckBox::indicator:checked {
    background-color: #0078D4;
    border-color: #0078D4;
}
/* Ensure text in colored buttons is always white */
QPushButton#primaryInfo, QPushButton#primarySuccess, QPushButton#importantError {
    color: #ffffff !important;
}
QListWidget {
    background-color: #252525;
    border: 1px solid #333333;
    border-radius: 6px;
    color: #cccccc;
    padding: 5px;
}
QListWidget::item {
    padding: 10px;
    border-bottom: 1px solid #333333;
}
QListWidget::item:selected {
    background-color: #2d2d2d;
    color: #0078D4;
    font-weight: bold;
}
QTabWidget::pane {
    border: 1px solid #333333;
    background-color: #1e1e1e;
    top: -1px;
}
QTabBar::tab {
    background-color: #252525;
    color: #888888;
    padding: 12px 24px;
    border: 1px solid #333333;
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 4px;
    font-weight: 500;
}
QTabBar::tab:selected {
    background-color: #1e1e1e;
    color: #ffffff;
    border-bottom: 3px solid #0078D4;
    font-weight: bold;
}
QTabBar::tab:hover:!selected {
    background-color: #2d2d2d;
    color: #ffffff;
}
QToolBar {
    background-color: #252525;
    border-bottom: 1px solid #333333;
    spacing: 8px;
    padding: 6px;
}
QToolButton {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 6px;
    color: #ffffff;
}
QToolButton:hover {
    background-color: #333333;
    border-color: #444444;
}
QToolButton:checked {
    background-color: #3d3d3d;
    border-color: #0078D4;
}
QSlider::groove:horizontal {
    border: 1px solid #333333;
    height: 6px;
    background: #252525;
    margin: 2px 0;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #0078D4;
    border: 1px solid #0078D4;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}
QSlider::handle:horizontal:hover {
    background: #0086ee;
}
QProgressBar {
    border: 1px solid #333333;
    border-radius: 5px;
    text-align: center;
    background-color: #252525;
}
QProgressBar::chunk {
    background-color: #0078D4;
    border-radius: 4px;
}
QWidget#recordingControls {
    background-color: #1e1e1ec0; /* Translucent */
    border: 1px solid #444444;
    border-radius: 12px;
}
QLabel#timerLabel {
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 18px;
    font-weight: bold;
    color: #0078D4;
}
"""


