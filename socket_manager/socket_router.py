


import openai
import json
import aiohttp
from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
import os
from bson import ObjectId
from dotenv import load_dotenv
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

from openai_code.conversation import stream_response
from tts.greeting import greeting_message
from tts.end_meeting import end_meeting_message
from socket_manager.init_socket import ws_manager
from openai_code.memory_handling import memory

load_dotenv(override=True)
MONGO_URI = os.getenv('MONGO_URI')
openai.api_key = os.getenv('OPENAI_API_KEY')

# Initialize MongoDB connection
client = AsyncIOMotorClient(MONGO_URI)
db = client['CEFRL']
conversations_collection = db['conversations']
result = db['results']

# Initialize FastAPI components
obj_memory1 = memory()
socket_app = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@socket_app.websocket("/ws/{userid}/{name}/{languageCode}")
async def websocket_endpoint(websocket: WebSocket, userid: str, name: str, languageCode: str):
    await ws_manager.connect(websocket, userid)
    res = await obj_memory1.add_new_session(userid)
    print(f"Session response for {userid}: {res}")
    await greeting_message(userid, name, languageCode)
    
    conversation_id = None

    try:
        while True:
            data = await websocket.receive_json()
            print("recieved data    :  ",type(data))
            if not data:
                continue

            try:
                user_input = data.get('message', None)
                message_id = data.get('id', None)
                user_id = data.get('user_id', None)
                session_id = data.get('session_id', None)
                voice = data.get('voice', None)
                print("input voice type  :  ",  type(voice))


                if not user_input or user_input.strip() == "":
                    continue

                print(f"User {user_id} sent message: {user_input} in session {session_id}")

                # Find or create the conversation based on user_id and session_id
                conversation = await conversations_collection.find_one({
                    "user_id": ObjectId(user_id),
                    "session_id": session_id
                })
                print("after find conversation collection ")

                if conversation:
                    conversation_id = conversation["_id"]
                else:
                    print(f"No conversation found for user {user_id} in session {session_id}. Creating new conversation.")
                    # Create a new conversation
                    conversation_create = {
                        "user_id": ObjectId(user_id),
                        "session_id": session_id,
                        "session": {
                            "messages": []
                        },
                        "created_at": datetime.utcnow()
                    }
                    res = await conversations_collection.insert_one(conversation_create)
                    print("after insert in  conversation collection ")
                    conversation_id = res.inserted_id
                    print(f"New conversation created with ID {conversation_id} for user {user_id}.")
                    result_data = { "user_id":user_id , "test_id":session_id ,"started_at":datetime.now()}
                    res = await result.insert_one(result_data)
                    print("after insert in  result  collection ")


                # Store user message in conversation using session_id
                await conversations_collection.update_one(
                    {"_id": ObjectId(conversation_id)},
                    {"$push": {"session.messages": {"role": "user", "content": user_input, "voice": voice}}}
                )
                print(f"Message stored for user {user_id} in conversation {conversation_id}")

                if user_input.lower() == 'exit':
                    await websocket.send_text(json.dumps({"message": "Goodbye!"}))
                    break

                # Handle AI response
                print("\n\n\n  going to response   : ")
                await stream_response(user_input, message_id, conversation_id, userid, languageCode)

            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                await ws_manager.send_json_message({"message": "Invalid message format. Please send a JSON object."}, userid)
            except Exception as e:
                print(f"Error: {e}")
                await ws_manager.send_json_message({"message": "An error occurred while processing your message."}, userid)

    except WebSocketDisconnect:
        print(f"User {userid} disconnected.")
        res = await obj_memory1.remove_session(userid)
        print(f"Session removed for {userid}: {res}")
        ws_manager.disconnect(userid)

    finally:
        res = await obj_memory1.remove_session(userid)
        print(f"Session removed for {userid} in finally block: {res}")
        ws_manager.disconnect(userid)

@socket_app.post("/meeting_end_msg/{userid}")
async def send_meeting_end_msg(userid: str):
    if userid:
        res = await end_meeting_message(userid)
        if res:
            return JSONResponse(content="End meeting message sent.", status_code=200)
        else:
            return JSONResponse(content="End meeting message not sent.", status_code=201)
    return JSONResponse(content="Empty user ID.", status_code=400)


#After transfer


# import openai
# import json
# import aiohttp
# from fastapi import WebSocket, WebSocketDisconnect, APIRouter
# from fastapi.responses import JSONResponse
# from passlib.context import CryptContext
# import os
# from bson import ObjectId
# from dotenv import load_dotenv
# from datetime import datetime
# from motor.motor_asyncio import AsyncIOMotorClient
# from openai_code.conversation import stream_response
# from tts.greeting import greeting_message
# from tts.end_meeting import end_meeting_message
# from socket_manager.init_socket import ws_manager
# from openai_code.memory_handling import memory
# import boto3
# from botocore.exceptions import NoCredentialsError

# # Load environment variables
# load_dotenv(override=True)
# MONGO_URI = os.getenv('MONGO_URI')
# openai.api_key = os.getenv('OPENAI_API_KEY')
# AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
# AWS_REGION = os.getenv('AWS_REGION')
# BUCKET_NAME = os.getenv('BUCKET_NAME')

