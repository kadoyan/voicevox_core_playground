from openai import OpenAI
from pathlib import Path
from voicevox_core import VoicevoxCore
from json.decoder import JSONDecodeError
import json
import os
import random
import string
import shutil

def Conversation(talk: bool = True, speed: float = 1.0, input: str = ""):

    TALK_ON = "talk on"
    TALK_OFF = "talk off"

    # コアファイルの設定
    open_jtalk_dict_dir = Path("open_jtalk_dic_utf_8-1.11")
    core = VoicevoxCore(open_jtalk_dict_dir=open_jtalk_dict_dir)

    # 声ID
    speaker_id = 2
    # モデルデータの読み込み
    if not core.is_model_loaded(speaker_id):
        core.load_model(speaker_id)

    client = OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama",
    )

    MODEL = "nebel/fugaku-llm:13b-instruct"

    # 会話履歴を保存するファイル名
    history_file = "conversation_history.json"
    # 音声ファイルを保存するディレクトリ
    voice_path = "voice"
    # 音声ファイル名
    voice_file = ""

    # 履歴の読み込み
    if Path(history_file).exists():
        with open(history_file, "r") as file:
            # messages = json.load(file)
            try:
                messages = json.load(file)
            except JSONDecodeError:
                messages = []
    else:
        messages = []

    role = "user"
    message = input
    system_message = [
        {
            "role": "system",
            "content": "あなたは、20代の女性です。親しみやすい言葉遣いをします。長い返答や、回りくどい表現は使いません。",
        }
    ]

    # ユーザーのメッセージを履歴に追加
    messages.append({"role": role, "content": message})

    # LLMへのリクエスト
    merged = [*system_message, *messages]
    response = client.chat.completions.create(
        model=MODEL, messages=merged  # 全履歴を送信
    )

    if talk:
        shutil.rmtree(voice_path + "/")
        llm_response = response.choices[0].message.content
        messages.append({"role": "assistant", "content": llm_response})

        if talk:
            audio_query = core.audio_query(llm_response, speaker_id)
            audio_query.speed_scale = speed
            wave_bytes = core.synthesis(audio_query, speaker_id)
            # ファイルを保存
            voice_file = randomname(16) + ".wav"
            os.makedirs(voice_path, mode=0o755, exist_ok=True)
            with open(os.path.join(voice_path, voice_file), "wb") as f:
                f.write(wave_bytes)

        # 履歴の保存
        with open(history_file, "w") as file:
            json.dump(messages, file, ensure_ascii=False, indent=4)

        # レスポンス
        return {
            "messages": messages,
            "audio_path": os.path.join(voice_path, voice_file)
        }
        
def randomname(n):
   randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
   return ''.join(randlst)
