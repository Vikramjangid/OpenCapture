from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QColor, QPalette

class CountdownOverlay(QWidget):
    finished = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
        # specific style for transparency
        self.setWindowState(Qt.WindowFullScreen)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)
        
        self.label = QLabel("")
        self.label.setAlignment(Qt.AlignCenter)
        font = QFont("Arial", 100, QFont.Bold)
        self.label.setFont(font)
        
        # White text with shadow/outline effect if possible (basic style)
        self.label.setStyleSheet("color: white; background-color: rgba(0, 0, 0, 100); border-radius: 20px; padding: 20px;")
        
        layout.addWidget(self.label)
        
        self.count = 3
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_count)

    def start(self):
        self.show()
        self.count = 3
        self.label.setText(str(self.count))
        self.timer.start(1000) # 1 second interval

    def update_count(self):
        self.count -= 1
        if self.count > 0:
            self.label.setText(str(self.count))
        else:
            self.label.setText("GO!")
            # Brief delay to show GO/Rec
            QTimer.singleShot(500, self.finish)
            self.timer.stop()
            
    def finish(self):
        self.hide()
        self.finished.emit()
