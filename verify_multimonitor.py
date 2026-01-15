import sys
import os
import mss
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QRect

def verify_mapping():
    print("Verifying Monitor Mapping between PySide6 and MSS...")
    
    # 1. Get MSS Monitors
    with mss.mss() as sct:
        mss_monitors = sct.monitors
        print(f"\nMSS Monitors (Bounding Box at index 0):")
        for i, m in enumerate(mss_monitors):
            print(f"  [{i}]: {m}")

    # 2. Get PySide6 Screens
    app = QApplication(sys.argv)
    screens = app.screens()
    print(f"\nPySide6 Screens:")
    total_rect = QRect()
    for i, s in enumerate(screens):
        geom = s.geometry()
        dpr = s.devicePixelRatio()
        print(f"  [{i}]: {s.name()} {geom} (DPR: {dpr})")
        total_rect = total_rect.united(geom)
    
    print(f"\nPySide6 Total Virtual Desktop: {total_rect}")
    
    # 3. Compare Bounding Boxes
    mss_bb = mss_monitors[0]
    ps_bb = total_rect
    
    print(f"\nComparison:")
    print(f"  MSS BB: left={mss_bb['left']}, top={mss_bb['top']}, w={mss_bb['width']}, h={mss_bb['height']}")
    print(f"  PS  BB: left={ps_bb.x()}, top={ps_bb.y()}, w={ps_bb.width()}, h={ps_bb.height()}")
    
    if (mss_bb['left'] == ps_bb.x() and mss_bb['top'] == ps_bb.y() and 
        mss_bb['width'] == ps_bb.width() and mss_bb['height'] == ps_bb.height()):
        print("\n✅ MATCH! Coordinate systems are aligned.")
    else:
        print("\n❌ MISMATCH! Coordinate systems are NOT aligned.")
        print("This may require manual offset adjustment in engine.py.")

if __name__ == "__main__":
    verify_mapping()
