import requests
import json
import base64
import re

def invoke(action, **params):
    request = {
        "action": action,
        "version": 6,
        "params": params
    }
    response = requests.post("http://localhost:8765", json=request)
    return response.json()

def get_audio_file(text, language="ja", voice="324", length="1.1"):
    url = f"http://127.0.0.1:23456/voice/vits?text={text}&id={voice}&format=mp3&lang={language}&length={length}"
    response = requests.get(url)
    if response.status_code == 200:
        audio_base64 = base64.b64encode(response.content).decode('utf-8')
        return audio_base64
    return None

def summarize_text(text, max_length=40):
    if len(text) > max_length:
        return text[:18] + "..." + text[-18:]
    return text

def extract_original_sentence(text):
    # 移除HTML标签
    no_html = re.sub(r'<[^>]+>', '', text)

    # 移除括号及其内容
    no_parentheses = re.sub(r'\[.*?\]', '', no_html)
    
    return no_parentheses

def process_deck(deck_name, text_tag, file_mp3, voice, overwrite=False):
    # 首先查询所有卡片
    card_ids = invoke("findCards", query=f"deck:{deck_name}")["result"]
    card_infos = invoke("cardsInfo", cards=card_ids)["result"]
    total_cards = len(card_infos)

    print(f"共找到 {total_cards} 张卡片，开始处理...")

    # 检查每张卡片是否需要更新
    for index, card_info in enumerate(card_infos, start=1):
        card_id = card_info["cardId"]
        text = extract_original_sentence(card_info["fields"][text_tag]["value"])
        audio_field = card_info["fields"][file_mp3]["value"]

        if not audio_field or overwrite:
            audio_base64 = get_audio_file(text, voice=voice)
            if audio_base64:
                file_name = f"{card_id}_{file_mp3}.mp3"  # 在文件名中加入字段名
                invoke("storeMediaFile", filename=file_name, data=audio_base64)

                updated_fields = {
                    file_mp3: f"[sound:{file_name}]"
                }
                invoke("updateNoteFields", note={
                    "id": card_info["note"],
                    "fields": updated_fields
                })
                update_status = f"更新成功：{summarize_text(text)}"
            else:
                update_status = "音频生成失败"
        else:
            update_status = "跳过"

        print(f"进度: {index}/{total_cards} (卡片ID: {card_id}) - {update_status}")

    print("所有卡片处理完毕。")

# 使用示例
process_deck("蓝宝书日语文法::蓝宝书文法N1", "句型", "句型发音", 342, overwrite=True)
process_deck("蓝宝书日语文法::蓝宝书文法N1", "日文", "例句发音", 342, overwrite=True)
# process_deck("蓝宝书文法N1", "日文", "例句发音", 324, overwrite=False)

# 324日语胡桃（高桥李依）；342日语雷电将军（泽城美雪）