from bson import ObjectId
from fastapi import HTTPException, APIRouter
from motor.motor_asyncio import AsyncIOMotorClient
import os



MONGO_URI = os.getenv('MONGO_URI')
client = AsyncIOMotorClient(MONGO_URI)
db = client['CEFRL']
conversations_collection = db['conversations']



show_text = APIRouter()
@show_text.get("/users/{user_id}/messages")
async def get_user_messages(user_id: str, session_id: str):
    try:
        # Convert user_id to ObjectId
        user_object_id = ObjectId(user_id)
        
        # Query the conversation collection to find conversations for the given user_id and session_id
        conversation = await conversations_collection.find_one({
            "user_id": user_object_id,
            "session_id": session_id
        })

        if not conversation:
            raise HTTPException(status_code=404, detail="No conversations found for the given user_id and session_id.")

        # Extract messages
        session = conversation.get("session", {})
        messages = session.get("messages", [])

        if not messages:
            raise HTTPException(status_code=404, detail="No messages found in the conversation.")

        return {"user_id": user_id, "session_id": session_id, "messages": messages}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")