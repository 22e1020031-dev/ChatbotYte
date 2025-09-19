from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import os
import google.generativeai as genai

# ====== Cấu hình Gemini ======
API_KEY = os.getenv("GEMINI_API_KEY")  # lấy từ biến môi trường trên Render
if not API_KEY:
    raise ValueError("Chưa cấu hình GEMINI_API_KEY trong Render")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# ====== Khởi tạo FastAPI ======
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # cho phép GitHub Pages gọi API
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

appointments = []
conversations = {}

# ====== API Chat ======
@app.post("/api/message")
async def message(req: Request):
    data = await req.json()
    user = data.get("username")
    msg = data.get("message")

    if not user or not msg:
        return {"reply": "Vui lòng nhập tên và tin nhắn."}

    if user not in conversations:
        # Không dùng role "system"
        conversations[user] = [
            {"role": "user", "content": "Bạn là một trợ lí y tế hữu ích, hãy hỗ trợ tôi."}
        ]

    conversations[user].append({"role": "user", "content": msg})

    try:
        history = [
            {"role": m["role"], "parts": [m["content"]]}
            for m in conversations[user]
        ]

        response = model.generate_content(history)
        reply = response.text
        conversations[user].append({"role": "model", "content": reply})
    except Exception as e:
        reply = f"Lỗi gọi Gemini API: {e}"

    return {"reply": reply}



# ====== API Lịch hẹn ======
@app.get("/api/appointments")
async def get_appts(user: str):
    user_appts = [a for a in appointments if a["user"] == user]
    return {"appointments": user_appts}


# ====== API Đặt lịch ======
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
