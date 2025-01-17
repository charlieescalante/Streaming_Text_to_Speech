import sounddevice as sd
import numpy as np
import queue
import threading

class AudioPlayer:
    def __init__(self):
        self.audio_queue = queue.Queue()
        self.sample_rate = 24000  # Match your desired audio playback rate
        self.stop_signal = threading.Event()
        self.playback_thread = threading.Thread(target=self.play_audio)
        self.playback_thread.start()

    def play_audio(self):
        while not self.stop_signal.is_set():
            try:
                audio_chunk = self.audio_queue.get(timeout=0.1)
                audio_array = np.frombuffer(audio_chunk, dtype=np.int16)
                sd.play(audio_array, samplerate=self.sample_rate)
                sd.wait()  # Wait for playback to finish
            except queue.Empty:
                continue

    def add_audio_chunk(self, chunk):
        self.audio_queue.put(chunk)

    def stop(self):
        self.stop_signal.set()
        self.playback_thread.join()
        sd.stop()
