


import openai
import json
import aiohttp
from fastapi import WebSocket
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from dotenv import load_dotenv
END_OF_MESSAGE_TOKEN = "."
from openai_code.memory_handling import memory
""" custom module"""
from tts.text_to_speach import text_to_speech
from tts.sp_char import special_char
from socket_manager.init_socket import ws_manager
from .prompt import SYSTEM_PROMPT , USER_PROMPT
# Load environment variables
load_dotenv(override=True)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = os.getenv('OPENAI_API_KEY')
MONGO_URI = os.getenv('MONGO_URI')
client = AsyncIOMotorClient(MONGO_URI)
db = client['CEFRL']
conversations_collection = db['conversations']
obj_memory = memory()
mmr_dict = {}
async def stream_response( prompt, message_id, conversation_id,userid,languageCode):
    mmr_dict = {}
    data = await obj_memory.get_history(userid)
    new_CONTEXT = SYSTEM_PROMPT.substitute(previous_conversation=data , languageCode = languageCode)
    user_prompt_new = USER_PROMPT.substitute(previous_conversation=data , input=prompt)
    mmr_dict['Human'] = prompt
    res = await obj_memory.add_to_memory(userid,mmr_dict)
    # print("add messages : ",  res)
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4-turbo",
        "messages": [
            {"role": "system", "content": new_CONTEXT},
            {"role": "user", "content": user_prompt_new}
        ],
        "stream": True
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            if response.status != 200:
                error_message = await response.text()
                print(f"Request error: {response.status}, {error_message}")
                await ws_manager.send_json_message({"message": "An error occurred while fetching the response from the AI.", "id": message_id},userid)
                return
            response_buffer = ""
            full_response = ""
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
                                full_response = full_response+" "+content
                                # print("response buffer  :  ", response_buffer)
                                await ws_manager.send_json_message({"message": content, "id": message_id},userid)
                                # if content in ['.', '?']:
                                if content in special_char:
                                    audio_base64 = await text_to_speech(response_buffer,languageCode)
                                    await ws_manager.send_json_message({"audio": audio_base64, "id": message_id,"text":response_buffer},userid)
                                    # Save ChatGPT response to conversation
                                    await conversations_collection.update_one(
                                        {"_id": ObjectId(conversation_id)},
                                        {"$push": {"session.messages": {"role": "assistant", "content": response_buffer.strip(),"audio":audio_base64}}}
                                    )
                                    response_buffer = ""
                    except json.JSONDecodeError as e:
                        print(f"JSON decode error in streaming: {e}")
            else:
                if response_buffer:
                    audio_base64 = await text_to_speech(response_buffer , languageCode )
                    await ws_manager.send_json_message({"audio": audio_base64, "id": message_id,"text":response_buffer},userid)
                    # Save the final ChatGPT response to conversation
                    await conversations_collection.update_one(
                        {"_id": ObjectId(conversation_id)},
                        {"$push": {"session.messages": {"role": "assistant", "content": response_buffer.strip(),"audio":audio_base64}}}
                    )
            mmr_dict ={}
            mmr_dict['response'] = full_response
            res = await obj_memory.add_to_memory(userid,mmr_dict)
            # print("add ai response to mmry   :  ",res)
            full_response = ""
    await ws_manager.send_json_message({"message": END_OF_MESSAGE_TOKEN, "id": message_id},userid)



