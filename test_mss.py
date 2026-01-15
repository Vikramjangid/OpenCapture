import mss
from PIL import Image

def test_mss():
    print("Testing MSS Capture...")
    try:
        with mss.mss() as sct:
            # Full screen
            monitor = sct.monitors[0] # All screens
            sct_img = sct.grab(monitor)
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            print(f"MSS Fullscreen Success! size: {img.size}")
            img.save("test_mss_full.png")
            
            # Region (monitor 1)
            reg = {"top": 100, "left": 100, "width": 400, "height": 300}
            sct_img = sct.grab(reg)
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            print(f"MSS Region Success! size: {img.size}")
            img.save("test_mss_reg.png")
    except Exception as e:
        print(f"MSS Failed: {e}")

if __name__ == "__main__":
    test_mss()
