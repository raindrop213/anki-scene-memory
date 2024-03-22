import os
import json
import urllib.request
import base64
import time

class AnkiConnector:
    def __init__(self, config=None):
        # 加载配置
        if config is None:
            import yaml
            with open('e:/mypj/anki-scene-memory/config.yaml', 'r', encoding='utf-8') as file:
                self.config = yaml.safe_load(file)
        else:
            self.config = config # 使用传递的配置

        # 从YAML配置中提取值
        self.anki_api_url = self.config['anki']['anki_api_url']
        self.voice_exp = int(self.config['vits']['voice_exp'])
        self.voice_sen = int(self.config['vits']['voice_sen'])
        self.language = self.config['vits']['language']
        self.length = float(self.config['vits']['length'])

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

        # 生成音频/图片
        if not self.get_audio_file(expression, exp_path, voice=self.voice_exp):
            raise Exception("Failed to generate: audio-expression")
        
        if not self.get_audio_file(sentence, sen_path, voice=self.voice_sen):
            raise Exception("Failed to generate: audio-sentence")
        
        if not all(os.path.exists(path) for path in [image_path, exp_path, sen_path]):
            raise Exception("Failed to generate: image")
        
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

    def delete_note(self, note_id):
        """
        删除指定ID的卡片
        :param note_id: 要删除的卡片的ID
        :return: 删除操作的结果
        """
        try:
            result = self.invoke('deleteNotes', notes=[note_id])
            print(f'Deleted note with ID: {note_id}')
            return result
        except Exception as e:
            print(f'Failed to delete note with ID {note_id}: {e}')
            return None

if __name__ == '__main__':
    connector = AnkiConnector()
    note_id = connector.create_note(deckName="manga_test",
                                    modelName="manga",
                                    expression="連邦",
                                    sentence="まさか連邦の白い雌豹マリアナ・ルチアーノ様にお会い出来るとは",
                                    meaning="解释",
                                    image_path='cache/picture.jpg',
                                    exp_path='cache/audio-exp.mp3',
                                    sen_path='cache/audio-sen.mp3')
    connector.delete_note(note_id)
