from module.mecab import MeCabConverter
processor = MeCabConverter()
results = processor.process_text("pythonが大好きです")
print(results) # [{'word': 'python', 'pos': '名詞', 'furigana': ''}, {'word': 'が', 'pos': '助詞', 'furigana': ''}, {'word': '大好き', 'pos': '形状詞', 'furigana': 'だいすき'}, {'word': 'です', 'pos': '助動詞', 'furigana': ''}]
