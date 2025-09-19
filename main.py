from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os

app = FastAPI()

# Lấy API key từ Render Environmentd
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Cấu hình model Gemini
model = genai.GenerativeModel("gemini-1.5-flash")

appointments = []
conversations = {}

@app.post("/api/message")
async def message(req: Request):
    data = await req.json()
    user = data.get("username")
    msg = data.get("message")

    if user not in conversations:
        conversations[user] = []
        # thêm câu mở đầu để định hướng
        conversations[user].append(
            {"role": "user", "parts": "Bạn là một trợ lí y tế hữu ích, hãy trả lời tự nhiên và dễ hiểu."}
        )

    conversations[user].append({"role": "user", "parts": msg})

    try:
        response = model.generate_content(conversations[user])
        reply = response.text
        conversations[user].append({"role": "model", "parts": reply})
    except Exception as e:
        reply = f"Lỗi gọi Gemini API: {e}"

    return {"reply": reply}
