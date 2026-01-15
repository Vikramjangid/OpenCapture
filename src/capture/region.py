from PySide6.QtWidgets import QWidget, QApplication, QRubberBand
from PySide6.QtCore import Qt, QRect, QPoint, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QBrush

class RegionSelectionOverlay(QWidget):
    # Signal emitted when a selection is finalized: (x, y, w, h)
    selection_made = Signal(int, int, int, int)
    selection_updated = Signal(QRect)
    canceled = Signal()

    def __init__(self, screen=None):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground) # Important for transparency
        self.setCursor(Qt.CrossCursor)
        
        # Geometry covers a specific screen or all
        self.target_screen = screen
        self.update_geometry()
        
        self.origin = QPoint()
        self.current_pos = QPoint()
        self.is_selecting = False
        self.global_selection_rect = QRect()
        
        import logging
        self.logger = logging.getLogger("RegionSelection")

    def update_geometry(self):
        """Calculates and sets geometry."""
        from PySide6.QtGui import QGuiApplication
        
        if self.target_screen:
            geom = self.target_screen.geometry()
            print(f"Overlay targeting screen: {self.target_screen.name()}, Geometry: {geom}")
            self.setGeometry(geom)
        else:
            # Fallback to virtual desktop (old behavior)
            total_rect = QRect()
            for screen in QGuiApplication.screens():
                total_rect = total_rect.united(screen.geometry())
            self.setGeometry(total_rect)
        
        # Visual style
        self.overlay_color = QColor(0, 0, 0, 100) # Semi-transparent black
        self.selection_border_color = QColor(0, 120, 215) # Blue

    def sync_selection(self, global_rect, is_selecting):
        self.global_selection_rect = global_rect
        self.is_selecting = is_selecting
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw the dark overlay
        painter.setBrush(self.overlay_color)
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())
        
        if self.is_selecting and not self.global_selection_rect.isEmpty():
            # Map global rect to local coordinates
            local_rect = QRect(
                self.mapFromGlobal(self.global_selection_rect.topLeft()),
                self.mapFromGlobal(self.global_selection_rect.bottomRight())
            )
            
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.setBrush(Qt.SolidPattern) 
            painter.drawRect(local_rect)
            
            # Reset to draw border
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            painter.setPen(QPen(self.selection_border_color, 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(local_rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.origin = self.mapToGlobal(event.pos())
            self.is_selecting = True
            self.update_selection(event.pos())

    def mouseMoveEvent(self, event):
        if self.is_selecting:
            self.update_selection(event.pos())

    def update_selection(self, current_pos):
        self.global_selection_rect = QRect(self.origin, self.mapToGlobal(current_pos)).normalized()
        self.selection_updated.emit(self.global_selection_rect)
        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.is_selecting:
            self.is_selecting = False
            
            global_release = self.mapToGlobal(event.pos())
            rect = QRect(self.origin, global_release).normalized()
            
            print(f"Selection released: {rect.x()}, {rect.y()}, {rect.width()}x{rect.height()}")
            self.close()
            
            # Check for minimal size to avoid accidental clicks
            if rect.width() > 5 and rect.height() > 5:
                self.selection_made.emit(rect.x(), rect.y(), rect.width(), rect.height())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.canceled.emit()
            self.close()
