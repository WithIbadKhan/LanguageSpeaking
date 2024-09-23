from fastapi import  HTTPException ,APIRouter
# from socket_manager.socket_handler import languagetest

import os
import openai

openai.api_key = os.getenv('OPENAI_API_KEY')
async def summarize_conversation(prompt: str) -> str:
    try:
        # Use the asynchronous OpenAI API method `acreate`
        print("test")
        response = await openai.ChatCompletion.acreate(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that summarizes and provides feedback. You should give the output in json formate. And there should be you give value dont be give empty response in Grades"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
            # language = 'fr'
        )
        # Properly access the content from the response
        return response['choices'][0]['message']['content']
    except openai.error.OpenAIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
