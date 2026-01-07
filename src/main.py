import sys
import os

# Add local directory to path for imports to work in frozen/script mode
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from ui.dashboard import Dashboard

def main():
    app = QApplication(sys.argv)
    
    # Initialize Main Dashboard
    window = Dashboard()
    
    # Apply Dark Theme
    from ui.styles import DARK_THEME
    app.setStyleSheet(DARK_THEME)
    
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
