
DARK_THEME = """
QMainWindow {
    background-color: #2b2b2b;
    color: #ffffff;
}
QWidget {
    background-color: #2b2b2b;
    color: #ffffff;
    font-family: 'Segoe UI', Arial, sans-serif;
}
QLabel {
    color: #e0e0e0;
}
QPushButton {
    background-color: #3c3c3c;
    color: #ffffff;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 8px 16px;
    font-size: 14px;
}
QPushButton:hover {
    background-color: #505050;
    border-color: #666666;
}
QPushButton:pressed {
    background-color: #252525;
}
/* Specific Button Colors override */
QPushButton#primaryInfo {
    background-color: #0078D7;
    border: none;
}
QPushButton#primaryInfo:hover {
    background-color: #1084E3;
}
QPushButton#primarySuccess {
    background-color: #28a745;
    border: none;
}
QPushButton#primarySuccess:hover {
    background-color: #34c759;
}

QListWidget {
    background-color: #333333;
    border: 1px solid #444444;
    border-radius: 4px;
    color: #dddddd;
    padding: 5px;
}
QListWidget::item {
    padding: 8px;
    border-bottom: 1px solid #3a3a3a;
}
QListWidget::item:selected {
    background-color: #0078D7;
    color: white;
}
QToolBar {
    background-color: #333333;
    border-bottom: 1px solid #444444;
    spacing: 10px;
    padding: 5px;
}
QToolButton {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 3px;
    padding: 4px;
    color: #ffffff;
}
QToolButton:hover {
    background-color: #444444;
    border: 1px solid #555555;
}
QMenuBar {
    background-color: #2b2b2b;
    color: white;
}
QMenuBar::item:selected {
    background-color: #444444;
}
QMenu {
    background-color: #333333;
    color: white;
    border: 1px solid #555555;
}
QMenu::item:selected {
    background-color: #0078D7;
}
"""
