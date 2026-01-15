import logging
import os
import mss
from PIL import Image

# Setup Logger
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'debug_capture.log')
logging.basicConfig(filename=log_file, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class CaptureEngine:
    def __init__(self):
        pass

    def capture_fullscreen(self, monitor_index=None):
        """Captures all screens combined or a specific monitor by index."""
        try:
            with mss.mss() as sct:
                if monitor_index is not None:
                    # sct.monitors[0] is all monitors, so screen 1 is sct.monitors[1]
                    monitor = sct.monitors[monitor_index + 1]
                    logging.info(f"Capturing monitor {monitor_index + 1}: {monitor}")
                else:
                    # All monitors
                    monitor = sct.monitors[0]
                    logging.info(f"Capturing all monitors: {monitor}")
                
                sct_img = sct.grab(monitor)
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
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
            # MSS uses logical coordinates which match PySide's global screen coordinates
            monitor = {"top": int(top), "left": int(left), "width": int(width), "height": int(height)}
            logging.info(f"MSS capturing region: {monitor}")
            
            with mss.mss() as sct:
                logging.debug(f"All monitors: {sct.monitors}")
                sct_img = sct.grab(monitor)
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                logging.info(f"Captured image size: {img.size}")
                return img
            
        except Exception as e:
            logging.error(f"Capture Error: {e}", exc_info=True)
            print(f"Capture Error: {e}")
            raise e

    def capture_all_screens(self):
        return self.capture_fullscreen()
