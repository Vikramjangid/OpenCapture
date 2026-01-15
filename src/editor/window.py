from PySide6.QtWidgets import QMainWindow, QToolBar, QStatusBar
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import Qt
from .canvas import EditorCanvas

class EditorWindow(QMainWindow):
    def __init__(self, pil_image=None):
        super().__init__()
        self.setWindowTitle("Snagit Editor - Developed by : Vikram Jangid (vikramjangid11@gmail.com)")
        self.resize(1200, 800)
        
        self.canvas = EditorCanvas()
        self.setCentralWidget(self.canvas)
        
        self.init_toolbar()
        
        if pil_image:
            self.canvas.set_image(pil_image)

    def init_toolbar(self):
        toolbar = QToolBar("Tools")
        self.addToolBar(toolbar)
        
        # Save Action
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_image)
        toolbar.addAction(save_action)

        # Copy Action
        copy_action = QAction("Copy", self)
        copy_action.setShortcut("Ctrl+C") 
        copy_action.triggered.connect(self.copy_to_clipboard)
        toolbar.addAction(copy_action)
        
        toolbar.addSeparator()

        # Undo/Redo
        undo_action = self.canvas.undo_stack.createUndoAction(self, "Undo")
        undo_action.setShortcut("Ctrl+Z")
        toolbar.addAction(undo_action)

        redo_action = self.canvas.undo_stack.createRedoAction(self, "Redo")
        redo_action.setShortcut("Ctrl+Shift+Z") # Or Ctrl+Y
        toolbar.addAction(redo_action)
        
        toolbar.addSeparator()

        # Drawing Tools
        self.add_tool_action(toolbar, "Arrow", "arrow")
        self.add_tool_action(toolbar, "Rectangle", "rectangle")
        self.add_tool_action(toolbar, "Text", "text")
        self.add_tool_action(toolbar, "Blur", "blur")
        
        toolbar.addSeparator()
        
        # Crop Action
        crop_action = QAction("Crop", self)
        crop_action.triggered.connect(self.start_crop)
        toolbar.addAction(crop_action)
        
        # Resize Action
        resize_action = QAction("Resize", self)
        resize_action.triggered.connect(self.open_resize_dialog)
        toolbar.addAction(resize_action)

        toolbar.addSeparator()
        
        # Help Action
        help_action = QAction("Help", self)
        help_action.triggered.connect(self.show_help)
        toolbar.addAction(help_action)
        
    def show_help(self):
        from ui.help_dialog import HelpDialog
        from utils.help_text import FAQ_TEXT
        dlg = HelpDialog("Quick Start Guide", FAQ_TEXT, self)
        dlg.exec()
        
    def start_crop(self):
        # We can reuse the RegionSelectionOverlay, but effectively we want to crop the existing image.
        # This is a bit tricky since Overlay captures SCREEN.
        # A proper crop tool should be inside the canvas.
        # Let's implement a "Crop Mode" in Canvas.
        self.canvas.set_current_tool("crop")

    def open_resize_dialog(self):
        from .dialogs import ResizeDialog
        # Get current scene size
        rect = self.canvas.scene.itemsBoundingRect()
        if rect.isEmpty():
             # Fallback
             rect = self.canvas.scene.sceneRect()
             
        dlg = ResizeDialog(int(rect.width()), int(rect.height()), self)
        if dlg.exec():
            w, h = dlg.get_result()
            self.canvas.resize_canvas(w, h)


    def save_image(self):
        from PySide6.QtWidgets import QFileDialog
        filename, _ = QFileDialog.getSaveFileName(self, "Save Capture", "capture.png", "Images (*.png *.jpg)")
        if filename:
            # Render the scene to an image
            from PySide6.QtGui import QImage, QPainter
            from PySide6.QtCore import QRectF
            
            # Create a QImage with the scene's size
            scene_rect = self.canvas.scene.sceneRect()
            image = QImage(scene_rect.size().toSize(), QImage.Format_ARGB32)
            image.fill(Qt.transparent)
            
            painter = QPainter(image)
            self.canvas.scene.render(painter, QRectF(image.rect()), scene_rect)
            painter.end()
            
            image.save(filename)
            
            # Add to history
            from utils.history import HistoryManager
            hm = HistoryManager()
            hm.add_entry(filename)

    def copy_to_clipboard(self):
        from PySide6.QtGui import QGuiApplication, QImage, QPainter
        
        scene_rect = self.canvas.scene.sceneRect()
        image = QImage(scene_rect.size().toSize(), QImage.Format_ARGB32)
        image.fill(Qt.transparent)
        
        painter = QPainter(image)
        self.canvas.scene.render(painter)
        painter.end()
        
        clipboard = QGuiApplication.clipboard()
        clipboard.setImage(image)
        print("Copied to clipboard")

    def add_tool_action(self, toolbar, name, mode):
        action = QAction(name, self)
        action.triggered.connect(lambda: self.set_tool(mode))
        toolbar.addAction(action)

    def set_tool(self, tool_mode):
        print(f"Tool selected: {tool_mode}")
        self.canvas.set_current_tool(tool_mode)

