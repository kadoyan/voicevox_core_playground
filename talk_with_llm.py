from openai import OpenAI
from pathlib import Path
from voicevox_core import VoicevoxCore
import simpleaudio as sa
import io

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
    api_key='ollama', # required, but unused
)

MODEL = "ELYZA-JP-8B:latest"

messages = []

while True:
    role = "user"
    message = input("?")
    
    # ユーザーのメッセージを履歴に追加
    messages.append({"role": role, "content": message})
    
    # LLMへのリクエスト
    response = client.chat.completions.create(
        model = MODEL,
        messages = messages  # 全履歴を送信
    )
    
    # LLMの応答を履歴に追加
    llm_response = response.choices[0].message.content
    messages.append({"role": "assistant", "content": llm_response})
    
    wave_bytes = core.tts(llm_response, speaker_id)

    # バイナリーデータをバイトストリームとして読み込む
    audio_stream = io.BytesIO(wave_bytes)
    # バイトストリームを再生可能なオブジェクトに変換
    wave_obj = sa.WaveObject.from_wave_file(audio_stream)

    # 再生
    print(llm_response)
    play_obj = wave_obj.play()
    play_obj.wait_done()  # 再生が完了するまで待機
