from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from .routes import router
from .websocket import connect_user, disconnect_user, send_message
from .database import messages_collection

import json
from datetime import datetime

app = FastAPI()

# ✅ CORS (important for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ include routes
app.include_router(router)


# ✅ Home route (optional)
@app.get("/")
def home():
    return {"message": "Chat backend is running 🚀"}


# ✅ WebSocket endpoint
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    user_id = user_id.lower()   # normalize
    await connect_user(user_id, websocket)

    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)

            print("📩 Received:", msg)

            # 🔥 Typing event
            if msg.get("type") == "typing":
                await send_message(msg["receiver"], msg)
                continue

            # ❌ Validate message
            if "sender" not in msg or "receiver" not in msg:
                print("❌ Invalid message:", msg)
                continue

            # ✅ Normalize usernames
            msg["sender"] = msg["sender"].lower()
            msg["receiver"] = msg["receiver"].lower()

            # ✅ Add metadata
            msg["timestamp"] = datetime.utcnow().isoformat()
            msg["read"] = False

            # ✅ Save to MongoDB
            try:
                messages_collection.insert_one(msg)
            except Exception as e:
                print("❌ DB Error:", e)

            # ✅ Send to receiver
            await send_message(msg["receiver"], msg)

    except Exception as e:
        print("❌ WebSocket crashed:", e)
        await disconnect_user(user_id)
