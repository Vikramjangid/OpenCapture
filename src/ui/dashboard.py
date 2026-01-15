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

        # Dynamic Full Screen Buttons
        from PySide6.QtGui import QGuiApplication
        screens = QGuiApplication.screens()
        for i, screen in enumerate(screens):
            btn = QPushButton(f"Capture {screen.name()}")
            btn.setObjectName("primarySuccess")
            btn.setFixedHeight(50)
            btn.clicked.connect(lambda checked=False, idx=i: self.start_full_capture(idx))
            layout.addWidget(btn)
        
        # All screens capture
        if len(screens) > 1:
            btn_all = QPushButton("Capture All Screens")
            btn_all.setObjectName("primarySuccess")
            btn_all.setFixedHeight(50)
            btn_all.clicked.connect(lambda checked=False: self.start_full_capture(None))
            layout.addWidget(btn_all)

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
        QApplication.processEvents()
        
        # Open Overlay for each screen
        from capture.region import RegionSelectionOverlay
        from PySide6.QtGui import QGuiApplication
        
        self.overlays = []
        for screen in QGuiApplication.screens():
            overlay = RegionSelectionOverlay(screen)
            overlay.selection_made.connect(self.on_selection_made)
            overlay.selection_updated.connect(self.on_selection_updated)
            overlay.canceled.connect(self.on_capture_canceled)
            overlay.show()
            self.overlays.append(overlay)

    def on_selection_updated(self, rect):
        for overlay in self.overlays:
            if overlay != self.sender():
                overlay.sync_selection(rect, True)

    def on_capture_canceled(self):
        if hasattr(self, 'overlays'):
            for overlay in self.overlays:
                overlay.close()
            self.overlays = []
        self.show()

    def start_full_capture(self, monitor_index=None):
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
            img = engine.capture_fullscreen(monitor_index)
            
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
        
        # Ensure ALL overlays are closed
        if hasattr(self, 'overlays'):
            for overlay in self.overlays:
                overlay.close()
            self.overlays = []
            
        QApplication.processEvents()
        time.sleep(0.2) # Increased buffer for compositor (0.1 was borderline)
        QApplication.processEvents()
        
        try:
            if w <= 0 or h <= 0:
                print("Skipping invalid capture dimensions")
                return
            
            # On macOS, MSS expects logical coordinates.
            # PySide also provides logical coordinates for widget geometry/events.
            
            # Scale coordinates only if NOT on macOS (e.g. Windows might need this)
            if sys.platform != "darwin":
                screen = QApplication.primaryScreen()
                dpr = screen.devicePixelRatio()
                print(f"Non-macOS platform detected: Scaling by DPR={dpr}")
                x = int(x * dpr)
                y = int(y * dpr)
                w = int(w * dpr)
                h = int(h * dpr)
            
            print(f"Final capture coordinates: ({x}, {y}, {w}, {h})")

            # Capture
            engine = CaptureEngine()
            img = engine.capture_region(x, y, w, h)
            
            # Open Editor
            self.editor = EditorWindow(img)
            self.editor.show()
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Capture Failed", f"An error occurred during capture:\n{str(e)}")
            print(f"Capture Error: {e}")
        
        # Show dashboard again or keep hidden? Snagit keeps dashboard open usually but minimized.
        self.show()
