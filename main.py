'''
ローカルLLM会話API

1. FastAPI、Uvicornをインストール
https://fastapi.tiangolo.com/ja/#_3

2. Uvicornを実行
uvicorn main:app --reload
'''

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse
from pydantic import BaseModel
from json.decoder import JSONDecodeError
import json

from conversation import Conversation

history_file = "conversation_history.json"
    
class ConversationRequest(BaseModel):
    text: str | None = None  # 3.10 以降の "Union" 省略記法
    
class resetRequest(BaseModel):
    agreement: bool

app = FastAPI()

origins = [
    "http://localhost:5174"
]

# Cross-Origin Resource Sharingを許可
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def main():
    return {"message": "Hello World"}

# LLMにテキストをポストして返答する
def SendToLLM(text: str) -> str:
    result = Conversation(True, 1, text)
    return result

@app.post("/post")
async def conversation_endpoint(req: ConversationRequest):
    # run_in_threadpool で別スレッドにして実行
    result = await run_in_threadpool(SendToLLM, req.text)
    return result

# 会話履歴を取得する
@app.get("/history")
async def main():
    with open(history_file, "r", encoding="utf-8") as f:
        try:
            messages = json.load(f)
            return messages
        except JSONDecodeError:
            return []

# 会話履歴を削除する
class resetHistory(BaseModel):
    agreement:str
    
@app.post("/reset")
async def reset_history(request: resetRequest):
    if request.agreement:
        try:
            with open(history_file, "w") as f:
                f.write("")
            return {"status": "OK"}
        except IOError as e:
            return {"status": "error", "detail": str(e)}
    return {"status": "NO"}

# 音声を取得する
@app.get("/voice/{filename}")
def download_file(filename: str):
    file_path = f"./voice/{filename}"
    return FileResponse(path=file_path, media_type='application/octet-stream', filename=filename)
