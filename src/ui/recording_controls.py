from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QApplication
from PySide6.QtCore import Qt, QTimer, Signal, QPoint
from PySide6.QtGui import QIcon, QAction
import sys

class RecordingControls(QWidget):
    stop_clicked = Signal()
    pause_clicked = Signal(bool) # True=Paused, False=Resumed
    cancel_clicked = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Styles
        self.setStyleSheet("""
            QWidget {
                background-color: #333;
                color: white;
                border-radius: 10px;
                border: 1px solid #555;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #555;
            }
            QLabel {
                font-weight: bold;
                font-size: 14px;
                padding: 0 10px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        # Draggable Grip (Label 'REC')
        self.lbl_rec = QLabel("REC")
        self.lbl_rec.setStyleSheet("color: red;")
        layout.addWidget(self.lbl_rec)

        # Timer
        self.lbl_timer = QLabel("00:00")
        layout.addWidget(self.lbl_timer)

        # Pause Button
        self.btn_pause = QPushButton("||")
        self.btn_pause.setFixedSize(30, 30)
        self.btn_pause.setToolTip("Pause")
        self.btn_pause.clicked.connect(self.toggle_pause)
        layout.addWidget(self.btn_pause)

        # Stop Button
        self.btn_stop = QPushButton("■")
        self.btn_stop.setFixedSize(30, 30)
        self.btn_stop.setStyleSheet("font-size: 16px; color: #ff5555;")
        self.btn_stop.setToolTip("Stop")
        self.btn_stop.clicked.connect(self.on_stop)
        layout.addWidget(self.btn_stop)

        # Cancel Button
        # self.btn_cancel = QPushButton("X")
        # self.btn_cancel.setFixedSize(30, 30)
        # self.btn_cancel.clicked.connect(self.cancel_clicked.emit)
        # layout.addWidget(self.btn_cancel)

        self.elapsed_seconds = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)
        
        self.is_paused = False
        
        # Dragging logic
        self.old_pos = None

    def update_timer(self):
        self.elapsed_seconds += 1
        m, s = divmod(self.elapsed_seconds, 60)
        h, m = divmod(m, 60)
        if h > 0:
            self.lbl_timer.setText(f"{h:02}:{m:02}:{s:02}")
        else:
            self.lbl_timer.setText(f"{m:02}:{s:02}")

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            self.timer.stop()
            self.btn_pause.setText("▶")
            self.lbl_rec.setText("PAUSE")
            self.lbl_rec.setStyleSheet("color: yellow;")
        else:
            self.timer.start(1000)
            self.btn_pause.setText("||")
            self.lbl_rec.setText("REC")
            self.lbl_rec.setStyleSheet("color: red;")
            
        self.pause_clicked.emit(self.is_paused)

    def on_stop(self):
        self.timer.stop()
        self.stop_clicked.emit()

    # Dragging Implementation
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    def show_processing(self):
        """Updates the UI to show a processing state."""
        self.timer.stop()
        self.btn_pause.hide()
        self.btn_stop.hide()
        # self.btn_cancel.hide()
        
        self.lbl_rec.setText("SAVING...")
        self.lbl_rec.setStyleSheet("color: orange; font-weight: bold;")
        self.lbl_timer.setText("Please wait")
