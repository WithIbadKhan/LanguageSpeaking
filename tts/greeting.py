# #Greeting
# import random
# import base64
# from tts.text_to_speach import text_to_speech
# from socket_manager.init_socket import ws_manager


# async def greeting_message(userid , name, languageCode):

#     if name:
#         greeting_messages = [
#     f"Hello {name}, welcome! I’m here to assist you throughout this test.",
#     f"Hey {name}, glad to have you here! I’ll be guiding you through this test.",
#     f"Hello {name}, it’s awesome to have you here! Let’s begin the test.",
#     f"Hello {name}, welcome! I’m here to help you with this test.",
#     f"Hi {name}, it’s great to see you! I’ll be assisting you during this test.",
#     f"Hey {name}, welcome! I’m here to support you through this test.",
#     f"Greetings {name}, ready to start the test? I’m here to help!",
#     f"Welcome {name}, I’m here to assist you. Let’s get started with the test!",
#     f"Good day {name}, I’m here to guide you through this test. Let’s begin!",
#     f"Hi {name}, excited to start the test? I’m here to help you along the way!",
#     f"Hello {name}, welcome! Let’s get started with the test—I’m here to assist you!",
#     f"Hey {name}, curious about the test? I’m here to guide you through it!",
#     f"Welcome {name}, let’s start the test! I’m here to assist you every step of the way."
# ]

#         text = random.choice(greeting_messages)
#         print("chosen  :  ",text)
#         audio_bytes = await text_to_speech(text,languageCode)
#         print("after base64")

#         # data = base64.b64encode(audio_bytes).decode('utf-8')
#         print("after base64")
#         greeting_data = {"event":"greeting","text":text ,"audio":audio_bytes}
#         await ws_manager.send_json_message(greeting_data,userid)
#         greeting_data = {"event":"end_greeting" ,"respond_by":"lead"}
#         await ws_manager.send_json_message(greeting_data,userid)
#         return True

from tts.text_to_speach import text_to_speech
from socket_manager.init_socket import ws_manager

async def greeting_message(userid, name, languageCode):

    # Define greeting messages for English and French
    greeting_messages = {
        "en": f"Hello {name}! We are pleased to have you here.You are about to start a language test that will evaluate your listening, pronunciation, and fluency. Take your time and have a great time testing your skills! Are you ready to proceed?",
        "fr": f"Bonjour {name} ! Nous sommes ravis de vous accueillir ici. Vous êtes sur le point de commencer un test de langue qui évaluera votre écoute, votre prononciation et votre aisance. Prenez votre temps et passez un bon moment à tester vos compétences! Êtes-vous prêt à continuer ?"
    }

    # Choose the greeting message based on languageCode
    greeting_message = greeting_messages.get(languageCode, greeting_messages["en"]) 

    print("Chosen: ", greeting_message)

    # Generate audio bytes for the chosen greeting message
    audio_bytes = await text_to_speech(greeting_message, languageCode)
    print("After text-to-speech conversion")

    # Prepare the data to be sent over the WebSocket
    greeting_data = {"event": "greeting", "text": greeting_message, "audio": audio_bytes}
    await ws_manager.send_json_message(greeting_data, userid)

    # End greeting event
    end_greeting_data = {"event": "end_greeting", "respond_by": "lead"}
    await ws_manager.send_json_message(end_greeting_data, userid)

    return True
