from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsPathItem, QGraphicsItem, QGraphicsTextItem, QGraphicsPixmapItem
from PySide6.QtGui import QPen, QColor, QPainterPath, QFont, QImage, QPixmap
from PySide6.QtCore import Qt

class DrawingTool:
    NONE = 0
    RECTANGLE = 1
    ARROW = 2

class DraggableRectItem(QGraphicsRectItem):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.setPen(QPen(QColor("red"), 3))
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)

class ArrowItem(QGraphicsPathItem):
    def __init__(self, start_point, end_point):
        super().__init__()
        self.setPen(QPen(QColor("red"), 3))
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.update_arrow(start_point, end_point)

    def update_arrow(self, start, end):
        path = QPainterPath()
        path.moveTo(start)
        path.lineTo(end)
        
        # Draw ArrowHead
        import math
        angle = math.atan2(start.y() - end.y(), start.x() - end.x())
        arrow_len = 15
        arrow_angle = math.pi / 6
        
        p1 = end + args_to_point(angle + arrow_angle, arrow_len)
        p2 = end + args_to_point(angle - arrow_angle, arrow_len)
        
        path.lineTo(p1)
        path.moveTo(end)
        path.lineTo(p2)
        
        self.setPath(path)

def args_to_point(angle, length):
    from PySide6.QtCore import QPointF
    import math
    return QPointF(math.cos(angle) * length, math.sin(angle) * length)

class TextItem(QGraphicsTextItem):
    def __init__(self, text="Double Click to Edit", position=None):
        super().__init__(text)
        if position:
            self.setPos(position)
        self.setDefaultTextColor(QColor("red"))
        self.setFont(QFont("Arial", 14, QFont.Bold))
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsFocusable)
        self.setTextInteractionFlags(Qt.TextEditorInteraction) # Allows editing

class BlurItem(QGraphicsPixmapItem):
    def __init__(self, rect, source_pixmap):
        super().__init__()
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        
        # Crop from source
        cropped = source_pixmap.copy(rect.toRect())
        
        # Apply intense blur (using simplistic scaling down and up for performance/no-dep)
        w, h = cropped.width(), cropped.height()
        if w > 0 and h > 0:
            small = cropped.scaled(max(1, w // 10), max(1, h // 10), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            blurred = small.scaled(w, h, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            self.setPixmap(blurred)
            self.setPos(rect.x(), rect.y())
