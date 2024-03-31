import io
import requests
import urllib.parse
import pygame

class VitsAPI:
    def __init__(self, config):
        self.config = config
        pygame.mixer.init() # Initialize the mixer module

    def play_audio(self, text):
        params = {
            'text': text,
            'id': self.config['vits']['gui_voice'],
            'lang': self.config['vits']['language'],
            'format': 'mp3',
            'length': self.config['vits']['gui_length']
        }
        url = f"http://127.0.0.1:23456/voice/vits?{urllib.parse.urlencode(params)}"
        # Request the audio file
        response = requests.get(url)
        if response.status_code == 200:
            # Use io.BytesIO to create a file-like object from the audio data
            audio_data = io.BytesIO(response.content)
            # Load this object like a file
            pygame.mixer.music.load(audio_data)
            pygame.mixer.music.play()
