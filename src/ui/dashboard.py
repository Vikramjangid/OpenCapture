from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, 
                               QLabel, QHBoxLayout, QListWidget, QSystemTrayIcon, QMenu, QStyle, QApplication, QTabWidget, QMessageBox)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QAction
import sys

class ImageCaptureWidget(QWidget):
    def __init__(self, parent_dashboard):
        super().__init__()
        self.dashboard = parent_dashboard
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Header
        header = QLabel("Image Capture")
        header.setObjectName("sectionHeader")
        layout.addWidget(header, alignment=Qt.AlignCenter)


        # Capture Region Button
        self.btn_capture = QPushButton("Capture Region")
        self.btn_capture.setObjectName("primaryInfo") 
        self.btn_capture.setFixedHeight(50)
        self.btn_capture.clicked.connect(self.dashboard.start_capture)
        layout.addWidget(self.btn_capture)

        # Dynamic Full Screen Buttons
        from PySide6.QtGui import QGuiApplication
        screens = QGuiApplication.screens()
        for i, screen in enumerate(screens):
            btn = QPushButton(f"Capture {screen.name()}")
            btn.setObjectName("primarySuccess")
            btn.setFixedHeight(50)
            btn.clicked.connect(lambda checked=False, idx=i: self.dashboard.start_full_capture(idx))
            layout.addWidget(btn)
        
        # All screens capture
        if len(screens) > 1:
            btn_all = QPushButton("Capture All Screens")
            btn_all.setObjectName("primarySuccess")
            btn_all.setFixedHeight(50)
            btn_all.clicked.connect(lambda checked=False: self.dashboard.start_full_capture(None))
            layout.addWidget(btn_all)

        layout.addStretch()

class VideoCaptureWidget(QWidget):
    def __init__(self, parent_dashboard):
        super().__init__()
        self.dashboard = parent_dashboard
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Header
        header = QLabel("Video Screen Recorder")
        header.setObjectName("sectionHeader")
        layout.addWidget(header, alignment=Qt.AlignCenter)


        # Video Options Group
        from PySide6.QtWidgets import QGroupBox, QCheckBox
        options_group = QGroupBox("Recording Options")
        options_layout = QVBoxLayout()
        
        self.chk_mic = QCheckBox("Record Microphone")
        self.chk_mic.setChecked(True)
        options_layout.addWidget(self.chk_mic)

        self.chk_webcam = QCheckBox("Round Webcam Overlay")
        options_layout.addWidget(self.chk_webcam)
        
        self.chk_cursor = QCheckBox("Capture Cursor")
        self.chk_cursor.setChecked(True)
        options_layout.addWidget(self.chk_cursor)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Capture Region Button (Video)
        self.btn_record_region = QPushButton("Record Region")
        self.btn_record_region.setObjectName("primaryInfo")
        self.btn_record_region.setFixedHeight(50)
        self.btn_record_region.clicked.connect(lambda: self.dashboard.start_video_capture("region"))
        layout.addWidget(self.btn_record_region)

        # Record Full Screen
        from PySide6.QtGui import QGuiApplication
        screens = QGuiApplication.screens()
        for i, screen in enumerate(screens):
            btn = QPushButton(f"Record {screen.name()}")
            btn.setObjectName("importantError") # Red for recording
            btn.setFixedHeight(50)
            btn.clicked.connect(lambda checked=False, idx=i: self.dashboard.start_video_capture("screen", idx))
            layout.addWidget(btn)

        layout.addStretch()

