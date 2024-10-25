from openai import OpenAI
from pathlib import Path
from voicevox_core import VoicevoxCore
import simpleaudio as sa
import io
import json
import wave

talk = True
TALK_ON = "talk on"
TALK_OFF = "talk off"

# コアファイルの設定
open_jtalk_dict_dir=Path("open_jtalk_dic_utf_8-1.11")
core = VoicevoxCore(open_jtalk_dict_dir=open_jtalk_dict_dir)

# ずんだもんの声ID
speaker_id = 3
# モデルデータの読み込み
if not core.is_model_loaded(speaker_id):
    core.load_model(speaker_id)

client = OpenAI(
    base_url = 'http://localhost:11434/v1',
    api_key='ollama',
)

# MODEL = "ELYZA-JP-8B:latest"
MODEL = "dsasai/llama3-elyza-jp-8b:latest"

# 保存するファイル名
history_file = "conversation_history.json"

# 履歴の読み込み
if Path(history_file).exists():
    with open(history_file, 'r') as file:
        messages = json.load(file)
else:
    messages = []

while True:
    role = "user"
    message = input("?")

    # トークモードの状態
    if message.strip().lower() in (TALK_OFF.lower(), TALK_ON.lower()):
        talk = message.strip().lower() == TALK_ON.lower()
        print(f"トークモードは{'オン' if talk else 'オフ'}です")
        continue # 次のループへ
    
    # ユーザーのメッセージを履歴に追加
    messages.append({"role": role, "content": message})
    
    # LLMへのリクエスト
    response = client.chat.completions.create(
        model = MODEL,
        messages = messages  # 全履歴を送信
        # messages=messages[-10:]  # 最新の10メッセージのみ送信
    )
    
    if talk:
        llm_response = response.choices[0].message.content
        messages.append({"role": "assistant", "content": llm_response})
    
        if talk:
            wave_bytes = core.tts(llm_response, speaker_id)

            # バイナリーデータをバイトストリームとして読み込む
            audio_stream = io.BytesIO(wave_bytes)
            # バイトストリームを再生可能なオブジェクトに変換
            wave_read = wave.open(audio_stream, 'rb')
            wave_obj = sa.WaveObject.from_wave_read(wave_read)
            
            # 再生
            play_obj = wave_obj.play()
            # play_obj.wait_done()  # 再生が完了するまで待機
        
        # 履歴の保存
        with open(history_file, 'w') as file:
            json.dump(messages, file, ensure_ascii=False, indent=4)
        
        #レスポンスを文字で表示
        print(llm_response)
