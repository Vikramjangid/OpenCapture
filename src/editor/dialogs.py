from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QPushButton, QGraphicsRectItem, QGraphicsItem
from PySide6.QtGui import QPen, QColor, QBrush
from PySide6.QtCore import Qt, QRect

class ResizeDialog(QDialog):
    def __init__(self, current_width, current_height, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Resize Image")
        self.layout = QVBoxLayout(self)
        
        # Width
        w_layout = QHBoxLayout()
        w_layout.addWidget(QLabel("Width:"))
        self.w_spin = QSpinBox()
        self.w_spin.setRange(1, 10000)
        self.w_spin.setValue(current_width)
        w_layout.addWidget(self.w_spin)
        self.layout.addLayout(w_layout)
        
        # Height
        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel("Height:"))
        self.h_spin = QSpinBox()
        self.h_spin.setRange(1, 10000)
        self.h_spin.setValue(current_height)
        h_layout.addWidget(self.h_spin)
        self.layout.addLayout(h_layout)
        
        # Buttons
        btns = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        btns.addWidget(ok_btn)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(cancel_btn)
        self.layout.addLayout(btns)
        
    def get_result(self):
        return self.w_spin.value(), self.h_spin.value()

class CropSelector(QGraphicsRectItem):
    """A simple rect that shows what will be cropped."""
    def __init__(self, rect):
        super().__init__(rect)
        self.setPen(QPen(QColor(255, 255, 255), 2, Qt.DashLine))
        self.setBrush(QColor(0, 0, 0, 100)) # Darken outside? No, this is the selection. 
        # Actually standard is: Darken everything else, clear inside.
        # But for simplicity, let's just make a dashed box that is resizable/movable.
        
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        # To make it resizable is complex (handles). 
        # For MVP, let's just use the Rectangle drag logic form Canvas but strictly for this item.
