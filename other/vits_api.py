
import requests

def get_audio_file(text, language="ja", voice="324", length="1.1"):
    url = f"http://127.0.0.1:23456/voice/vits?text={text}&id={voice}&lang={language}&length={length}"
    response = requests.get(url)
    if response.status_code == 200:
        audio_base64 = response.content
        return audio_base64
    return None

if __name__ == "__main__":
    print(get_audio_file("こっ：これは戦闘領域外での奇襲及び拉致行為よっ立派な宇宙条約違反だわっ！！"))