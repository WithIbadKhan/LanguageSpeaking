import asyncio
import json
import aiohttp
import openai
import requests
import base64
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from pymongo import MongoClient
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, UploadFile, File
import jwt
import os
import io
from sp_char import special_char
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets
from dotenv import load_dotenv
from pydub import AudioSegment
import uuid

# Load environment variables
load_dotenv()

DG_API_KEY = os.getenv('DG_API_KEY')
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
MONGO_URI = os.getenv('MONGO_URI')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

END_OF_MESSAGE_TOKEN = "."
voice_id = "21m00Tcm4TlvDq8ikWAM"
context = "You are CEFRL, human assistant for language speaking. You act like a language teacher and should question the user to try to understand their level of speaking. Your answers should be limited to 1-2 short sentences."
# Set your secret keys and configuration settings
SECRET_KEY = secrets.token_hex(16)
JWT_SECRET_KEY = secrets.token_hex(16)
JWT_EXPIRATION_DELTA = timedelta(minutes=60)  # Set your desired expiration time
PERMANENT_SESSION_LIFETIME = timedelta(days=2)

# Initialize FastAPI app
app = FastAPI()


def summarize_conversation(prompt: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that summarizes and provides feedback."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = MongoClient(MONGO_URI)
db = client['chloe']
user_collection = db['users']
recovery_collection = db['recovery']

# Email configuration
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USERNAME = "technologiesoctaloop@gmail.com"
MAIL_PASSWORD = "vlrv oxym zzdv oavt"
MAIL_DEFAULT_SENDER = "Octaloop_Tech <technologiesoctaloop@gmail.com>"

# Ensure the file exists
if not os.path.exists('conversation_log.txt'):
    open('conversation_log.txt', 'w').close()

# Write input and output text to a file
def write_to_file(role, text):
    with open('conversation_log.txt', 'a') as file:
        file.write(f"{role}: {text}\n")

# Pydantic models
class User(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    language_interface: str
    language_test: str

class Login(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    token: str
    token_timestamp: datetime

class ForgotPassword(BaseModel):
    email: EmailStr

class Recovery(BaseModel):
    code: str

class ResetPassword(BaseModel):
    email: EmailStr
    code: str
    new_password: str
    confirm_password: str

# Helper functions
def generate_token(email: str) -> str:
    payload = {
        "email": email,
        "exp": datetime.utcnow() + JWT_EXPIRATION_DELTA
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")

def send_recovery_email(email: str, code: str):
    subject = 'Password Recovery Code'
    body = f'Your recovery code is: {code}'
    msg = MIMEMultipart()
    msg['From'] = MAIL_DEFAULT_SENDER
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    try:
        # Connect to SMTP server
        server = smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT) if MAIL_USE_SSL else smtplib.SMTP(MAIL_SERVER, MAIL_PORT)
        server.connect(MAIL_SERVER, MAIL_PORT)
        server.ehlo()
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        # Send email
        server.sendmail(MAIL_DEFAULT_SENDER, email, msg.as_string())
        server.quit()
        print(f"Email sent to {email} with recovery code.")
    except Exception as e:
        print(f"Error sending email: {e}")

def generate_recovery_code() -> str:
    return ''.join(random.choices(string.digits, k=4))

@app.post("/register")
async def register(user: User):
    if user_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=201, detail="Email already exists")
    user_id = str(uuid.uuid4())
    # Create a dictionary with the required fields
    user_dict = {
        "user_id": user_id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "language_interface": user.language_interface,
        "language_test": user.language_test
    }

    user_collection.insert_one(user_dict)
    return {"detail": "User registered successfully","user_id": user_id}

@app.post("/signup")
async def signup(user: User):
    if user_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=201, detail="Email already exists")
    hashed_password = CryptContext(schemes=["pbkdf2_sha256"]).hash(user.password)
    user_dict = user.dict()
    user_dict["password_hashed"] = hashed_password
    del user_dict["password"]  
    user_collection.insert_one(user_dict)
    return {"message": "User created successfully"}

@app.post("/login")
async def login(login_data: Login):
    user = user_collection.find_one({"email": login_data.email})
    if not user or not CryptContext(schemes=["pbkdf2_sha256"]).verify(login_data.password, user["password_hashed"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = generate_token(login_data.email)
    token_timestamp = datetime.utcnow() + timedelta(hours=24)
    user_collection.update_one({"_id": user["_id"]}, {"$set": {"token": token, "token_timestamp": token_timestamp}})
    return {"token": token, "token_timestamp": token_timestamp}

@app.post("/forgot_password")
async def forgot_password(forgot_password_data: ForgotPassword):
    user = user_collection.find_one({"email": forgot_password_data.email})
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")
    code = generate_recovery_code()
    recovery_data = {
        "user_id": user["_id"],
        "recovery_code": code,
        "timestamp": datetime.utcnow()
    }
    db.recovery.insert_one(recovery_data)
    send_recovery_email(forgot_password_data.email, code)
    return {"message": "Recovery code sent to your email"}

@app.post("/verify_recovery_code")
async def verify_recovery_code(recovery: Recovery):
    recovery_data = db.recovery.find_one({
        "recovery_code": recovery.code,
        "timestamp": {"$gte": datetime.utcnow() - timedelta(hours=1)}
    })
    if not recovery_data:
        raise HTTPException(status_code=201, detail="Invalid or expired recovery code")
    return {"message": "Recovery code verified successfully"}

@app.post("/reset_password")
async def reset_password(reset_password_data: ResetPassword):
    user = user_collection.find_one({"email": reset_password_data.email})
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")
    recovery_data = db.recovery.find_one({"recovery_code": reset_password_data.code})
    if not recovery_data:
        raise HTTPException(status_code=201, detail="Invalid or expired recovery code")
    expiration_time = recovery_data["timestamp"] + timedelta(minutes=5)
    if datetime.utcnow() > expiration_time:
        raise HTTPException(status_code=201, detail="Invalid or expired recovery code")
    if reset_password_data.new_password != reset_password_data.confirm_password:
        raise HTTPException(status_code=201, detail="New password and confirm password do not match")
    hashed_password = CryptContext(schemes=["pbkdf2_sha256"]).hash(reset_password_data.new_password)
    user_collection.update_one({"_id": user["_id"]}, {"$set": {"password_hashed": hashed_password}})
    db.recovery.delete_one({"_id": recovery_data["_id"]})
    return {"message": "Password successfully reset. You can now log in with your new password."}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_text()
            if not message:
                continue
            try:
                data = json.loads(message)
                user_input = data.get('message')
                message_id = data.get('id')
                write_to_file("User", user_input)  # Store user input
                if user_input.lower() == 'exit':
                    await websocket.send_text(json.dumps({"message": "Goodbye!"}))
                    break
                await stream_response(websocket, user_input, message_id)
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

async def stream_response(websocket: WebSocket, prompt, message_id):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4-turbo",
        "messages": [
            {"role": "system", "content": context},
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
                                await websocket.send_text(json.dumps({"message": content, "id": message_id}))
                                if content in special_char or response_buffer.count(" ") >= 10:
                                    audio_base64 = await text_to_speech(response_buffer)
                                    await websocket.send_text(json.dumps({"audio": audio_base64, "id": message_id}))
                                    write_to_file("Agent", response_buffer.strip())  # Store agent response
                                    response_buffer = ""
                    except json.JSONDecodeError as e:
                        print(f"JSON decode error in streaming: {e}")
            else:
                audio_base64 = await text_to_speech(response_buffer)
                await websocket.send_text(json.dumps({"audio": audio_base64, "id": message_id}))
                write_to_file("Agent", response_buffer.strip())  # Store agent response

    await websocket.send_text(json.dumps({"message": END_OF_MESSAGE_TOKEN, "id": message_id}))
    write_to_file("Agent", response_buffer.strip())  # Store agent response

async def text_to_speech(text):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream/with-timestamps"
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
@app.post("/analyze-conversation/")
async def analyze_conversation(file: UploadFile = File(...)):
    try:
        # Read content from the uploaded file
        content = await file.read()
        input_content = content.decode('utf-8')

        # Prepare the prompt
        prompt = f"""{input_content}\n\nYou are an expert language coach. 
            You will read and analyze a conversation between an agent and 
            a user from a provided text file. Your task is to identify 
            any areas where the user may have used incorrect words,
            had pronunciation issues, listening capability gaps, or lacked
            fluency. You will provide constructive feedback to the user on
            these points and give practical tips on how to improve their language skills based on the conversation."""

        # Get response from ChatGPT
        response = summarize_conversation(prompt)

        return {"feedback": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# Port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