class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OpenCapture")
        self.resize(450, 600)
        
        # Set Window Icon
        import os
        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "icon.png"))
        if not os.path.exists(icon_path):
             icon_path = "icon.png"
             
        self.setWindowIcon(QIcon(icon_path))
        self.icon_path = icon_path 

        self.init_ui()
        self.init_tray()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header = QLabel("OpenCapture")
        header.setObjectName("dashboardHeader")
        main_layout.addWidget(header, alignment=Qt.AlignCenter)


        # Tabs
        self.tabs = QTabWidget()

        
        self.image_tab = ImageCaptureWidget(self)
        self.video_tab = VideoCaptureWidget(self)
        
        self.tabs.addTab(self.image_tab, self.style().standardIcon(QStyle.SP_DialogSaveButton), "Image Capture")
        self.tabs.addTab(self.video_tab, self.style().standardIcon(QStyle.SP_MediaPlay), "Video Record")
        
        main_layout.addWidget(self.tabs)

        # Recent Captures Label
        recent_label = QLabel("Recent Captures")
        recent_label.setObjectName("sectionHeader")
        main_layout.addWidget(recent_label)


        # List for recent files
        self.recent_list = QListWidget()
        main_layout.addWidget(self.recent_list)
        
        # Help / FAQ Button
        self.btn_help = QPushButton("Quick Start Guide / FAQ")
        self.btn_help.setFixedHeight(40)
        self.btn_help.clicked.connect(self.show_help)
        main_layout.addWidget(self.btn_help)
        
        self.load_recent_captures()

    def show_help(self):
        from ui.help_dialog import HelpDialog
        from utils.help_text import FAQ_TEXT, ABOUT_TEXT
        dlg = HelpDialog("Quick Start Guide", FAQ_TEXT + "\n\n" + ABOUT_TEXT, self)
        dlg.exec()

    def load_recent_captures(self):
        from utils.history import HistoryManager
        import os
        self.recent_list.clear() # Fix: recent_list was missing in previous method update, relying on init_ui order
        hm = HistoryManager()
        for path in hm.get_recent():
            if os.path.exists(path):
                self.recent_list.addItem(path)

    def init_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        from PySide6.QtWidgets import QStyle
        if hasattr(self, 'icon_path') and self.icon_path:
             self.tray_icon.setIcon(QIcon(self.icon_path))
        else:
             self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        
        menu = QMenu()

        capture_action = QAction("Capture Image", self)
        capture_action.triggered.connect(self.start_capture)
        menu.addAction(capture_action)
        
        capture_video_action = QAction("Record Video (Region)", self)
        capture_video_action.triggered.connect(lambda: self.start_video_capture("region"))
        menu.addAction(capture_video_action)
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

    def showEvent(self, event):
        self.load_recent_captures()
        super().showEvent(event)

    # --- IMAGE CAPTURE METHODS ---
    def start_capture(self):
        self.hide()
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
        
        self.hide()
        QApplication.processEvents()
        time.sleep(0.2)
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
        
        if hasattr(self, 'overlays'):
            for overlay in self.overlays:
                overlay.close()
            self.overlays = []
            
        QApplication.processEvents()
        time.sleep(0.2)
        QApplication.processEvents()
        
        try:
            if w <= 0 or h <= 0: return
            
            # Platform specific scaling usually here (omitted for brevity, assume similar to before or handled in engine)
            if sys.platform != "darwin":
                screen = QApplication.primaryScreen()
                dpr = screen.devicePixelRatio()
                x = int(x * dpr)
                y = int(y * dpr)
                w = int(w * dpr)
                h = int(h * dpr)

            engine = CaptureEngine()
            img = engine.capture_region(x, y, w, h)
            
            self.editor = EditorWindow(img)
            self.editor.show()
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Capture Failed", f"An error occurred during capture:\n{str(e)}")
        
        self.show()

    # --- VIDEO CAPTURE METHODS ---
    def start_video_capture(self, mode, monitor_index=None):
        """
        mode: 'region' or 'screen'
        """
        self.hide()
        QApplication.processEvents()
        
        # Get options from Video Tab
        record_mic = self.video_tab.chk_mic.isChecked()
        record_webcam = self.video_tab.chk_webcam.isChecked()
        capture_cursor = self.video_tab.chk_cursor.isChecked()
        
        logging_info = f"Starting Video Capture: Mode={mode}, Mic={record_mic}, Webcam={record_webcam}, Cursor={capture_cursor}"
        print(logging_info)
        
        if mode == 'region':
            # Reuse region selection overlay but connect to video start
            from capture.region import RegionSelectionOverlay
            from PySide6.QtGui import QGuiApplication
            
            self.overlays = []
            for screen in QGuiApplication.screens():
                overlay = RegionSelectionOverlay(screen)
                # We need a specific slot for video region selection
                overlay.selection_made.connect(lambda x,y,w,h: self.on_video_region_selected(x,y,w,h, record_mic, record_webcam, capture_cursor))
                overlay.selection_updated.connect(self.on_selection_updated)
                overlay.canceled.connect(self.on_capture_canceled)
                overlay.show()
                self.overlays.append(overlay)
        else:
            # Full screen video
            # TODO: trigger recorder manager with specific monitor
            self.start_recording_manager(monitor_index, None, record_mic, record_webcam, capture_cursor)

    def on_video_region_selected(self, x, y, w, h, mic, webcam, cursor):
        if hasattr(self, 'overlays'):
            for overlay in self.overlays:
                overlay.close()
            self.overlays = []

        QApplication.processEvents()
        
        if sys.platform != "darwin":
             screen = QApplication.primaryScreen()
             dpr = screen.devicePixelRatio()
             x = int(x * dpr)
             y = int(y * dpr)
             w = int(w * dpr)
             h = int(h * dpr)
             
        self.start_recording_manager(None, (x, y, w, h), mic, webcam, cursor)

    def start_recording_manager(self, monitor_index, region, mic, webcam, cursor):
        from capture.recorder_manager import RecorderManager
        
        self.recorder_manager = RecorderManager()
        self.recorder_manager.recording_finished.connect(self.on_recording_finished)
        self.recorder_manager.start_recording(
            monitor_index=monitor_index,
            region=region,
            input_mic=mic,
            input_webcam=webcam,
            capture_cursor=cursor
        )
        
        # Show floating controls (inside manager or here? Manager is better to own it)
        # We'll assume manager handles showing the control UI

    def on_recording_finished(self, output_files):
        print(f"Recording finished. Files: {output_files}")
        self.show()
        
        # Open Video Editor
        from editor.video_window import VideoEditorWindow
        if output_files and len(output_files) > 0:
            video_file = output_files[0] 
            audio_file = None
            if len(output_files) > 1:
                audio_file = output_files[1]
                
            self.video_editor = VideoEditorWindow(video_file, audio_file)
            self.video_editor.show()

