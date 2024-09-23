import random
import base64
from tts.text_to_speach import text_to_speech
from socket_manager.init_socket import ws_manager

async def end_meeting_message(userid):

    if userid:

        greeting_messages = [
            f"Hello {userid}, welcome to our conversation!",
            f"Hey {userid}, I'm excited to chat with you today!",
            f"Hello {userid}, it's awesome to have you here!",
            f"Hello {userid}, let's begin!",
            f"Hi {userid}, it's great to see you!",
            f"Hey {userid}, let's talk!",
            f"Greetings {userid}, ready to chat?",
            f"Welcome {userid}, let's get started!",
            f"Good day {userid}, let's talk!",
            f"Hi {userid}, excited to chat?",
            f"Hello {userid}, let's get started!",
            f"Hey {userid}, curious about what we'll discuss?",
            f"Welcome {userid}, let's chat!"
            ]
        text = random.choice(greeting_messages)
        audio_bytes = await text_to_speech(text)
        data = base64.b64encode(audio_bytes).decode('utf-8')
        greeting_data = {"event":"end_meeting","text":text ,"voice":data}
        await ws_manager.send_json_message(greeting_data,userid)
        greeting_data = {"event":"end_end_meeting" }
        await ws_manager.send_json_message(greeting_data,userid)
        return True
    




