import streamlit as st
import openai
import threading
import queue
import pyaudio
import re
import os
from streamlit.runtime.scriptrunner import RerunException

# Load OpenAI API key
openai.api_key = st.secrets["OPENAI_API_Key"]

# Initialize PyAudio
class AudioPlayer:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paInt16, channels=1, rate=24000, output=True
        )
        self.audio_queue = queue.Queue()
        self.playback_thread = threading.Thread(target=self.play_audio)
        self.stop_signal = threading.Event()
        self.playback_thread.start()

    def play_audio(self):
        while not self.stop_signal.is_set():
            try:
                audio_chunk = self.audio_queue.get(timeout=0.1)
                self.stream.write(audio_chunk)
            except queue.Empty:
                continue

    def add_audio_chunk(self, chunk):
        self.audio_queue.put(chunk)

    def stop(self):
        self.stop_signal.set()
        self.playback_thread.join()
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

# Generate and play text with TTS
class StreamHandler:
    def __init__(self, audio_player):
        self.text_buffer = ""
        self.sentence_queue = queue.Queue()
        self.results = []
        self.audio_player = audio_player

    def process_text_delta(self, text):
        self.results.append(text)
        self.text_buffer += text
        self.extract_sentences()

    def extract_sentences(self):
        sentences = re.findall(r'[^.!?]+[.!?]', self.text_buffer)
        for sentence in sentences:
            self.sentence_queue.put(sentence.strip())
        self.text_buffer = re.sub(r'.*[.!?]', '', self.text_buffer)

    def play_sentences(self):
        while not self.sentence_queue.empty():
            sentence = self.sentence_queue.get()
            # Replace this TTS stub with your actual OpenAI API call for speech synthesis
            audio_chunks = generate_tts_audio(sentence)
            for chunk in audio_chunks:
                self.audio_player.add_audio_chunk(chunk)

def generate_tts_audio(sentence):
    # Stub for generating TTS audio, replace with OpenAI TTS call
    # Here, it would interact with OpenAI's TTS model
    return [b'\x00' * 2400]  # Replace this with real audio chunk generation logic

def main():
    st.title("Text Generation and TTS Streaming")
    input_text = st.text_area("Enter your prompt:", "Write about penguins.")
    if st.button("Generate"):
        audio_player = AudioPlayer()
        try:
            stream_handler = StreamHandler(audio_player)
            # Simulated text streaming; replace with OpenAI API stream
            generated_text = "Penguins are fascinating birds. They are flightless, adapted to life in water..."
            for char in generated_text:
                stream_handler.process_text_delta(char)
                st.write("".join(stream_handler.results), unsafe_allow_html=True)
                st.experimental_rerun()
            stream_handler.play_sentences()
        finally:
            audio_player.stop()

if __name__ == "__main__":
    main()
