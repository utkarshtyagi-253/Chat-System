from fastapi import WebSocket
from typing import Dict

# Using a single dictionary to track both connection and existence 
# is more efficient than maintaining a separate set for online_users.
connections: Dict[str, WebSocket] = {}

async def connect_user(user_id: str, websocket: WebSocket):
    user_id = user_id.lower().strip()
    await websocket.accept()
    connections[user_id] = websocket
    print(f"✅ Connected: {user_id}")

def get_online_users():
    # Simply return the keys from our active connections
    return list(connections.keys())

async def disconnect_user(user_id: str):
    user_id = user_id.lower().strip()
    # Using pop handles both removing the connection and the "online" status
    connections.pop(user_id, None)
    print(f"❌ Disconnected: {user_id}")

# Fixed typo: "aasync" -> "async"
async def send_message(receiver: str, message: dict):
    receiver = receiver.lower()

    # ✅ REMOVE MongoDB _id if present
    message.pop("_id", None)

    print("📩 Sending to:", receiver)
    print("👥 Connected users:", list(connections.keys()))

    if receiver in connections:
        await connections[receiver].send_json(message)
    else:
        print("❌ User not connected:", receiver)

    if receiver in connections:
        try:
            await connections[receiver].send_json(message)
        except Exception as e:
            print(f"⚠️ Failed to send to {receiver}: {e}")
            await disconnect_user(receiver)
    else:
        print(f"❌ User not connected: {receiver}")