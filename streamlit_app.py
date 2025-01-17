import streamlit as st
import openai
import sounddevice as sd
import numpy as np
import queue
import threading
import re
import os

# Load OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_Key"]

# AudioPlayer class for audio playback
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

# StreamHandler for processing and managing text and audio streaming
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
            audio_chunks = self.generate_tts_audio(sentence)
            for chunk in audio_chunks:
                self.audio_player.add_audio_chunk(chunk)

    def generate_tts_audio(self, sentence):
        # Simulate TTS audio generation (replace this with OpenAI TTS API calls)
        # Example: streaming audio bytes for testing
        return [b'\x00' * 2400]  # Replace this with real audio chunk generation

# Main function for Streamlit app
def main():
    st.title("Streaming Text-to-Speech App")
    st.write("Enter text below, and it will be processed and read aloud in real-time.")
    
    input_text = st.text_area("Enter your prompt:", "Write about penguins.")
    generate_button = st.button("Generate and Stream")

    if generate_button:
        audio_player = AudioPlayer()
        try:
            stream_handler = StreamHandler(audio_player)
            
            # Simulated text streaming (replace with OpenAI API response streaming)
            generated_text = "Penguins are fascinating birds. They are flightless, adapted to life in water..."
            
            # Process and display text incrementally
            for char in generated_text:
                stream_handler.process_text_delta(char)
                st.write("".join(stream_handler.results), unsafe_allow_html=True)
            
            # Play audio for the generated text
            stream_handler.play_sentences()
        finally:
            audio_player.stop()

if __name__ == "__main__":
    main()
