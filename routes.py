from fastapi import APIRouter, HTTPException
from app.models import User, Message
from app.database import users_collection, messages_collection
from app.auth import hash_password, verify_password, create_token
from .websocket import get_online_users




router = APIRouter()
@router.get("/online-users")
def online():
    return {"online_users": get_online_users()}
@router.post("/register")
def register(user: User):
    if users_collection.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="User exists")

    users_collection.insert_one({
        "username": user.username,
        "password": hash_password(user.password)
    })
    return {"msg": "User created"}
@router.put("/mark-read/{sender}/{receiver}")
def mark_read(sender: str, receiver: str):
    messages_collection.update_many(
        {"sender": sender, "receiver": receiver, "read": False},
        {"$set": {"read": True}}
    )
    return {"msg": "Messages marked as read"}

@router.post("/login")
def login(user: User):
    db_user = users_collection.find_one({"username": user.username})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token({"sub": user.username})
    return {"token": token}

@router.get("/messages/{user1}/{user2}")
def get_messages(user1: str, user2: str):
    msgs = list(messages_collection.find({
        "$or": [
            {"sender": user1, "receiver": user2},
            {"sender": user2, "receiver": user1}
        ]
    }))

    # ✅ REMOVE _id from all messages
    for msg in msgs:
        msg.pop("_id", None)

    return msgs
