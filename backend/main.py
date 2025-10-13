from google import genai

client = genai.Client()  # 自動讀取 GEMINI_API_KEY
resp = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="你好！有收到訊息就說你好，我是Gemini 2.5 flash! 用繁體中文回答!"
)
print(resp.text)
