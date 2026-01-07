from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt

class HelpDialog(QDialog):
    def __init__(self, title, content, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(500, 600)
        
        layout = QVBoxLayout(self)
        
        # Content
        text = QTextBrowser()
        text.setHtml(content)
        text.setOpenExternalLinks(True)
        # Style override for text browser to look clean in dark mode
        text.setStyleSheet("border: none; background-color: #333; color: #ddd; padding: 10px; font-size: 14px;")
        layout.addWidget(text)
        
        # Close Button
        btn_layout = QHBoxLayout()
        btn_close = QPushButton("Close")
        btn_close.setFixedWidth(100)
        btn_close.clicked.connect(self.accept)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)
        
        layout.addLayout(btn_layout)
