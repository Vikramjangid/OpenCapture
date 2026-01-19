
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPixmap, QImage, QBrush, QColor, QPen, QUndoStack, QUndoCommand
from PIL.ImageQt import ImageQt
import logging

class AddItemCommand(QUndoCommand):
    def __init__(self, scene, item):
        super().__init__()
        self.scene = scene
        self.item = item

    def undo(self):
        self.scene.removeItem(self.item)

    def redo(self):
        self.scene.addItem(self.item)

class EditorCanvas(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setBackgroundBrush(Qt.darkGray)
        self.undo_stack = QUndoStack(self)
        self.current_color = QColor("red")
        self.current_line_width = 3
        logging.info("EditorCanvas initialized.")
        
    def set_image(self, pil_image):
        """Converts PIL image to QPixmap and adds to scene."""
        logging.info(f"Setting image in editor: {pil_image.size} mode {pil_image.mode}")
        self.scene.clear()
        self.undo_stack.clear()
        
        # Use ImageQt to handle conversion and strides correctly
        self.image = pil_image
        self.qimage = ImageQt(self.image)
        
        pixmap = QPixmap.fromImage(self.qimage)
        self.bg_item = self.scene.addPixmap(pixmap)
        self.bg_item.setZValue(-100) # Ensure it's always at the bottom
        self.setSceneRect(0, 0, pixmap.width(), pixmap.height())

    def resize_canvas(self, w, h):
        """Resizes the scene (and background image if possible)."""
        # For simplicity, we just scale the whole view? Or the image?
        # Usually checking "Resize Image" means scaling the bitmap.
        
        items = self.scene.items()
        if not items: return
        
        # Taking the last item as background (assumption)
        bg = items[-1]
        if isinstance(bg, QGraphicsPixmapItem):
             pix = bg.pixmap()
             new_pix = pix.scaled(w, h, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
             bg.setPixmap(new_pix)
             self.setSceneRect(0, 0, w, h)
             
             # Note: Other items (arrows/text) won't scale automatically unless we iterate and scale them too.
             # MVP: Only scales background. User can move items.

    def set_drawing_color(self, color):
        self.current_color = color
        
    def set_drawing_width(self, width):
        self.current_line_width = width

    def set_current_tool(self, tool_mode):
        self.current_tool = tool_mode
        if tool_mode != "none":
            self.setDragMode(QGraphicsView.NoDrag)
        else:
            self.setDragMode(QGraphicsView.ScrollHandDrag)

    def mousePressEvent(self, event):
        if not hasattr(self, 'current_tool') or self.current_tool == "none":
            super().mousePressEvent(event)
            return

        sp = self.mapToScene(event.pos())
        self.start_point = sp
        logging.info(f"Mouse Press at {sp}, Tool: {self.current_tool}")
        self.current_item = None
        
        
        if self.current_tool == "rectangle":
            from .tools import DraggableRectItem
            self.current_item = DraggableRectItem(sp.x(), sp.y(), 0, 0, self.current_color, self.current_line_width)
            self.scene.addItem(self.current_item)
            
        elif self.current_tool == "arrow":
            from .tools import ArrowItem
            self.current_item = ArrowItem(sp, sp, self.current_color, self.current_line_width)
            self.scene.addItem(self.current_item)
            
        elif self.current_tool == "circle":
            from .tools import CircleItem
            self.current_item = CircleItem(sp.x(), sp.y(), 0, 0, self.current_color, self.current_line_width)
            self.scene.addItem(self.current_item)
            
        elif self.current_tool == "line":
            from .tools import LineItem
            self.current_item = LineItem(sp.x(), sp.y(), sp.x(), sp.y(), self.current_color, self.current_line_width)
            self.scene.addItem(self.current_item)
            
        elif self.current_tool == "text":
            from .tools import TextItem
            self.current_item = TextItem("Your Text Here", sp, self.current_color)
            
            # Push command immediately for one-click items
            command = AddItemCommand(self.scene, self.current_item)
            self.undo_stack.push(command)
            
            self.current_tool = "none" 
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            
        elif self.current_tool == "blur":
            from .tools import DraggableRectItem
            self.current_item = DraggableRectItem(sp.x(), sp.y(), 0, 0)
            self.current_item.setPen(QPen(QColor(0, 120, 215), 1, Qt.DashLine))
            self.scene.addItem(self.current_item)
            
        elif self.current_tool == "crop":
            # Just like rectangle but with visual difference
            from .tools import DraggableRectItem
            self.current_item = DraggableRectItem(sp.x(), sp.y(), 0, 0)
            self.current_item.setPen(QPen(QColor(255, 255, 255), 2, Qt.DashLine))
            self.current_item.setBrush(QColor(0, 0, 0, 50))
            self.scene.addItem(self.current_item)
            
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if hasattr(self, 'current_item') and self.current_item:
            sp = self.mapToScene(event.pos())
            
            if self.current_tool in ["rectangle", "blur", "crop", "circle"]:
                x = min(self.start_point.x(), sp.x())
                y = min(self.start_point.y(), sp.y())
                w = abs(self.start_point.x() - sp.x())
                h = abs(self.start_point.y() - sp.y())
                
                if self.current_tool == "circle":
                    self.current_item.setRect(x, y, w, h)
                else:
                    self.current_item.setRect(x, y, w, h)
                
            elif self.current_tool == "arrow":
                self.current_item.update_arrow(self.start_point, sp)
            
            elif self.current_tool == "line":
                self.current_item.setLine(self.start_point.x(), self.start_point.y(), sp.x(), sp.y())
                
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if hasattr(self, 'current_item') and self.current_item:
            if self.current_tool == "crop":
                rect = self.current_item.rect().normalized()
                self.scene.removeItem(self.current_item)
                
                if rect.width() > 5 and rect.height() > 5:
                    # 1. Physical crop of the background pixmap
                    if hasattr(self, 'bg_item') and self.bg_item:
                        pix = self.bg_item.pixmap()
                        
                        # Calculate the intersection with the actual image bounds
                        # to avoid out-of-bounds errors in copy()
                        image_bounds = self.bg_item.pixmap().rect()
                        crop_rect = rect.toRect().intersected(image_bounds)
                        
                        if not crop_rect.isEmpty():
                            cropped_pix = pix.copy(crop_rect)
                            self.bg_item.setPixmap(cropped_pix)
                            self.bg_item.setPos(0, 0)
                            
                            # 2. Adjust all other items
                            # They must move by the offset of the crop
                            offset = crop_rect.topLeft()
                            for item in self.scene.items():
                                if item != self.bg_item:
                                    item.setPos(item.pos() - offset)
                            
                            # 3. Update Scene Rect
                            self.setSceneRect(0, 0, cropped_pix.width(), cropped_pix.height())
                
                self.current_tool = "none"
                self.setDragMode(QGraphicsView.ScrollHandDrag)
                
            elif self.current_tool == "blur":
                rect = self.current_item.rect().normalized()
                self.scene.removeItem(self.current_item)
                
                # Create actual blur item
                from .tools import BlurItem
                # Find background pixmap to sample from
                if hasattr(self, 'bg_item') and self.bg_item:
                    blur_item = BlurItem(rect, self.bg_item.pixmap())
                    command = AddItemCommand(self.scene, blur_item)
                    self.undo_stack.push(command)
                
                self.current_tool = "none"
                self.setDragMode(QGraphicsView.ScrollHandDrag)
            
            elif self.current_tool in ["rectangle", "arrow", "circle", "line"]:
                # Push Command for the item we just drew
                self.scene.removeItem(self.current_item)
                command = AddItemCommand(self.scene, self.current_item)
                self.undo_stack.push(command)

            self.current_item = None
        super().mouseReleaseEvent(event)
