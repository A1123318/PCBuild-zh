# backend/services/chat/genai_client.py
import os
from functools import lru_cache

from google import genai


@lru_cache(maxsize=1)
def get_genai_client() -> genai.Client:
    """
    取得 Gemini client（以快取避免每次 request 都初始化）。
    SDK 也支援從環境變數讀取 API key；此處保留你原本的 env key 相容性。
    """
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if api_key:
        return genai.Client(api_key=api_key)
    # 讓 SDK 自行嘗試從環境變數取得（或後續呼叫時報錯）
    return genai.Client()
