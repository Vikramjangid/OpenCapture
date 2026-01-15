# OpenCapture

> A professional, lightweight, and powerful screen capture and annotation tool built with Python and PySide6.

OpenCapture offers a seamless experience for capturing screenshots, annotating them with precision tools, and sharing them instantly. Designed for efficiency and ease of use, it mimics the best features of premium tools like Snagit.

## 🚀 Features

### 📸 Capture Modes
- **Region Capture**: Select a specific area of your screen with pixel-perfect precision.
- **Full Screen Capture**: Instantly capture the entire desktop environment.
- **Multi-Monitor Support**: Seamlessly capture specific monitors or all screens at once.

### 🎨 Powerful Editor
- **Annotation Tools**:
    - **Arrow**: Draw attention to specific details.
    - **Rectangle**: Highlight areas of interest.
    - **Text**: Add labels and descriptions with a double-click.
    - **Blur**: specific areas to hide sensitive information.
- **Image Manipulation**:
    - **Crop**: Trim the image to focus on what matters.
    - **Resize**: Adjust image dimensions while maintaining quality.
- **Undo/Redo**: Full history support to revert or re-apply changes (Ctrl+Z / Ctrl+Shift+Z).

### 📤 Sharing & Output
- **Clipboard Integration**: Copy edited images directly to your clipboard (Ctrl+C) for pasting into Teams, Slack, or emails.
- **File Saving**: Save captures locally in high-quality formats (PNG, JPG) (Ctrl+S).

## ⌨️ Keyboard Shortcuts

| Action | Shortcut |
| :--- | :--- |
| **Save Image** | `Ctrl + S` |
| **Copy to Clipboard** | `Ctrl + C` |
| **Undo** | `Ctrl + Z` |
| **Redo** | `Ctrl + Shift + Z` |
| **Quit App** | Right-click Tray Icon > Quit |

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- pip

### Installation Steps

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/Vikramjangid/OpenCapture.git
    cd OpenCapture
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Application**
    ```bash
    python src/main.py
    ```
    *Alternatively, run the `run.bat` script on Windows.*

## 📂 Project Structure

```text
src/
├── capture/      # Screen capture logic (MSS, Region Selection)
├── editor/       # Image editor (Canvas, Tools, Undo/Redo)
├── ui/           # Dashboard, System Tray, Styles
├── utils/        # History, Help Text, Helpers
└── main.py       # Application Entry Point
```

## 👨‍💻 Credits

**Developed by Vikram Jangid**
- Email: [vikramjangid11@gmail.com](mailto:vikramjangid11@gmail.com)
- Project: OpenCapture

---
*Built with ❤️ using [PySide6](https://doc.qt.io/qtforpython/)*
