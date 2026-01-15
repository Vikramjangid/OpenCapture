import sys
import os

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
sys.path.append(src_dir)

from capture.engine import CaptureEngine
from PIL import Image

def test_fullscreen():
    print("Testing Fullscreen Capture...")
    engine = CaptureEngine()
    try:
        img = engine.capture_fullscreen()
        print(f"Success! Image size: {img.size}")
        img.save("test_fullscreen.png")
        print("Saved to test_fullscreen.png")
    except Exception as e:
        print(f"Fullscreen Capture Failed: {e}")

def test_region():
    print("\nTesting Region Capture (100, 100, 400, 300)...")
    engine = CaptureEngine()
    try:
        # These should be logical coordinates on macOS
        img = engine.capture_region(100, 100, 400, 300)
        print(f"Success! Image size: {img.size}")
        img.save("test_region.png")
        print("Saved to test_region.png")
    except Exception as e:
        print(f"Region Capture Failed: {e}")

if __name__ == "__main__":
    test_fullscreen()
    test_region()
