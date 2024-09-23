import json , os , requests, io
import base64
from dotenv import load_dotenv 
load_dotenv()
END_OF_MESSAGE_TOKEN = "."
VOICE_ID = "21m00Tcm4TlvDq8ikWAM"
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
import os , re
from dotenv import load_dotenv
load_dotenv()
from elevenlabs import Voice, VoiceSettings
from elevenlabs.client import ElevenLabs
# from .sp_char import special_char
client = ElevenLabs(
  api_key=ELEVENLABS_API_KEY,
)
async def text_to_speech(text : str , languageCode : str ):
    try:
        text = re.sub(r'[^A-Za-z0-9 ]+', ' ', text)
        audio = client.generate(
                text=text,
                model="eleven_turbo_v2_5",
                voice=Voice(
                    voice_id='cjVigY5qzO86Huf0OWal',

                    settings=VoiceSettings(stability=0.5, similarity_boost=0.8, style=0.0, use_speaker_boost=True)
                )
            )
            # print("audio   :  ",b"".join(audio))
        audio_bytes = b"".join(audio)  # Join the list of byte chunks into a single bytes object
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        print("data of voice in text to voice fun    :  ", type(audio_base64))
        return audio_base64

    except Exception as e:
        print("some error occur  :  ",e)
        return {"Error":"some errro in elevenlabs"}