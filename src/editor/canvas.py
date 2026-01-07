
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
        self.scene.addPixmap(pixmap)
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
            self.current_item = DraggableRectItem(sp.x(), sp.y(), 0, 0)
            # self.scene.addItem(self.current_item) # Done via command later? No, visual feedback needed
            self.scene.addItem(self.current_item)
            
        elif self.current_tool == "arrow":
            from .tools import ArrowItem
            self.current_item = ArrowItem(sp, sp)
            self.scene.addItem(self.current_item)
            
        elif self.current_tool == "text":
            from .tools import TextItem
            self.current_item = TextItem("Your Text Here", sp)
            
            # Push command immediately for one-click items
            command = AddItemCommand(self.scene, self.current_item)
            self.undo_stack.push(command)
            
            self.current_tool = "none" 
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            
        elif self.current_tool == "crop":
            # Just like rectangle but with visual difference
            from .dialogs import CropSelector
            # Convert to rect item for visual
            from .tools import DraggableRectItem
            self.current_item = DraggableRectItem(sp.x(), sp.y(), 0, 0)
            self.current_item.setPen(QPen(QColor(255, 255, 255), 2, Qt.DashLine))
            self.current_item.setBrush(QColor(0, 0, 0, 50))
            self.scene.addItem(self.current_item)
            
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if hasattr(self, 'current_item') and self.current_item:
            sp = self.mapToScene(event.pos())
            
            if self.current_tool in ["rectangle", "blur"]:
                x = min(self.start_point.x(), sp.x())
                y = min(self.start_point.y(), sp.y())
                w = abs(self.start_point.x() - sp.x())
                h = abs(self.start_point.y() - sp.y())
                self.current_item.setRect(x, y, w, h)
                
            elif self.current_tool == "arrow":
                self.current_item.update_arrow(self.start_point, sp)
                
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if hasattr(self, 'current_item') and self.current_item:
            if self.current_tool == "crop":
                rect = self.current_item.rect()
                self.scene.removeItem(self.current_item)
                
                # Perform Crop
                # We need to crop the SCENE rect and the BACKGROUND image.
                # Just setting scene rect is usually enough for display, but for saving we want to crop the image.
                
                # 1. Update Scene Rect
                # Normalize rect to handle negative width/height
                normalized_rect = rect.normalized()
                
                # Check for validity
                if normalized_rect.width() > 10 and normalized_rect.height() > 10:
                    self.setSceneRect(normalized_rect)
                    # We should also crop the background image to save memory/cleanliness?
                    # Or just rely on render(scene_rect) which we do in save_image!
                    # Reset tool
                    self.current_tool = "none"
                    self.setDragMode(QGraphicsView.ScrollHandDrag)
                
            elif self.current_tool == "blur":
                # Finalize blur
                rect = self.current_item.rect()
                # Remove the selector
                self.scene.removeItem(self.current_item)
                
                # Create actual blur item
                from .tools import BlurItem
                # Get the whole scene pixmap? Or assuming the bg is the first item?
                # We need the underlying image. 
                # Assumption: The first item in the scene is the background Pixmap
                items = self.scene.items()
                bg_item = items[-1] # Background is usually at the bottom (-1 in painter's algo?)
                if isinstance(bg_item, QGraphicsPixmapItem):
                    blur_item = BlurItem(rect, bg_item.pixmap())
                    # Push Command
                    command = AddItemCommand(self.scene, blur_item)
                    self.undo_stack.push(command)
            
            elif self.current_tool in ["rectangle", "arrow"]:
                # Push Command for the item we just drew
                # To do this correctly with undo stack, the item must be removed first if we want 'redo' to add it.
                # But we already added it for visual feedback.
                # QUndoStack.push() executes redo(). 
                # So we should remove it, then push (which adds it back).
                self.scene.removeItem(self.current_item)
                command = AddItemCommand(self.scene, self.current_item)
                self.undo_stack.push(command)

            self.current_item = None
        super().mouseReleaseEvent(event)
