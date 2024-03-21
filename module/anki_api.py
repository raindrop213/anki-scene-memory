import os
import json
import urllib.request
import base64
import time
import configparser

class AnkiConnector:
    def __init__(self, config=None):
        if config is None:
            self.config = configparser.ConfigParser()
            self.config.read('../config.ini')  # 从文件加载配置
        else:
            self.config = config  # 使用传递的配置

        self.anki_api_url = self.config.get('anki', 'anki_api_url')
        self.anki_api_url = self.config.get('anki', 'anki_api_url')

        self.voice_exp = self.config.get('vits', 'voice_exp')
        self.voice_sen = self.config.get('vits', 'voice_sen')
        self.language = self.config.get('vits', 'language')
        self.length = self.config.get('vits', 'length')

    def encode_to_base64(self, content):
        encoded_content = base64.b64encode(content)
        return encoded_content.decode('utf-8')

    def get_audio_file(self, text, path, voice):
        params = urllib.parse.urlencode({'text': text, 'id': voice, 'lang': self.language, 'format': 'mp3', 'length': self.length})
        url = f"http://127.0.0.1:23456/voice/vits?{params}"
        request = urllib.request.Request(url)
        with urllib.request.urlopen(request) as response:
            if response.status == 200:
                audio_content = response.read()
                with open(path, 'wb') as audio_file:
                    audio_file.write(audio_content)
                    return path
        return None

    def request(self, action, **params):
        return {'action': action, 'params': params, 'version': 6}

    def invoke(self, action, **params):
        request_json = json.dumps(self.request(action, **params)).encode('utf-8')
        with urllib.request.urlopen(urllib.request.Request(self.anki_api_url, request_json)) as response:
            result = json.load(response)
            if 'error' not in result or result['error'] is not None:
                raise Exception('Failed to invoke action {}: {}'.format(action, result.get('error')))
            return result['result']

    def create_note(self, deckName, modelName, expression, sentence, meaning, image_path, exp_path, sen_path):

        # 生成音频
        self.get_audio_file(expression, exp_path, voice=self.voice_exp)
        self.get_audio_file(sentence, sen_path, voice=self.voice_sen)

        if not all(os.path.exists(path) for path in [image_path, exp_path, sen_path]):
            raise FileNotFoundError("One or more media files do not exist.")
        
        timestamp = str(int(time.time() * 1000))  # 转换时间戳到毫秒

        image_file_name = f'_{timestamp}_{image_path.split("/")[-1]}'
        audio_exp_file_name = f'_{timestamp}_{exp_path.split("/")[-1]}'
        audio_sen_file_name = f'_{timestamp}_{sen_path.split("/")[-1]}'

        note_id = self.invoke('addNote', note={
            "deckName": deckName,
            "modelName": modelName,
            "fields": {
                "expression": expression,
                "image": f'<img src="{image_file_name}">',
                "sentence": sentence,
                "meaning": meaning,
                "audio-exp": f'[sound:{audio_exp_file_name}]',
                "audio-sen": f'[sound:{audio_sen_file_name}]'
            },
            "options": {
                "allowDuplicate": False
            },
            "tags": ["RD213_manga"]
        })

        self.invoke('storeMediaFile', filename=image_file_name, path=os.path.abspath(image_path))
        self.invoke('storeMediaFile', filename=audio_exp_file_name, path=os.path.abspath(exp_path))
        self.invoke('storeMediaFile', filename=audio_sen_file_name, path=os.path.abspath(sen_path))
        
        print('Created note with ID:', note_id)
        return note_id

if __name__ == '__main__':
    connector = AnkiConnector()
    note_id = connector.create_note(deckName="HT",
                                    modelName="manga",
                                    expression="連邦",
                                    sentence="まさか連邦の白い雌豹マリアナ・ルチアーノ様にお会い出来るとは",
                                    meaning="解释",
                                    image_path='cache/picture.jpg',
                                    exp_path='cache/audio-exp.mp3',
                                    sen_path='cache/audio-sen.mp3')

