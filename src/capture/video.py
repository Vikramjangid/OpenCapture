import cv2
import numpy as np
import mss
import time
import platform
import logging
from PySide6.QtCore import QThread, Signal
import pyautogui
from datetime import datetime
import collections

class VideoRecorder(QThread):
    error_occurred = Signal(str)
    recording_started = Signal() # Renamed concept: now means "Setup Done, Ready for Countdown"

    def __init__(self, output_path, region=None, monitor_index=None, fps=20.0, 
                 webcam_enabled=False, cursor_enabled=True):
        super().__init__()
        self.output_path = output_path
        self.region = region # tuple (x, y, w, h)
        self.monitor_index = monitor_index # int
        self.fps = fps
        self.webcam_enabled = webcam_enabled
        self.cursor_enabled = cursor_enabled
        
        self.is_running = True
        self.is_paused = False
        self._recording_active = False # New flag: waits for countdown
        
    def start_capture(self):
        """Called after countdown to actually begin writing frames."""
        self._recording_active = True

    def run(self):
        try:
            with mss.mss() as sct:
                # Determine capture area
                if self.region:
                    monitor = {"top": self.region[1], "left": self.region[0], "width": self.region[2], "height": self.region[3]}
                elif self.monitor_index is not None:
                    # sct.monitors[0] is all, [1] is first. 
                    if self.monitor_index + 1 < len(sct.monitors):
                        monitor = sct.monitors[self.monitor_index + 1]
                    else:
                        monitor = sct.monitors[1] # Fallback
                else:
                    monitor = sct.monitors[0] # All screens

                # Keep original monitor for capturing
                capture_monitor = monitor.copy()
                
                # Align capture dimensions to be even numbers upfront
                # This ensures sct.grab() returns the correct size, avoiding expensive cv2.resize() in the loop
                if capture_monitor["width"] % 2 != 0:
                    capture_monitor["width"] -= 1
                if capture_monitor["height"] % 2 != 0:
                    capture_monitor["height"] -= 1
                
                width = capture_monitor["width"]
                height = capture_monitor["height"]
                    
                logging.info(f"Video Capture Target: {width}x{height}")
                
                # Video Writer Setup
                fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
                out = cv2.VideoWriter(self.output_path, fourcc, self.fps, (width, height))
                
                if not out.isOpened():
                    msg = "Could not open VideoWriter. Check codec or file permissions."
                    logging.error(msg)
                    self.error_occurred.emit(msg)
                    return

                # Webcam Setup
                cap_webcam = None
                if self.webcam_enabled:
                    # Use CAP_DSHOW on Windows to avoid black screens/long delays
                    backend = cv2.CAP_DSHOW if platform.system() == "Windows" else cv2.CAP_ANY
                    cap_webcam = cv2.VideoCapture(0, backend)
                    
                    if not cap_webcam.isOpened():
                        logging.warning("Could not open webcam.")
                        cap_webcam = None
                    else:
                        # Warmup
                        ret, _ = cap_webcam.read()
                        if not ret:
                            logging.warning("Webcam opened but failed to read frame.")
                            cap_webcam = None

                # Ready for countdown
                self.recording_started.emit() 
                
                # Wait for start signal (Countdown)
                while self.is_running and not self._recording_active:
                     time.sleep(0.05)
                
                if not self.is_running:
                    # Stopped during countdown
                    out.release()
                    if cap_webcam: cap_webcam.release()
                    return

                logging.info("Starting Main Capture Loop")
                start_time = time.time()
                frame_count = 0
                
                while self.is_running:
                    if self.is_paused:
                        # Adjust start_time to account for pause duration so we don't jump ahead
                        pause_start = time.time()
                        while self.is_paused and self.is_running:
                            time.sleep(0.1)
                        # Remove paused duration from 'virtual' start time
                        start_time += (time.time() - pause_start)
                        continue
                        
                    # Target Frame Calculation for Sync
                    now = time.time()
                    elapsed = now - start_time
                    expected_frames = int(elapsed * self.fps)
                    
                    # If we have already written enough frames for this timecode, assume we are "ahead" and wait
                    # But usually screen recording is slow, so we are "behind".
                    if frame_count > expected_frames:
                        # Sleep a tiny bit to limit cpu usage if we are super fast
                        time.sleep(0.005) 
                        continue
                    
                    # Capture Screen
                    img = sct.grab(capture_monitor)
                    frame = np.array(img)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                    
                    # No resize needed if mss gave us the right size, which it should.
                    # Just in case of some weird driver behavior, we check shape but hopefully skip resize.
                    if frame.shape[1] != width or frame.shape[0] != height:
                        frame = cv2.resize(frame, (width, height))
                    
                    # Draw Cursor
                    if self.cursor_enabled:
                        try:
                            # ... (Cursor logic same as before, omitted for brevity if using replace_file_content carefully)
                            cur_x, cur_y = pyautogui.position()
                            rel_x = cur_x - capture_monitor["left"]
                            rel_y = cur_y - capture_monitor["top"]
                            if 0 <= rel_x < width and 0 <= rel_y < height:
                                cv2.circle(frame, (rel_x, rel_y), 5, (0, 0, 255), 2)
                        except: pass
                            
                    # Draw Webcam Overlay
                    if cap_webcam:
                        try:
                            ret, web_frame = cap_webcam.read()
                            if ret:
                                # Resize webcam frame
                                target_w = width // 5
                                scale = target_w / web_frame.shape[1]
                                target_h = int(web_frame.shape[0] * scale)
                                web_frame = cv2.resize(web_frame, (target_w, target_h))
                                
                                padding = 20
                                y_offset = height - target_h - padding
                                x_offset = width - target_w - padding
                                
                                if y_offset >= 0 and x_offset >= 0:
                                    h_w, w_w = web_frame.shape[:2]
                                    if (y_offset + h_w) <= frame.shape[0] and (x_offset + w_w) <= frame.shape[1]:
                                         frame[y_offset:y_offset+h_w, x_offset:x_offset+w_w] = web_frame
                                         cv2.rectangle(frame, (x_offset, y_offset), (x_offset+w_w, y_offset+h_w), (255, 255, 255), 2)
                        except Exception as e_web:
                             pass

                    # Write Frame
                    # Logic: If we are behind by N frames, write this frame N times to catch up
                    # This ensures the video files duration matches Real Time exactly.
                    
                    frames_to_write = max(1, expected_frames - frame_count + 1)
                    
                    # Cap frames to write to avoid huge lag spike filling? 
                    # E.g. if system froze for 5s, we'd write 100 frames. That's actually desired for sync.
                    
                    for _ in range(frames_to_write):
                         out.write(frame)
                         frame_count += 1

                # Cleanup
                logging.info(f"Stopping recording. Total frames written: {frame_count}")
                try:
                    out.release()
                except: pass
                
                if cap_webcam:
                    try: cap_webcam.release()
                    except: pass
                    
        except Exception as e:
            logging.error(f"Video Recording Error: {e}", exc_info=True)
            self.error_occurred.emit(str(e))
            
    def stop(self):
        self.is_running = False
        # Do not wait() here to avoid blocking the main thread. 
        # The manager should listen to the 'finished' signal.

    def pause(self):
        self.is_paused = True
    
    def resume(self):
        self.is_paused = False
