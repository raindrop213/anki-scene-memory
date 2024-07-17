import MeCab

class MeCabConverter:
    def __init__(self, unidic_path):
        self.tagger = MeCab.Tagger(rf'-r nul -d {unidic_path}')

    def convert_to_hiragana(self, katakana):
        katakana_to_hiragana_map = {
            'ァ': 'ぁ', 'ア': 'あ', 'ィ': 'ぃ', 'イ': 'い', 'ゥ': 'ぅ', 'ウ': 'う', 'ェ': 'ぇ', 'エ': 'え', 'ォ': 'ぉ', 'オ': 'お',
            'カ': 'か', 'ガ': 'が', 'キ': 'き', 'ギ': 'ぎ', 'ク': 'く', 'グ': 'ぐ', 'ケ': 'け', 'ゲ': 'げ', 'コ': 'こ', 'ゴ': 'ご',
            'サ': 'さ', 'ザ': 'ざ', 'シ': 'し', 'ジ': 'じ', 'ス': 'す', 'ズ': 'ず', 'セ': 'せ', 'ゼ': 'ぜ', 'ソ': 'そ', 'ゾ': 'ぞ',
            'タ': 'た', 'ダ': 'だ', 'チ': 'ち', 'ヂ': 'ぢ', 'ッ': 'っ', 'ツ': 'つ', 'ヅ': 'づ', 'テ': 'て', 'デ': 'で', 'ト': 'と', 'ド': 'ど',
            'ナ': 'な', 'ニ': 'に', 'ヌ': 'ぬ', 'ネ': 'ね', 'ノ': 'の', 'ハ': 'は', 'バ': 'ば', 'パ': 'ぱ', 'ヒ': 'ひ', 'ビ': 'び', 'ピ': 'ぴ',
            'フ': 'ふ', 'ブ': 'ぶ', 'プ': 'ぷ', 'ヘ': 'へ', 'ベ': 'べ', 'ペ': 'ぺ', 'ホ': 'ほ', 'ボ': 'ぼ', 'ポ': 'ぽ',
            'マ': 'ま', 'ミ': 'み', 'ム': 'む', 'メ': 'め', 'モ': 'も', 'ャ': 'ゃ', 'ヤ': 'や', 'ュ': 'ゅ', 'ユ': 'ゆ', 'ョ': 'ょ', 'ヨ': 'よ',
            'ラ': 'ら', 'リ': 'り', 'ル': 'る', 'レ': 'れ', 'ロ': 'ろ', 'ヮ': 'ゎ', 'ワ': 'わ', 'ヰ': 'ゐ', 'ヱ': 'ゑ', 'ヲ': 'を', 'ン': 'ん',
            'ヴ': 'ゔ', 'ヵ': 'ゕ', 'ヶ': 'ゖ', 'ヽ': 'ゝ', 'ヾ': 'ゞ'
        }

        return ''.join(katakana_to_hiragana_map.get(char, char) for char in katakana)

    def get_mecab_result(self, parse_result):
        results = []
        for line in parse_result.split('\n'):
            if line and not line.startswith('EOS'):
                parts = line.split('\t')  # 两项，一个单词一个结果
                word = parts[0]
                details = parts[1].split(',')
                pos = details[0]  # 词性

                # print(len(details))  # 单词的分析项数
                if len(details) > 6:
                    if "-" in details[7]:
                        furigana = details[7].split("-")[1]
                    else:
                        furigana = self.convert_to_hiragana(details[6])  # 假名注音
                else:
                    furigana = word

                results.append({
                    "word": word,
                    "pos": pos,
                    "furigana": furigana
                })
        return results

    def process_text(self, text):
        parse_result = self.tagger.parse(text)
        return self.get_mecab_result(parse_result)

if __name__=='__main__':
    processor = MeCabConverter("./files/unidic-3.1.0/unidic")
    results = processor.process_text("pythonが大好きです")
    # results = processor.process_text("python")
    # results = processor.process_text("クラスメート")
    # results = processor.process_text("大好き")

    print(f'Results: {results}')
    for result in results:
        print(f'{result["word"]} 《{result["furigana"]}》 ({result["pos"]})')

