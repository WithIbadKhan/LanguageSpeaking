# from fastapi import HTTPException, APIRouter
# from bson import ObjectId
# from motor.motor_asyncio import AsyncIOMotorClient
# import os






# MONGO_URI = os.getenv('MONGO_URI')
# client = AsyncIOMotorClient(MONGO_URI)
# db = client['CEFRL']
# user_collection = db['users']
# conversations_collection = db['conversations']
# scores_collection = db['scores']
# display_app = APIRouter()
# @display_app.get("/users/{user_id}/messages")
# async def get_user_messages(user_id: str, session_id: str):
#     try:
#         # Convert user_id to ObjectId
#         user_object_id = ObjectId(user_id)
        
#         # Query the conversation collection to find conversations for the given user_id and session_id
#         conversation = await conversations_collection.find_one({
#             "user_id": user_object_id,
#             "session_id": session_id
#         })

#         if not conversation:
#             raise HTTPException(status_code=404, detail="No conversations found for the given user_id and session_id.")

#         # Extract messages
#         session = conversation.get("session", {})
#         messages = session.get("messages", [])

#         if not messages:
#             raise HTTPException(status_code=404, detail="No messages found in the conversation.")

#         return {"user_id": user_id, "session_id": session_id, "messages": messages}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")




from fastapi import HTTPException, APIRouter, Query
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URI = os.getenv('MONGO_URI')
client = AsyncIOMotorClient(MONGO_URI)
db = client['CEFRL']
user_collection = db['users']
conversations_collection = db['conversations']
scores_collection = db['scores']
display_app = APIRouter()

@display_app.get("/users/{user_id}/messages")
async def get_user_messages(user_id: str, session_id: str = Query(...)):
    try:
        # Convert user_id to ObjectId
        user_object_id = ObjectId(user_id)
        
        # Query the conversation collection to find conversations for the given user_id and session_id
        conversation = await conversations_collection.find_one({
            "user_id": user_object_id,
            "session_id": session_id
        })

        if not conversation:
            raise HTTPException(status_code=201, detail="No conversations found for the given user_id and session_id.")

        # Extract messages
        session = conversation.get("session", {})
        messages = session.get("messages", [])

        if not messages:
            raise HTTPException(status_code=404, detail="No messages found in the conversation.")

        return {"user_id": user_id, "session_id": session_id, "messages": messages}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
