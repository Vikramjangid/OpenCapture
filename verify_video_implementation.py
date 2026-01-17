import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

print("Checking imports...")

try:
    import capture.video
    print("SUCCESS: capture.video")
except Exception as e:
    print(f"FAILED: capture.video - {e}")

try:
    import capture.audio
    print("SUCCESS: capture.audio")
except Exception as e:
    print(f"FAILED: capture.audio - {e}")

try:
    import ui.recording_controls
    print("SUCCESS: ui.recording_controls")
except Exception as e:
    print(f"FAILED: ui.recording_controls - {e}")

try:
    import capture.recorder_manager
    print("SUCCESS: capture.recorder_manager")
except Exception as e:
    print(f"FAILED: capture.recorder_manager - {e}")

try:
    import editor.video_window
    print("SUCCESS: editor.video_window")
except Exception as e:
    print(f"FAILED: editor.video_window - {e}")

try:
    import ui.dashboard
    print("SUCCESS: ui.dashboard")
except Exception as e:
    print(f"FAILED: ui.dashboard - {e}")

print("Import check complete.")
