from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os

app = FastAPI()

# --- Config Gemini ---
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

appointments = []
conversations = {}

@app.post("/api/message")
async def message(req: Request):
    data = await req.json()
    user = data.get("username")
    msg = data.get("message")

    # Nếu là tin nhắn đầu tiên thì thêm prompt hướng dẫn
    if user not in conversations:
        conversations[user] = []

    conversations[user].append(f"Người dùng: {msg}")

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Gom toàn bộ lịch sử hội thoại thành 1 prompt
        prompt = (
            "Bạn là một trợ lý y tế hữu ích. "
            "Hãy trả lời ngắn gọn, chính xác và thân thiện.\n\n"
        )
        prompt += "\n".join(conversations[user])

        response = model.generate_content(prompt)

        reply = response.text
        conversations[user].append(f"Trợ lý: {reply}")
    except Exception as e:
        reply = f"Lỗi gọi Gemini API: {e}"

    return {"reply": reply}


@app.get("/api/appointments")
async def get_appts(user: str):
    user_appts = [a for a in appointments if a["user"] == user]
    return {"appointments": user_appts}


@app.post("/api/book")
async def book(req: Request):
    data = await req.json()
    appt = {
        "user": data["user"],
        "clinic": data["clinic"],
        "date": data["date"],
        "time": data["time"],
    }
    appointments.append(appt)
    return {"message": "Đặt lịch thành công", "appointment": appt}
