import io
import requests
import urllib.parse
import pygame
import threading

class VitsAPI:
    def __init__(self, config):
        self.config = config
        pygame.mixer.init() # Initialize the mixer module

    def play_audio(self, text):
        # 创建并启动一个线程来播放音频
        thread = threading.Thread(target=self._play_audio_thread, args=(text,))
        thread.start()

    def _play_audio_thread(self, text):
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
    
    def play_tips(self, tips_path):

        # 提示音
        pygame.mixer.music.load(tips_path)
        pygame.mixer.music.play()


