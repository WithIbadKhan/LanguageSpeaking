
#update analyze and cerf_ws
import asyncio
import openai

import json
import aiohttp
# from openai import AsyncOpenAI
import base64
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from pydantic_core import core_schema
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os
import io
from openai import OpenAIError
from bson import ObjectId
from typing import List, Optional, Annotated
from dotenv import load_dotenv
from pydub import AudioSegment
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import traceback

# Load environment variables
load_dotenv(override=True)
MONGO_URI = os.getenv('MONGO_URI')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
openai.api_key = os.getenv('OPENAI_API_KEY')
# Constants
END_OF_MESSAGE_TOKEN = "."
VOICE_ID = "21m00Tcm4TlvDq8ikWAM"
CONTEXT = "You are CEFRL, human assistant for language speaking. You act like a language teacher and should question the user to try to understand their level of speaking. Your answers should be limited to 1-2 short sentences."

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
client = AsyncIOMotorClient(MONGO_URI)
db = client['CEFRL']
user_collection = db['users']
conversations_collection = db['conversations']

scores_collection = db['scores']

# OpenAI client
# openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# Password hashing (still used in case needed for user operations)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema([
                    core_schema.str_schema(),
                    core_schema.no_info_plain_validator_function(cls.validate),
                ]),
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(str),
        )

PydanticObjectId = Annotated[PyObjectId, Field(default_factory=PyObjectId)]

# Pydantic models
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    # password: str
    language_interface: str
    language_test: str

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language_interface: Optional[str] = None
    language_test: Optional[str] = None

class User(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    language_interface: str
    language_test: str

    model_config = {
        "populate_by_name": True,
        "json_encoders": {ObjectId: str},
        "arbitrary_types_allowed": True,
    }

class Message(BaseModel):
    role: str
    content: str

class Session(BaseModel):
    messages: List[Message]

class ConversationCreate(BaseModel):
    user_id: PydanticObjectId
    session: Session

class Conversation(ConversationCreate):
    id: PydanticObjectId = Field(alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "populate_by_name": True,
        "json_encoders": {ObjectId: str},
        "arbitrary_types_allowed": True,
    }

class ScoreCreate(BaseModel):
    conversation_id: PydanticObjectId
    average_score: float
    fluency: float
    pronunciation: float
    listening: float

class Score(ScoreCreate):
    id: PydanticObjectId = Field(alias="_id")

    model_config = {
        "populate_by_name": True,
        "json_encoders": {ObjectId: str},
        "arbitrary_types_allowed": True,
    }
async def summarize_conversation(prompt: str) -> str:
    try:
        # Use the asynchronous OpenAI API method `acreate`
        print("test")
        response = await openai.ChatCompletion.acreate(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that summarizes and provides feedback."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        # Properly access the content from the response
        return response['choices'][0]['message']['content']
    except openai.error.OpenAIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
# User CRUD operations
@app.post("/register")
async def register(user: UserCreate):
    if await user_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=200, detail="Email already exists")
    
    # Create the user dictionary without the password
    user_dict = {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "language_interface": user.language_interface,
        "language_test": user.language_test,
        "created_at": datetime.utcnow()
    }
    
    # Insert the new user into the database
    result = await user_collection.insert_one(user_dict)
    user_id = result.inserted_id
    
    return {"detail": "User registered successfully", "user_id": str(user_id)}

@app.get("/users/{user_id}", response_model=User)
async def read_user(user_id: str):
    user = await user_collection.find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user)

