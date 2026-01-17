import sounddevice as sd
import soundfile as sf
import numpy as np
import threading
import logging
import time

class AudioRecorder(threading.Thread):
    def __init__(self, output_path, device=None, channels=1, samplerate=44100):
        super().__init__()
        self.output_path = output_path
        self.device = device
        self.channels = channels
        self.samplerate = samplerate
        self.is_running = False
        self.is_paused = False
        self.error = None
        
    def run(self):
        self.is_running = True
        try:
            with sf.SoundFile(self.output_path, mode='x', samplerate=self.samplerate,
                              channels=self.channels, subtype='PCM_16') as file:
                with sd.InputStream(samplerate=self.samplerate, device=self.device,
                                    channels=self.channels, callback=self.callback):
                    while self.is_running:
                        time.sleep(0.1)
                        # The callback handles the writing. 
                        # We just keep the stream alive here.
                        # Pausing logic would need to be handled in callback or by stopping stream.
                        
        except Exception as e:
            logging.error(f"Audio Recording Error: {e}", exc_info=True)
            self.error = str(e)
            
    def callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            logging.warning(f"Audio status: {status}")
        
        if not self.is_paused:
            # Append to file
            # Since we opened the file in the main run loop, we can't easily write to it from here safely 
            # if the file object isn't thread-safe or if we are in a different context.
            # However, sounddevice InputStreams allow using a queue to pass data to main thread.
            # OR we can write directly if we are careful. 
            # Actually, the common pattern is using a queue.
            pass

    # RE-IMPLEMENTATION using a Queue pattern for safety and simpler pausing
    
class AudioRecorderQueue(threading.Thread):
    def __init__(self, output_path, device=None, channels=1, samplerate=44100):
        super().__init__()
        self.output_path = output_path
        self.device = device
        self.channels = channels
        self.samplerate = samplerate
        self.is_running = False
        self.is_paused = False
        self._stop_event = threading.Event()
        
    def run(self):
        import queue
        q = queue.Queue()

        def callback(indata, frames, time, status):
            if status:
                logging.warning(f"Audio status: {status}")
            q.put(indata.copy())

        self.is_running = True
        try:
            with sf.SoundFile(self.output_path, mode='x', samplerate=self.samplerate,
                              channels=self.channels, subtype='PCM_16') as file:
                with sd.InputStream(samplerate=self.samplerate, device=self.device,
                                    channels=self.channels, callback=callback):
                    while self.is_running:
                        if self._stop_event.is_set():
                            break
                        
                        try:
                            # varying timeout to match block size approx
                            data = q.get(timeout=1) 
                        except queue.Empty:
                            continue
                            
                        if not self.is_paused:
                            file.write(data)
                            
        except Exception as e:
            logging.error(f"Audio Recording Error: {e}", exc_info=True)
            print(f"Audio Error: {e}")

    def stop(self):
        self.is_running = False
        self._stop_event.set()
        self.join()

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False
