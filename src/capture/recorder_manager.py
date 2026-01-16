from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication
import os
import datetime
import logging
from capture.video import VideoRecorder
from capture.audio import AudioRecorderQueue
from ui.recording_controls import RecordingControls
from ui.countdown import CountdownOverlay

class RecorderManager(QObject):
    recording_finished = Signal(list) # Emits list of file paths created

    def __init__(self):
        super().__init__()
        self.video_recorder = None
        self.audio_recorder = None
        self.controls = None
        self.countdown = None # New attribute
        self.output_files = []

    def start_recording(self, region=None, monitor_index=None, 
                        input_mic=True, input_webcam=False, capture_cursor=True):
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.output_files = []
        
        save_dir = os.path.join(os.getcwd(), "captures")
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        video_filename = os.path.join(save_dir, f"video_{timestamp}.mp4")
        self.output_files.append(video_filename)
        
        # Determine FPS from system
        fps = 30.0
        try:
            screen = QApplication.primaryScreen()
            rate = screen.refreshRate()
            if rate > 0:
                fps = rate
        except:
             pass
             
        logging.info(f"Target Recording FPS: {fps}")
        
        # Start Video (First phase: Initialization)
        self.video_recorder = VideoRecorder(video_filename, region, monitor_index, 
                                            fps=fps,
                                            webcam_enabled=input_webcam, 
                                            cursor_enabled=capture_cursor)
        self.video_recorder.finished.connect(self._on_video_finished)
        
        # Start Audio
        if input_mic:
            audio_filename = os.path.join(save_dir, f"audio_{timestamp}.wav")
            self.output_files.append(audio_filename)
            # TODO: Add device selection logic if needed. For now default.
            self.audio_recorder = AudioRecorderQueue(audio_filename)
            
        # Connect setup ready signal
        if self.video_recorder:
            self.video_recorder.recording_started.connect(self._on_video_setup_ready)
            self.video_recorder.start() # This starts the video recorder thread, but not capture
        elif self.audio_recorder:
             # Audio only?
            self.audio_recorder.start()
            self._create_controls()

    def _on_video_setup_ready(self):
        """Called when video initialization (webcam etc) is done. Start Countdown."""
        self.countdown = CountdownOverlay()
        self.countdown.finished.connect(self._on_countdown_finished)
        self.countdown.start()
        
    def _on_countdown_finished(self):
        """Countdown done, actually start capturing."""
        if self.video_recorder:
            self.video_recorder.start_capture() # This starts the actual video capture
            
        if self.audio_recorder:
            self.audio_recorder.start() # This starts the audio capture
            
        # Update UI Controls
        self._create_controls()

    def _create_controls(self):
        if not self.controls:
            self.controls = RecordingControls()
            self.controls.pause_clicked.connect(self.toggle_pause)
            self.controls.stop_clicked.connect(self.stop_recording)
            self.controls.cancel_clicked.connect(self.cancel_recording)
        
        self.controls.show()

    def stop_recording(self):
        # Update UI to show processing immediately
        if self.controls:
            self.controls.show_processing()
            QApplication.processEvents() # Force UI update

        # Stop Audio
        if self.audio_recorder:
            self.audio_recorder.stop()

        # Stop Video Asynchronously
        if self.video_recorder:
            # Connect the finished signal to the final cleanup
            self.video_recorder.finished.connect(self._on_video_finished)
            self.video_recorder.stop()
        else:
            self._on_video_finished()

    def _on_video_finished(self):
        # Cleanup controls
        if self.controls:
            self.controls.close()
            
        self.recording_finished.emit(self.output_files)

    def toggle_pause(self, is_paused):
        if self.video_recorder:
            if is_paused:
                self.video_recorder.pause()
            else:
                self.video_recorder.resume()
                
        if self.audio_recorder:
            if is_paused:
                self.audio_recorder.pause()
            else:
                self.audio_recorder.resume()

    def cancel_recording(self):
        # Similar to stop but maybe delete files?
        self.stop_recording()
        # TODO: Delete files logic