@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: str, user: UserUpdate):
    update_data = {k: v for k, v in user.model_dump().items() if v is not None}
    if len(update_data) == 0:
        raise HTTPException(status_code=200, detail="No fields to update")
    result = await user_collection.update_one(
        {"_id": ObjectId(user_id)}, {"$set": update_data}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    updated_user = await user_collection.find_one({"_id": ObjectId(user_id)})
    return User(**updated_user)

@app.delete("/users/{user_id}")
async def delete_user(user_id: str):
    result = await user_collection.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User deleted successfully"}

# WebSocket endpoint
@app.websocket("/cefrl_ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    conversation_id = None
    try:
        while True:
            message = await websocket.receive_text()
            if not message:
                continue
            try:
                data = json.loads(message)
                user_input = data.get('message')
                message_id = data.get('id')
                user_id = data.get('user_id')
                session_id = data.get('session_id')
                print("userid",user_id)

                # Find or create the conversation based on user_id and session_id
                conversation = await conversations_collection.find_one({
                    "user_id": ObjectId(user_id),
                    "session.session_id": session_id
                })

                if conversation:
                    conversation_id = conversation["_id"]
                else:
                    # If no conversation exists, create a new one
                    conversation_create = {
                        "user_id": ObjectId(user_id),
                        "session": {
                            "session_id": session_id,
                            "messages": []
                        },
                        "created_at": datetime.utcnow()
                    }
                    result = await conversations_collection.insert_one(conversation_create)
                    conversation_id = result.inserted_id
                    print("conversation_id",conversation_id)
                # Store user message in conversation
                await conversations_collection.update_one(
                    {"_id": ObjectId(conversation_id)},
                    {"$push": {"session.messages": {"role": "user", "content": user_input}}}
                )

                if user_input.lower() == 'exit':
                    await websocket.send_text(json.dumps({"message": "Goodbye!"}))
                    break

                await stream_response(websocket, user_input, message_id, conversation_id)

            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                await websocket.send_text(json.dumps({"message": "Invalid message format. Please send a JSON object."}))
            except Exception as e:
                print(f"Error: {e}")
                await websocket.send_text(json.dumps({"message": "An error occurred while processing your message."}))
    except WebSocketDisconnect:
        print("Client disconnected.")
    except Exception as e:
        print(f"Unexpected error: {e}")

async def stream_response(websocket: WebSocket, prompt, message_id, conversation_id):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4-turbo",
        "messages": [
            {"role": "system", "content": CONTEXT},
            {"role": "user", "content": prompt}
        ],
        "stream": True
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            if response.status != 200:
                error_message = await response.text()
                print(f"Request error: {response.status}, {error_message}")
                await websocket.send_text(json.dumps({"message": "An error occurred while fetching the response from the AI.", "id": message_id}))
                return
            response_buffer = ""
            async for line in response.content:
                decoded_line = line.decode('utf-8').strip()
                if not decoded_line:
                    continue
                if decoded_line.startswith('data: '):
                    decoded_line = decoded_line[6:]
                    if decoded_line == '[DONE]':
                        break
                    try:
                        json_data = json.loads(decoded_line)
                        if 'choices' in json_data and len(json_data['choices']) > 0:
                            content = json_data['choices'][0]['delta'].get('content', '')
                            if content:
                                response_buffer += " " + content
                    
                                print("response buffer  :  ", response_buffer)
                                await websocket.send_text(json.dumps({"message": content, "id": message_id}))
                                if content in ['.', '!', '?']:
                                    audio_base64 = await text_to_speech(response_buffer)
                                    await websocket.send_text(json.dumps({"audio": audio_base64, "id": message_id}))
                                    # Save ChatGPT response to conversation
                                    await conversations_collection.update_one(
                                        {"_id": ObjectId(conversation_id)},
                                        {"$push": {"session.messages": {"role": "assistant", "content": response_buffer.strip()}}}
                                    )
                                    response_buffer = ""

                    except json.JSONDecodeError as e:
                        print(f"JSON decode error in streaming: {e}")
            else:
                if response_buffer:
                    audio_base64 = await text_to_speech(response_buffer)
                    await websocket.send_text(json.dumps({"audio": audio_base64, "id": message_id}))
                    # Save the final ChatGPT response to conversation
                    await conversations_collection.update_one(
                        {"_id": ObjectId(conversation_id)},
                        {"$push": {"session.messages": {"role": "assistant", "content": response_buffer.strip()}}}
                    )

    await websocket.send_text(json.dumps({"message": END_OF_MESSAGE_TOKEN, "id": message_id}))

async def text_to_speech(text):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream/with-timestamps"
    headers = {
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    response = requests.post(url, json=data, headers=headers, stream=True)
    if response.status_code != 200:
        print(f"Error encountered, status: {response.status_code}, content: {response.text}")
        return
    audio_bytes = b""
    for line in response.iter_lines():
        if line:
            json_string = line.decode("utf-8")
            response_dict = json.loads(json_string)
            audio_bytes_chunk = base64.b64decode(response_dict["audio_base64"])
            audio_bytes += audio_bytes_chunk
    audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
    wav_buffer = io.BytesIO()
    audio.export(wav_buffer, format="wav")
    wav_buffer.seek(0)
    audio_base64 = base64.b64encode(wav_buffer.read()).decode('utf-8')
    return audio_base64


@app.get("/analyze-conversation/")
async def analyze_conversation(user_id: str):
    try:
        # Your code logic here...
        # Convert user_id to ObjectId
        try:
            user_object_id = ObjectId(user_id)
        except Exception as e:
            raise HTTPException(status_code=200, detail=f"Invalid user_id format: {e}")

        # Query the conversation collection to find all messages for the given user_id
        conversation = await conversations_collection.find_one({
            "user_id": user_object_id
        })

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found.")

        # Extract messages from the session safely
        messages = conversation.get("session", {}).get("messages", [])
        if not messages:
            raise HTTPException(status_code=404, detail="No messages found in the conversation.")

        # Construct input content for analysis
        input_content = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        print("input", input_content)
        # Prepare the prompt for ChatGPT
        prompt = f"""{input_content}

You are an expert language coach. Your task is to analyze the conversation above between a language learner and an agent. Focus on identifying any areas where the user:
1. Used incorrect words.
2. Showed gaps in understanding.
3. Lacked fluency.

Provide constructive feedback on these points and offer practical tips to improve their language skills. If the conversation contains no meaningful content or text, assign a score of 0 for all categories and suggest that the user try again.

Output Format:
The response should be in JSON format:
{{
  "Summary": "Provide a concise summary of the conversation, including all feedback and improvement tips.",
  "Pronunciation": float,
  "Listening Comprehension": float,
  "Fluency": float,
  "Overall Score": "Grade (A1, A, B, C)"
}}

Scoring Guidelines:
- A1: 90-100%
- A: 75-89%
- B: 50-74%
- C: below 50%"""


        # Get response from ChatGPT
        response = await summarize_conversation(prompt)
        
        # Assuming response is returned as a JSON string, parse it into a dictionary
        json_response = json.loads(response)
        
        # Return the parsed JSON object
        return json_response
    except HTTPException as e:
        raise e  # Re-raise caught HTTP exceptions to return them to the client
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
    

@app.get("/users/{user_id}/messages")
async def get_user_messages(user_id: str):
    try:
        # Convert user_id to ObjectId
        try:
            user_object_id = ObjectId(user_id)
        except Exception as e:
            raise HTTPException(status_code=200, detail=f"Invalid user_id format: {e}")

        # Query the conversation collection to find all conversations for the given user_id
        conversations = await conversations_collection.find({"user_id": user_object_id}).to_list(length=None)

        if not conversations:
            raise HTTPException(status_code=404, detail="No conversations found for the given user_id.")

        # Extract all messages from all conversations
        all_messages = []
        for conversation in conversations:
            session = conversation.get("session", {})
            messages = session.get("messages", [])
            all_messages.extend(messages)

        if not all_messages:
            raise HTTPException(status_code=404, detail="No messages found in the conversations.")

        return {"user_id": user_id, "messages": all_messages}
    
    except HTTPException as e:
        raise e  # Re-raise caught HTTP exceptions to return them to the client
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
