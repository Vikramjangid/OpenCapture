from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, 
                               QLabel, QHBoxLayout, QListWidget, QSystemTrayIcon, QMenu, QStyle, QApplication)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QAction
import sys

class Dashboard(QMainWindow):
    # ... (init methods omitted for brevity in tool call, will target specific lines)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Snagit Clone By - Vikram Jangid")
        self.resize(400, 500)
        self.init_ui()
        self.init_tray()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header = QLabel("Snagit Clone")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        layout.addWidget(header, alignment=Qt.AlignCenter)


        # Capture Region Button
        self.btn_capture = QPushButton("Capture Region")
        self.btn_capture.setObjectName("primaryInfo") # For styling
        self.btn_capture.setFixedHeight(50)
        self.btn_capture.clicked.connect(self.start_capture)
        layout.addWidget(self.btn_capture)

        # Capture Full Screen Button
        self.btn_full_capture = QPushButton("Capture Full Screen")
        self.btn_full_capture.setObjectName("primarySuccess") # For styling
        self.btn_full_capture.setFixedHeight(50)
        self.btn_full_capture.clicked.connect(self.start_full_capture)
        layout.addWidget(self.btn_full_capture)

        # Help / FAQ Button
        self.btn_help = QPushButton("Quick Start Guide / FAQ")
        self.btn_help.setFixedHeight(40)
        self.btn_help.clicked.connect(self.show_help)
        layout.addWidget(self.btn_help)

        # Recent Captures Label
        recent_label = QLabel("Recent Captures")
        recent_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 10px; color: #aaa;")
        layout.addWidget(recent_label)

        # List for recent files
        self.recent_list = QListWidget()
        layout.addWidget(self.recent_list)
        
        self.load_recent_captures()

    def show_help(self):
        from ui.help_dialog import HelpDialog
        from utils.help_text import FAQ_TEXT
        dlg = HelpDialog("Quick Start Guide", FAQ_TEXT, self)
        dlg.exec()

    def load_recent_captures(self):
        from utils.history import HistoryManager
        import os
        self.recent_list.clear()
        hm = HistoryManager()
        for path in hm.get_recent():
            if os.path.exists(path):
                self.recent_list.addItem(path)

    def init_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        from PySide6.QtWidgets import QStyle
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        
        menu = QMenu()

        capture_action = QAction("Capture", self)
        capture_action.triggered.connect(self.start_capture)
        menu.addAction(capture_action)
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

    def showEvent(self, event):
        self.load_recent_captures()
        super().showEvent(event)

    def start_capture(self):
        self.hide() # Hide dashboard
        # Use a slight delay or just proceed? PySide usually handles hiding quickly.
        QApplication.processEvents()
        
        # Open Overlay
        from capture.region import RegionSelectionOverlay
        self.overlay = RegionSelectionOverlay()
        self.overlay.selection_made.connect(self.on_selection_made)
        self.overlay.show()

    def start_full_capture(self):
        from capture.engine import CaptureEngine
        from editor.window import EditorWindow
        import time
        from PySide6.QtWidgets import QApplication, QMessageBox

        self.hide()
        QApplication.processEvents()
        time.sleep(0.2) # Wait for dashboard to hide
        QApplication.processEvents()

        try:
            engine = CaptureEngine()
            img = engine.capture_fullscreen()
            
            self.editor = EditorWindow(img)
            self.editor.show()
        except Exception as e:
            QMessageBox.critical(self, "Capture Failed", f"An error occurred:\n{str(e)}")
        
        self.show()
        
    def on_selection_made(self, x, y, w, h):
        from capture.engine import CaptureEngine
        from editor.window import EditorWindow
        import time
        from PySide6.QtWidgets import QApplication, QMessageBox
        
        # Ensure overlay is fully closed and screen repainted
        # Force overlay to close if it hasn't already (though it should have in mouseRelease)
        if hasattr(self, 'overlay') and self.overlay.isVisible():
            self.overlay.close()
            
        QApplication.processEvents()
        time.sleep(0.2) # Increased buffer for compositor (0.1 was borderline)
        QApplication.processEvents()
        
        try:
            if w <= 0 or h <= 0:
                print("Skipping invalid capture dimensions")
                return
            
            # Handle DPI Scaling (Logical vs Physical pixels)
            screen = QApplication.primaryScreen()
            dpr = screen.devicePixelRatio()
            
            # Scale coordinates
            x = int(x * dpr)
            y = int(y * dpr)
            w = int(w * dpr)
            h = int(h * dpr)

            # Capture
            engine = CaptureEngine()
            img = engine.capture_region(x, y, w, h)
            
            # Open Editor
            self.editor = EditorWindow(img)
            self.editor.show()
        except Exception as e:
            QMessageBox.critical(self, "Capture Failed", f"An error occurred during capture:\n{str(e)}")
            print(f"Capture Error: {e}")
        
        # Show dashboard again or keep hidden? Snagit keeps dashboard open usually but minimized.
        self.show()
