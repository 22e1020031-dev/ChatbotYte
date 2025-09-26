from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
import os

app = FastAPI()

# Cho phép frontend gọi API từ bất kỳ domain nào
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lấy API key từ biến môi trường
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("❌ Chưa cấu hình GROQ_API_KEY trong biến môi trường")

# Khởi tạo client Groq
client = Groq(api_key=GROQ_API_KEY)

# Bộ nhớ lưu lịch hẹn & hội thoại
appointments = []
conversations = {}

@app.post("/api/message")
async def message(req: Request):
    data = await req.json()
    user = data.get("username")
    msg = data.get("message")

    # Nếu chưa có hội thoại thì tạo mới
    if user not in conversations:
        conversations[user] = [
            {"role": "system", "content": "Bạn là một trợ lí y tế hữu ích."}
        ]

    # Thêm tin nhắn của user vào hội thoại
    conversations[user].append({"role": "user", "content": msg})

    # Giữ lịch sử hội thoại ngắn gọn (40 message gần nhất)
    if len(conversations[user]) > 40:
        conversations[user] = conversations[user][-40:]

    try:
        # Gọi API Groq với model mới
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Model còn hoạt động
            messages=conversations[user],
            max_tokens=512
        )
        reply = response.choices[0].message.content

        # Thêm phản hồi của assistant vào hội thoại
        conversations[user].append({"role": "assistant", "content": reply})

    except Exception as e:
        reply = f"Lỗi gọi Groq API: {e}"

    return {"reply": reply}


@app.get("/api/appointments")
async def get_appts(user: str):
    """Trả về danh sách lịch hẹn của user"""
    user_appts = [a for a in appointments if a["user"] == user]
    return {"appointments": user_appts}


@app.post("/api/book")
async def book(req: Request):
    """API để đặt lịch khám"""
    data = await req.json()
    appt = {
        "user": data["user"],
        "clinic": data["clinic"],
        "date": data["date"],
        "time": data["time"],
    }
    appointments.append(appt)
    return {"message": "Đặt lịch thành công", "appointment": appt}
