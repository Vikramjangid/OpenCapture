from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QSlider, QFileDialog, QMessageBox, QStyle, QProgressDialog)
from PySide6.QtCore import Qt, QTimer, QUrl, QSize, Signal
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
import cv2
from PIL import Image
import os

class VideoEditorWindow(QMainWindow):
    def __init__(self, video_path, audio_path=None):
        super().__init__()
        self.setWindowTitle("Video Editor - OpenCapture")
        self.resize(800, 600)
        
        # Set Window Icon
        import os
        from PySide6.QtGui import QIcon
        possible_paths = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "icon.png")),
            "icon.png"
        ]
        for path in possible_paths:
            if os.path.exists(path):
                self.setWindowIcon(QIcon(path))
                break
        self.video_path = video_path
        self.audio_path = audio_path
        
        self.init_ui()
        self.setup_player()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Video Widget
        self.video_widget = QVideoWidget()
        layout.addWidget(self.video_widget, stretch=1)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.btn_play = QPushButton()
        self.btn_play.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.btn_play.clicked.connect(self.toggle_play)
        controls_layout.addWidget(self.btn_play)
        
        # Mute Button
        if self.audio_path:
            self.btn_mute = QPushButton()
            self.btn_mute.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
            self.btn_mute.clicked.connect(self.toggle_mute)
            controls_layout.addWidget(self.btn_mute)
            self.is_muted = False
        
        # Frame Stepping
        step_layout = QHBoxLayout()
        self.btn_prev_frame = QPushButton("<")
        self.btn_prev_frame.setObjectName("primaryInfo")
        self.btn_prev_frame.setToolTip("Previous Frame")
        self.btn_prev_frame.clicked.connect(lambda: self.step_frame(-1))
        step_layout.addWidget(self.btn_prev_frame)
        
        self.btn_next_frame = QPushButton(">")
        self.btn_next_frame.setObjectName("primaryInfo")
        self.btn_next_frame.setToolTip("Next Frame")
        self.btn_next_frame.clicked.connect(lambda: self.step_frame(1))
        step_layout.addWidget(self.btn_next_frame)

        
        controls_layout.addLayout(step_layout)
        
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self.set_position)
        controls_layout.addWidget(self.slider)
        
        self.lbl_duration = QLabel("00:00 / 00:00")
        controls_layout.addWidget(self.lbl_duration)
        
        layout.addLayout(controls_layout)
        
        # Editing Tools
        edit_layout = QHBoxLayout()
        
        self.btn_save_mp4 = QPushButton("Export MP4 + Audio")
        self.btn_save_mp4.setObjectName("primarySuccess")
        self.btn_save_mp4.setFixedHeight(40)
        self.btn_save_mp4.clicked.connect(self.save_as_mp4)
        edit_layout.addWidget(self.btn_save_mp4)
        
        self.btn_save_gif = QPushButton("Save as GIF")
        self.btn_save_gif.setObjectName("primaryInfo")
        self.btn_save_gif.setFixedHeight(40)
        self.btn_save_gif.clicked.connect(self.save_as_gif)
        edit_layout.addWidget(self.btn_save_gif)

        
        layout.addLayout(edit_layout)
        
        trim_layout = QHBoxLayout()
        self.btn_set_start = QPushButton("Set Start")
        self.btn_set_start.setObjectName("importantError")
        self.btn_set_start.setFixedHeight(40)
        self.btn_set_start.clicked.connect(self.set_start_trim)
        trim_layout.addWidget(self.btn_set_start)
        
        self.lbl_trim_start = QLabel("Start: 0s")
        self.lbl_trim_start.setObjectName("sectionHeader")
        trim_layout.addWidget(self.lbl_trim_start)
        
        self.btn_set_end = QPushButton("Set End")
        self.btn_set_end.setObjectName("importantError")
        self.btn_set_end.setFixedHeight(40)
        self.btn_set_end.clicked.connect(self.set_end_trim)
        trim_layout.addWidget(self.btn_set_end)

        self.lbl_trim_end = QLabel("End: Full")
        self.lbl_trim_end.setObjectName("sectionHeader")
        trim_layout.addWidget(self.lbl_trim_end)

        
        self.trim_start_ms = 0
        self.trim_end_ms = -1 # -1 means end
        
        layout.addLayout(trim_layout)

    def setup_player(self):
        # Video Player
        self.media_player = QMediaPlayer()
        # self.media_player.setAudioOutput(self.audio_output) # Video file has no audio usually in this setup
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.setSource(QUrl.fromLocalFile(self.video_path))
        
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)
        
        # Audio Player (if exists)
        self.media_player_audio = None
        if self.audio_path and os.path.exists(self.audio_path):
            self.media_player_audio = QMediaPlayer()
            self.audio_output = QAudioOutput()
            self.media_player_audio.setAudioOutput(self.audio_output)
            self.media_player_audio.setSource(QUrl.fromLocalFile(self.audio_path))
        
        # Auto play
        self.toggle_play()

    def toggle_play(self):
        if self.media_player.playbackState() == QMediaPlayer.PlayingState:
            self.media_player.pause()
            if self.media_player_audio: self.media_player_audio.pause()
            self.btn_play.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        else:
            self.media_player.play()
            if self.media_player_audio: self.media_player_audio.play()
            self.btn_play.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

    def toggle_mute(self):
        if not self.media_player_audio: return
        
        self.is_muted = not self.is_muted
        self.audio_output.setMuted(self.is_muted)
        
        if self.is_muted:
            self.btn_mute.setIcon(self.style().standardIcon(QStyle.SP_MediaVolumeMuted))
        else:
            self.btn_mute.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))

    def step_frame(self, direction):
        # 20 fps assumed or get from file
        step_ms = 50 
        new_pos = self.media_player.position() + (direction * step_ms)
        self.media_player.setPosition(max(0, new_pos))
        if self.media_player_audio:
             self.media_player_audio.setPosition(max(0, new_pos))

    def position_changed(self, position):
        self.slider.setValue(position)
        self.update_duration_label(position, self.media_player.duration())
        
        # Sync audio drift check (simple)
        if self.media_player_audio and self.media_player_audio.playbackState() == QMediaPlayer.PlayingState:
             diff = abs(self.media_player_audio.position() - position)
             if diff > 200: # 200ms drift
                 self.media_player_audio.setPosition(position)

    def duration_changed(self, duration):
        self.slider.setRange(0, duration)
        self.update_duration_label(0, duration)
        if self.trim_end_ms == -1:
             self.trim_end_ms = duration

    def set_position(self, position):
        self.media_player.setPosition(position)
        if self.media_player_audio:
            self.media_player_audio.setPosition(position)

    def update_duration_label(self, current, total):
        def fmt(ms):
            s = (ms // 1000) % 60
            m = (ms // 60000) % 60
            millis = ms % 1000
            return f"{m:02}:{s:02}:{millis:03}"
        self.lbl_duration.setText(f"{fmt(current)} / {fmt(total)}")

    def set_start_trim(self):
        self.trim_start_ms = self.media_player.position()
        self.lbl_trim_start.setText(f"Start: {self.trim_start_ms/1000:.1f}s")

    def set_end_trim(self):
        self.trim_end_ms = self.media_player.position()
        self.lbl_trim_end.setText(f"End: {self.trim_end_ms/1000:.1f}s")

    def save_as_gif(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save GIF", "", "GIF Files (*.gif)")
        if not path:
            return
            
        self.process_export(path, "gif")

    def save_as_mp4(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save MP4", "", "MP4 Files (*.mp4)")
        if not path:
            return
            
        self.process_export(path, "mp4")

    # Signals for thread communication
    export_progress = Signal(int)
    export_finished_signal = Signal(str, str) # status, message

    def process_export(self, output_path, fmt):
        # Create Progress Dialog
        self.progress_dialog = QProgressDialog("Exporting Video...", "Cancel", 0, 100, self)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setMinimumDuration(0)
        self.progress_dialog.setValue(0)
        
        # Connect signals
        self.export_progress.connect(self.progress_dialog.setValue)
        self.export_finished_signal.connect(self.on_export_finished)
        
        self.export_thread_running = True
        
        import threading
        t = threading.Thread(target=self._export_thread, args=(output_path, fmt))
        t.start()
        
    def on_export_finished(self, status, message):
        self.progress_dialog.close()
        self.setEnabled(True)
        if status == "success":
            QMessageBox.information(self, "Export Complete", message)
        else:
            QMessageBox.critical(self, "Export Failed", message)

    def _export_thread(self, output_path, fmt):
        try:
            print(f"Exporting to {output_path}...")
            cap = cv2.VideoCapture(self.video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps <= 0: fps = 20.0
            
            total_duration_ms = float(self.trim_end_ms)
            if total_duration_ms == -1:
                total_duration_ms = self.media_player.duration()
                
            start_frame = int(self.trim_start_ms / 1000 * fps)
            end_frame = int(total_duration_ms / 1000 * fps)
            total_frames_to_process = max(1, end_frame - start_frame)
            
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            frames = []
            audio_export_path = None
            
            if fmt == "mp4":
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
                
                # Handling Audio Slice separately
                if self.audio_path and os.path.exists(self.audio_path):
                    try:
                        import soundfile as sf
                        data, samplerate = sf.read(self.audio_path)
                        # Slice data
                        start_idx = int(self.trim_start_ms / 1000 * samplerate)
                        end_idx = int(total_duration_ms / 1000 * samplerate)
                        
                        if start_idx < len(data):
                             sliced_data = data[start_idx:end_idx] if end_idx > start_idx else data[start_idx:]
                             audio_export_path = output_path.replace(".mp4", "_audio.wav")
                             sf.write(audio_export_path, sliced_data, samplerate)
                             print(f"Exported trimmed audio to {audio_export_path}")
                    except Exception as e:
                        print(f"Audio export failed: {e}")
            
            curr = start_frame
            processed_count = 0
            
            while True:
                if self.progress_dialog.wasCanceled(): # Check cancellation
                     break
                     
                ret, frame = cap.read()
                if not ret or (end_frame > 0 and curr > end_frame):
                    break
                
                if fmt == "mp4":
                    out.write(frame)
                else:
                    # GIF
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frames.append(Image.fromarray(rgb_frame))
                
                curr += 1
                processed_count += 1
                
                # Emit progress
                progress = int((processed_count / total_frames_to_process) * 100)
                self.export_progress.emit(progress)
            
            cap.release()
            if fmt == "mp4":
                out.release()
            elif fmt == "gif" and frames:
                frames[0].save(output_path, save_all=True, append_images=frames[1:], duration=1000/fps, loop=0)
            
            # ATTEMPT MERGE IF FFMPEG EXISTS
            final_msg = f"Export finished.\nVideo: {output_path}"
            if fmt == "mp4" and audio_export_path:
                if self.check_ffmpeg():
                    merged_path = output_path.replace(".mp4", "_merged.mp4")
                    success = self.merge_audio_video(output_path, audio_export_path, merged_path)
                    if success:
                        # Replace original with merged? Or keep both?
                        # Let's replace to be "Single File" as requested
                        try:
                            os.remove(output_path)
                            os.remove(audio_export_path)
                            os.rename(merged_path, output_path)
                            final_msg = f"Export finished (Merged).\nFile: {output_path}"
                        except:
                            final_msg += f"\nMerged File: {merged_path}"
                else:
                    final_msg += "\n\nNote: Audio saved separately (_audio.wav). Install FFmpeg to merge automatically."

            self.export_finished_signal.emit("success", final_msg)
            
        except Exception as e:
            print(f"Export Error: {e}")
            self.export_finished_signal.emit("error", str(e))

    def check_ffmpeg(self):
        """Check if ffmpeg is in system path."""
        import shutil
        return shutil.which("ffmpeg") is not None

    def merge_audio_video(self, video_path, audio_path, output_path):
        import subprocess
        try:
            # -y overwrites output
            # -c:v copy -c:a aac copies video, encodes audio to aac
            cmd = [
                "ffmpeg", "-y",
                "-i", video_path,
                "-i", audio_path,
                "-c:v", "copy",
                "-c:a", "aac",
                "-strict", "experimental",
                output_path
            ]
            subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception as e:
            print(f"Merge Error: {e}")
            return False
            
    def closeEvent(self, event):
        self.media_player.stop()
        if self.media_player_audio:
            self.media_player_audio.stop()
        super().closeEvent(event)
