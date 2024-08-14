"""
ツイスターのルーレットをずんだもんが回すのだ

"""

from pathlib import Path
from voicevox_core import VoicevoxCore
import simpleaudio as sa
import io
import time
import random

# コアファイルの設定
core = VoicevoxCore(open_jtalk_dict_dir=Path("open_jtalk_dic_utf_8-1.11"))

# ずんだもんの声ID
speaker_id = 3
# モデルデータの読み込み
if not core.is_model_loaded(speaker_id):
    core.load_model(speaker_id)

# 選択肢
colors = ["あかに", "あおに", "みどりに", "きいろに", "あげて"]
body_parts = ["右手を", "右足を", "左手を", "左足を"]

def twister():
    random_color = random.choice(colors)
    random_body_part = random.choice(body_parts)
    return  f"{random_body_part} ,{random_color}"

while True:
    # 音声データ生成
    wave_bytes = core.tts(twister(), speaker_id)
    audio_stream = io.BytesIO(wave_bytes)
    wave_obj = sa.WaveObject.from_wave_file(audio_stream)
    
    # 読み上げ
    play_obj = wave_obj.play()
    play_obj.wait_done()
    
    # 5秒待つ
    time.sleep(5)
