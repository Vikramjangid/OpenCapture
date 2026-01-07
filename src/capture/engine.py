import logging
import os
from PIL import ImageGrab, Image

# Setup Logger
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'debug_capture.log')
logging.basicConfig(filename=log_file, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class CaptureEngine:
    def __init__(self):
        pass # MSS no longer needed

    def capture_fullscreen(self):
        """Captures all screens combined."""
        try:
             # all_screens=True requires a relatively recent Pillow (9.1+)
             img = ImageGrab.grab(all_screens=True)
             return img
        except Exception as e:
            logging.error(f"Fullscreen Capture Error: {e}", exc_info=True)
            print(f"Fullscreen Capture Error: {e}")
            raise e

    def capture_region(self, left, top, width, height):
        """Captures a specific region."""
        if width <= 0 or height <= 0:
            raise ValueError(f"Invalid capture dimensions: {width}x{height}")
            
        try:
            bbox = (int(left), int(top), int(left + width), int(top + height))
            logging.info(f"ImageGrab capturing bbox: {bbox}")
            
            # Capture using Pillow's ImageGrab (GDI based on Windows)
            # This is robust against the stride issues we saw with mss
            img = ImageGrab.grab(bbox=bbox, all_screens=True)
            return img
            
        except Exception as e:
            logging.error(f"Capture Error: {e}", exc_info=True)
            print(f"Capture Error: {e}")
            raise e

    def capture_all_screens(self):
        return self.capture_fullscreen()
