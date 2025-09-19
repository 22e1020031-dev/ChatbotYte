from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import os
import google.generativeai as genai

# ====== Cấu hình Gemini ======
API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyAWIZvCpHrKdPceh7mhtr13E4VHghbfgCQ")
genai.configure(api_key=API_KEY)

# Chọn model Gemini
model = genai.GenerativeModel("gemini-1.5-flash")

# ====== Khởi tạo FastAPI ======
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép frontend gọi từ bất kỳ domain nào
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Bộ nhớ hội thoại & lịch hẹn
appointments = []
conversations = {}

# ====== API chat ======
@app.post("/api/message")
async def message(req: Request):
    data = await req.json()
    user = data.get("username")
    msg = data.get("message")

    if not user or not msg:
        return {"reply": "Vui lòng nhập tên và tin nhắn."}

    # Nếu user chưa có hội thoại thì khởi tạo
    if user not in conversations:
        conversations[user] = [
            {"role": "system", "content": "Bạn là một trợ lí y tế hữu ích."}
        ]

    conversations[user].append({"role": "user", "content": msg})

    try:
        # Gửi lịch sử chat vào Gemini
        history = [
            {"role": m["role"], "parts": [m["content"]]}
            for m in conversations[user]
        ]

        response = model.generate_content(history)
        reply = response.text

        conversations[user].append({"role": "assistant", "content": reply})

    except Exception as e:
        reply = f"Lỗi gọi Gemini API: {e}"

    return {"reply": reply}

# ====== API lấy lịch hẹn ======
@app.get("/api/appointments")
async def get_appts(user: str):
    user_appts = [a for a in appointments if a["user"] == user]
    return {"appointments": user_appts}

# ====== API đặt lịch ======
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
