from PySide6.QtWidgets import QWidget, QApplication, QRubberBand
from PySide6.QtCore import Qt, QRect, QPoint, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QBrush

class RegionSelectionOverlay(QWidget):
    # Signal emitted when a selection is finalized: (x, y, w, h)
    selection_made = Signal(int, int, int, int)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground) # Important for transparency
        self.setCursor(Qt.CrossCursor)
        
        # Geometry covers all screens
        screen_geometry = QApplication.primaryScreen().virtualGeometry()
        self.setGeometry(screen_geometry)
        
        self.origin = QPoint()
        self.final_rect = QRect()
        self.is_selecting = False
        
        # Visual style
        self.overlay_color = QColor(0, 0, 0, 100) # Semi-transparent black
        self.selection_border_color = QColor(0, 120, 215) # Blue
        self.selection_fill_color = QColor(255, 255, 255, 0) # Transparent inside

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw the dark overlay over the whole screen
        painter.setBrush(self.overlay_color)
        painter.setPen(Qt.NoPen)
        full_rect = self.rect()
        
        if self.is_selecting:
            # We want to draw the overlay EVERYWHERE EXCEPT the selected rect.
            # Easiest way using paths or just simple subtraction logic visually?
            # Actually, standard way is draw full dim, then draw clear rect? 
            # Or draw 4 rectangles surrounding the selection.
            
            # Let's try drawing full dim, then setting composition mode to clear the selection?
            # No, that clears to transparent (which reveals desktop), which is what we want!
            
            painter.drawRect(full_rect)
            
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            current_rect = QRect(self.origin, self.current_pos).normalized()
            painter.setBrush(Qt.SolidPattern) # Brush content doesn't matter for Clear mode
            painter.drawRect(current_rect)
            
            # Reset to draw border
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            painter.setPen(QPen(self.selection_border_color, 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(current_rect)
            
        else:
            painter.drawRect(full_rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.origin = event.pos()
            self.current_pos = event.pos()
            self.is_selecting = True
            self.update()

    def mouseMoveEvent(self, event):
        if self.is_selecting:
            self.current_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.is_selecting:
            self.is_selecting = False
            rect = QRect(self.origin, event.pos()).normalized()
            self.close()
            # Check for minimal size to avoid accidental clicks and crashes
            if rect.width() > 10 and rect.height() > 10:
                self.selection_made.emit(rect.x(), rect.y(), rect.width(), rect.height())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