# # Initialize MongoDB connection
# client = AsyncIOMotorClient(MONGO_URI)
# db = client['CEFRL']
# conversations_collection = db['conversations']

# # AWS S3 client setup
# s3_client = boto3.client(
#     's3',
#     aws_access_key_id=AWS_ACCESS_KEY_ID,
#     aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
#     region_name=AWS_REGION
# )

# # FastAPI components
# obj_memory1 = memory()
# socket_app = APIRouter()
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# # Function to upload base64 audio to S3 and return the URL
# def upload_base64_audio_to_s3(base64_string, file_extension, s3_file_name):
#     try:
#         if ',' in base64_string:
#             base64_string = base64_string.split(',')[1]
        
#         audio_data = base64.b64decode(base64_string)
        
#         response = s3_client.put_object(
#             Body=audio_data, 
#             Bucket=BUCKET_NAME, 
#             Key=f"{s3_file_name}.{file_extension}", 
#             ACL='public-read'
#         )
        
#         return f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_file_name}.{file_extension}"
    
#     except NoCredentialsError:
#         print("Credentials not available for AWS S3.")
#         return None
#     except Exception as e:
#         print(f"Error occurred during S3 upload: {str(e)}")
#         return None

# @socket_app.websocket("/ws/{userid}/{name}/{languageCode}")
# async def websocket_endpoint(websocket: WebSocket, userid: str, name: str, languageCode: str):
#     await ws_manager.connect(websocket, userid)
#     res = await obj_memory1.add_new_session(userid)
#     print(f"Session response for {userid}: {res}")
#     await greeting_message(userid, name, languageCode)
    
#     conversation_id = None

#     try:
#         while True:
#             data = await websocket.receive_json()
#             if not data:
#                 continue

#             try:
#                 user_input = data.get('message', None)
#                 message_id = data.get('id', None)
#                 user_id = data.get('user_id', None)
#                 session_id = data.get('session_id', None)
#                 voice_base64 = data.get('voice', None)
#                 print("Received voice data type: ", type(voice_base64))

#                 if not user_input or user_input.strip() == "":
#                     continue

#                 print(f"User {user_id} sent message: {user_input} in session {session_id}")

#                 # Find or create the conversation based on user_id and session_id
#                 conversation = await conversations_collection.find_one({
#                     "user_id": ObjectId(user_id),
#                     "session_id": session_id
#                 })

#                 if conversation:
#                     conversation_id = conversation["_id"]
#                 else:
#                     print(f"No conversation found for user {user_id} in session {session_id}. Creating new conversation.")
#                     # Create a new conversation
#                     conversation_create = {
#                         "user_id": ObjectId(user_id),
#                         "session_id": session_id,
#                         "session": {
#                             "messages": []
#                         },
#                         "created_at": datetime.utcnow()
#                     }
#                     result = await conversations_collection.insert_one(conversation_create)
#                     conversation_id = result.inserted_id
#                     print(f"New conversation created with ID {conversation_id} for user {user_id}.")

#                 # Upload voice to S3 and store URL in MongoDB
#                 if voice_base64:
#                     voice_s3_url = upload_base64_audio_to_s3(voice_base64, 'webm', f"{user_id}/voice_{session_id}")
#                     if voice_s3_url:
#                         print(f"Voice uploaded to S3: {voice_s3_url}")
#                     else:
#                         print("Failed to upload voice to S3")

#                 # Store user message in conversation
#                 await conversations_collection.update_one(
#                     {"_id": ObjectId(conversation_id)},
#                     {"$push": {"session.messages": {"role": "user", "content": user_input, "voice": voice_s3_url if voice_base64 else None}}}
#                 )
#                 print(f"Message stored for user {user_id} in conversation {conversation_id}")

#                 if user_input.lower() == 'exit':
#                     await websocket.send_text(json.dumps({"message": "Goodbye!"}))
#                     break

#                 # Handle AI response
#                 await stream_response(user_input, message_id, conversation_id, userid, languageCode)

#             except json.JSONDecodeError as e:
#                 print(f"JSON decode error: {e}")
#                 await ws_manager.send_json_message({"message": "Invalid message format. Please send a JSON object."}, userid)
#             except Exception as e:
#                 print(f"Error: {e}")
#                 await ws_manager.send_json_message({"message": "An error occurred while processing your message."}, userid)

#     except WebSocketDisconnect:
#         print(f"User {userid} disconnected.")
#         res = await obj_memory1.remove_session(userid)
#         print(f"Session removed for {userid}: {res}")
#         ws_manager.disconnect(userid)

#     finally:
#         res = await obj_memory1.remove_session(userid)
#         print(f"Session removed for {userid} in finally block: {res}")
#         ws_manager.disconnect(userid)

# @socket_app.post("/meeting_end_msg/{userid}")
# async def send_meeting_end_msg(userid: str):
#     if userid:
#         res = await end_meeting_message(userid)
#         if res:
#             return JSONResponse(content="End meeting message sent.", status_code=200)
#         else:
#             return JSONResponse(content="End meeting message not sent.", status_code=201)
#     return JSONResponse(content="Empty user ID.", status_code=400)
