
# import openai
# import json
# from fastapi import HTTPException, APIRouter
# from motor.motor_asyncio import AsyncIOMotorClient
# import os
# from bson import ObjectId
# from .summerize import summarize_conversation
# OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
# openai.api_key = os.getenv('OPENAI_API_KEY')
# END_OF_MESSAGE_TOKEN = "."
# VOICE_ID = "21m00Tcm4TlvDq8ikWAM"

# # Initialize FastAPI app
# openai_analyze = APIRouter()
 

# # MongoDB connection
# MONGO_URI = os.getenv('MONGO_URI')
# client = AsyncIOMotorClient(MONGO_URI)
# db = client['CEFRL']
# user_collection = db['users']
# conversations_collection = db['conversations']
# scores_collection = db['scores']


# @openai_analyze.get("/analyze-conversation/")
# async def analyze_conversation(user_id: str, session_id: str):
#     try:
#         # Convert user_id to ObjectId
#         try:
#             user_object_id = ObjectId(user_id)
#         except Exception as e:
#             raise HTTPException(status_code=400, detail=f"Invalid user_id format: {e}")

#         # Query the conversation collection to find the conversation for the given user_id and session_id
#         conversation = await conversations_collection.find_one({
#             "user_id": user_object_id,
#             "session_id": session_id
#         })

#         if not conversation:
#             raise HTTPException(status_code=404, detail="Conversation not found for the given session_id.")

#         # Extract messages from the session safely
#         messages = conversation.get("session", {}).get("messages", [])
#         if not messages:
#             raise HTTPException(status_code=404, detail="No messages found in the conversation.")

#         # Construct input content for analysis
#         input_content = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
#         print("input", input_content)

#         # Prepare the prompt for ChatGPT
#         prompt = f"""{input_content}

# You are an expert language coach. Your task is to carefully analyze the following two-sided conversation text between a language learner and an agent. The conversation lasts 3 minutes, with the learner speaking for approximately 2 minutes. Evaluate the conversation based on three critical aspects: Fluency, Listening Comprehension, and Pronunciation. Use the criteria below to guide your analysis:

# Fluency:

# Words Per Minute (WPM): Calculate the learner's speaking speed by counting the total number of words spoken in the 120 seconds allocated. Typical conversational speech is between 120-150 WPM.
# Hesitations and Fillers: Identify and count any unnecessary pauses or filler words like 'um' or 'uh'.
# Coherence: Assess the logical flow of the dialogue and whether the learner maintains a consistent topic without abrupt changes.
# Listening Comprehension:

# Response Accuracy: Evaluate how accurately and appropriately the learner responds to the agent's questions or statements, focusing on relevance and correctness.
# Detail Retention: Assess the learner’s ability to recall and address details mentioned in the conversation.
# Inference: Judge whether the learner can make appropriate inferences from the context and respond suitably.
# Pronunciation:

# Phoneme Accuracy: Check the precision of the learner’s articulation of sounds, noting any unrelated or incorrectly pronounced words.
# Intonation and Stress Patterns: Evaluate the naturalness of the learner's intonation and the accuracy of stress patterns.
# Understandability: Determine how understandable the learner’s speech would be to a native speaker.

#  Your task is to analyze the conversation above between a language learner and an agent. Focus on identifying any areas where the user:
# 1. Used incorrect words.
# 2. Showed gaps in understanding.
# 3. Lacked fluency.

# Provide constructive feedback on these points and offer practical tips to improve their language skills. If the conversation contains no meaningful content or text, assign a score of 0 for all categories and suggest that the user try again. But remember, don't give 0 marks; the minimum score should be 40.

# Output Format:
# {{
#   "Summary": "Provide a concise summary of the conversation, including all feedback and improvement tips.",
#   "Pronunciation": float,
#   "Listening Comprehension": float,
#   "Fluency": float,
#   "Overall Score": "Grade (A1, A, B, C)"
# }}

# Scoring Guidelines:
# - A1: 90-100%
# - A: 75-89%
# - B: 50-74%
# - C: below 50%"""

#         # Get response from ChatGPT
#         response = await summarize_conversation(prompt)
        
#         # Assuming response is returned as a JSON string, parse it into a dictionary
#         json_response = json.loads(response)
        
#         # Return the parsed JSON object
#         return json_response

#     except HTTPException as e:
#         raise e  # Re-raise caught HTTP exceptions to return them to the client
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
    


#_______________________Working fine 




# import openai
# import json
# from datetime import datetime 
# from fastapi import HTTPException, APIRouter
# from motor.motor_asyncio import AsyncIOMotorClient
# import os
# from bson import ObjectId
# from .summerize import summarize_conversation
# import sendgrid
# from sendgrid.helpers.mail import Mail, Email, To, Content
# import logging

# # Setup logging
# logging.basicConfig(level=logging.INFO)

# # Set API keys from environment variables
# OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
# openai.api_key = OPENAI_API_KEY
# SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')

# # Initialize FastAPI router
# openai_analyze = APIRouter()

# # MongoDB connection
# MONGO_URI = os.getenv('MONGO_URI')
# client = AsyncIOMotorClient(MONGO_URI)
# db = client['CEFRL']
# user_collection = db['users']
# conversations_collection = db['conversations']
# summaries_collection = db['summaries']  # A new collection to store summaries

# # Function to send summary email
# def send_summary_email(email: str, summary: str):
#     sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
#     from_email = Email("ibadk6057@gmail.com")  # Replace with your email
#     to_email = To(email)
#     subject = "Your Conversation Summary and Feedback"
    
#     # Create the email content
#     html_content = f"""
#     <html>
#     <body>
#         <h1>Your Conversation Summary and Feedback</h1>
#         <p>{summary}</p>
#         <p>We hope this feedback helps you improve your language skills. Keep practicing!</p>
#         <p>Best regards,<br>The CEFRL Team</p>
#     </body>
#     </html>
#     """
    
#     content = Content("text/html", html_content)
#     mail = Mail(from_email, to_email, subject, content)
    
#     try:
#         response = sg.send(mail)
#         logging.info(f"Summary email sent successfully to {email}. Status Code: {response.status_code}")
#     except Exception as e:
#         logging.error(f"Failed to send summary email to {email}: {e}")

# @openai_analyze.get("/analyze-conversation/")
# async def analyze_conversation(user_id: str, session_id: str):
#     try:
#         # Convert user_id to ObjectId
#         user_object_id = ObjectId(user_id)

#         # Query the conversation collection to find the conversation for the given user_id and session_id
#         conversation = await conversations_collection.find_one({
#             "user_id": user_object_id,
#             "session_id": session_id
#         })

#         if not conversation:
#             raise HTTPException(status_code=404, detail="Conversation not found for the given session_id.")

#         # Extract messages from the session safely
#         messages = conversation.get("session", {}).get("messages", [])
#         if not messages:
#             raise HTTPException(status_code=404, detail="No messages found in the conversation.")

#         # Construct input content for analysis
#         input_content = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])

#         # Prepare the prompt for ChatGPT
#         prompt = f"""{input_content}
# You are an expert language coach. Your task is to analyze a conversation between a language learner and another participant. Based on the learner's performance, evaluate their language skills according to five key factors: Listening, Pronunciation, Fluency, Spoken Production, and Spoken Interaction. Each factor should be graded based on the provided levels: A0, A1, A2, B1, B2, C1, C2, where A0 is the beginner level.

# ### Grading Criteria:
# 1. **Listening:**
#    - **A0:** The learner understands very basic words or phrases when spoken slowly and clearly.
#    - **A1:** The learner can recognize familiar words and very basic phrases about immediate surroundings when spoken slowly and clearly.
#    - **A2:** The learner understands phrases and common vocabulary related to personal relevance and can catch the main point in simple messages.
#    - **B1:** The learner understands the main points of clear standard speech on familiar topics.
#    - **B2:** The learner understands extended speech and can follow complex lines of argument, provided the topic is familiar.
#    - **C1:** The learner understands extended speech even when it is not clearly structured.
#    - **C2:** The learner understands any kind of spoken language, even at fast native speed, with minimal difficulty.

# 2. **Pronunciation:**
#    - **A0:** The learner's pronunciation is basic with very limited clarity.
#    - **A1:** The learner's pronunciation is understandable when they speak slowly and clearly.
#    - **A2:** The learner's pronunciation is generally clear but may struggle with more complex words or phrases.
#    - **B1:** The learner's pronunciation is mostly clear, with occasional errors that do not affect comprehension.
#    - **B2:** The learner's pronunciation is clear and natural, with minor errors that do not impede understanding.
#    - **C1:** The learner's pronunciation is very clear, with accurate stress patterns and intonation, making them easy to understand even in complex situations.
#    - **C2:** The learner's pronunciation is nearly native-like, with precise articulation and intonation across all speech.

# 3. **Fluency:**
#    - **A0:** The learner can produce isolated words or short memorized phrases with significant hesitations.
#    - **A1:** The learner can speak using basic phrases but with frequent pauses and hesitations.
#    - **A2:** The learner can communicate in simple tasks with some fluency but with noticeable hesitations.
#    - **B1:** The learner can speak with some degree of fluency and spontaneity, though there are still pauses.
#    - **B2:** The learner can interact fluently and spontaneously, making regular interaction with native speakers quite possible.
#    - **C1:** The learner expresses ideas fluently and spontaneously without much searching for expressions.
#    - **C2:** The learner expresses ideas fluently and precisely, even in complex situations.

# 4. **Spoken Production:**
#    - **A0:** The learner uses basic words and memorized phrases to describe simple needs.
#    - **A1:** The learner uses simple phrases and sentences to describe where they live and people they know.
#    - **A2:** The learner uses a series of phrases and sentences to describe simple aspects of their background and environment.
#    - **B1:** The learner connects phrases to describe experiences, events, hopes, dreams, and briefly explain opinions.
#    - **B2:** The learner presents clear, detailed descriptions on a wide range of subjects related to their field of interest.
#    - **C1:** The learner presents clear, detailed descriptions of complex subjects, integrating sub-themes and concluding appropriately.
#    - **C2:** The learner produces clear, smoothly flowing descriptions or arguments, employing an appropriate style that ensures significant points are noticed and remembered.

# 5. **Spoken Interaction:**
#    - **A0:** The learner responds to very basic prompts or questions with memorized phrases.
#    - **A1:** The learner interacts simply if the other person repeats or rephrases things slowly.
#    - **A2:** The learner communicates in simple tasks, exchanging information on familiar topics.
#    - **B1:** The learner deals with most situations likely to arise when traveling in an area where the language is spoken.
#    - **B2:** The learner interacts fluently and spontaneously, making regular interaction with native speakers quite possible.
#    - **C1:** The learner expresses themselves fluently and spontaneously without much searching for expressions, using language effectively for social and professional purposes.
#    - **C2:** The learner participates effortlessly in any conversation or discussion, with a good command of idiomatic expressions and colloquialisms.

# ### Output Format:
# {{
#   "Summary": "Provide a concise summary of the learner's performance, including an overall assessment level and detailed feedback for each factor.",
#   "Listening": "Assessment Level (A0, A1, A2, B1, B2, C1, C2)",
#   "Pronunciation": "Assessment Level (A0, A1, A2, B1, B2, C1, C2)",
#   "Fluency": "Assessment Level (A0, A1, A2, B1, B2, C1, C2)",
#   "Spoken Production": "Assessment Level (A0, A1, A2, B1, B2, C1, C2)",
#   "Spoken Interaction": "Assessment Level (A0, A1, A2, B1, B2, C1, C2)",
#   "Overall Score": "Overall Grade (A0, A1, A2, B1, B2, C1, C2)"
# }}

# At the end of the assessment, summarize the learner's performance, providing feedback and practical tips for improvement.
# """



#         # Get response from ChatGPT
#         response = await summarize_conversation(prompt)
        
#         # Assuming response is returned as a JSON string, parse it into a dictionary
#         try:
#             json_response = json.loads(response)
#         except json.JSONDecodeError as e:
#             logging.error(f"Failed to parse JSON response from OpenAI API: {e}")
#             raise HTTPException(status_code=500, detail=f"Failed to parse JSON response from OpenAI API: {e}")
        
#         # Check if the summary is empty
#         summary = json_response.get("Summary", "").strip()
#         if not summary:
#             raise HTTPException(status_code=400, detail="The summary is empty. Please ensure the test is completed fully before requesting a summary.")

#         # Store the summary in a new collection
#         summary_data = {
#             "user_id": user_object_id,
#             "session_id": session_id,
#             "summary": summary,
#             "created_at": datetime.utcnow()
#         }
#         await summaries_collection.insert_one(summary_data)
#         logging.info(f"Summary stored successfully for user_id {user_id} and session_id {session_id}.")

#         # Return the summary
#         return {"summary": summary}

#     except HTTPException as e:
#         raise e  # Re-raise caught HTTP exceptions to return them to the client
#     except Exception as e:
#         logging.error(f"An error occurred: {e}")
#         raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

# @openai_analyze.post("/send-summary/")
# async def send_summary(email: str, session_id: str):
#     try:
#         # Fetch the user from the database using the provided email
#         user = await user_collection.find_one({"email": email})
#         if not user:
#             raise HTTPException(status_code=404, detail="User not found.")
        
#         user_id = user["_id"]

#         # Retrieve the summary from the summaries collection
#         summary_record = await summaries_collection.find_one({
#             "user_id": user_id,
#             "session_id": session_id
#         })

#         if not summary_record:
#             raise HTTPException(status_code=404, detail="Summary not found for the given session_id.")

#         # Extract the summary
#         summary = summary_record.get("summary", "No summary available.")

#         # Send the summary email
#         send_summary_email(email, summary)

#         return {"detail": "Summary sent successfully.", "user_email": email}

#     except HTTPException as e:
#         raise e  # Re-raise caught HTTP exceptions to return them to the client
#     except Exception as e:
#         logging.error(f"An error occurred: {e}")
#         raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")





import openai
import json
from datetime import datetime, timedelta
from fastapi import HTTPException, APIRouter
from motor.motor_asyncio import AsyncIOMotorClient
import os
from bson import ObjectId
from .summerize import summarize_conversation
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
import logging
import random
import string

# Setup logging
logging.basicConfig(level=logging.INFO)

# Set API keys from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')

# Initialize FastAPI router
openai_analyze = APIRouter()

# MongoDB connection
MONGO_URI = os.getenv('MONGO_URI')
client = AsyncIOMotorClient(MONGO_URI)
db = client['CEFRL']
user_collection = db['users']
conversations_collection = db['conversations']
summaries_collection = db['summaries']  # A new collection to store summaries
verified_collection = db['verified_users']  # Collection to store verified users
otp_collection = db['otp_verification']  # Collection to store OTPs
results_collection = db['results']  

# Function to send summary email
def send_summary_email(email: str, summary: str):
    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
    from_email = Email("ibadk6057@gmail.com")  # Replace with your email
    to_email = To(email)
    subject = "Your Conversation Summary and Feedback"
    
    # Create the email content
    html_content = f"""
    <html>
    <body>
        <h1>Your Conversation Summary and Feedback</h1>
        <p>{summary}</p>
        <p>We hope this feedback helps you improve your language skills. Keep practicing!</p>
        <p>Best regards,<br>The CEFRL Team</p>
    </body>
    </html>
    """
    
    content = Content("text/html", html_content)
    mail = Mail(from_email, to_email, subject, content)
    
    try:
        response = sg.send(mail)
        logging.info(f"Summary email sent successfully to {email}. Status Code: {response.status_code}")
    except Exception as e:
        logging.error(f"Failed to send summary email to {email}: {e}")

# Function to generate a random OTP
def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))

# Function to send OTP via email
def send_otp_email(email: str, otp: str):
    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
    from_email = Email("ibadk6057@gmail.com")  # Replace with your email
    to_email = To(email)
    subject = "Your OTP Code"
    
    html_content = f"""
    <html>
    <body>
        <h1>Your OTP Code</h1>
        <p>Your OTP code is <strong>{otp}</strong>. Please use this code to verify your email address.</p>
        <p>This code is valid for 10 minutes.</p>
        <p>Best regards,<br>The CEFRL Team</p>
    </body>
    </html>
    """
    
    content = Content("text/html", html_content)
    mail = Mail(from_email, to_email, subject, content)
    
    try:
        response = sg.send(mail)
        logging.info(f"OTP email sent successfully to {email}. Status Code: {response.status_code}")
    except Exception as e:
        logging.error(f"Failed to send OTP email to {email}: {e}")

# Endpoint to verify OTP
@openai_analyze.post("/verify-otp/")
async def verify_otp(email: str, otp: str):
    try:
        # Retrieve the OTP record
        otp_record = await otp_collection.find_one({"email": email, "otp": otp})
        
        if not otp_record:
            raise HTTPException(status_code=201, detail="Invalid OTP")

        # Check if the OTP has expired
        if datetime.utcnow() > otp_record["expiry"]:
            raise HTTPException(status_code=201, detail="OTP has expired")

        # Mark the user as verified
        user_id = otp_record["user_id"]
        session_id = otp_record["session_id"]
        await verified_collection.insert_one({
            "email": email,
            "user_id": user_id,
            "session_id": session_id,
            "verified": True
        })

        # Remove the OTP record
        await otp_collection.delete_one({"email": email, "otp": otp})

        return {"detail": "Email verified successfully."}

    except HTTPException as e:
        raise e  # Re-raise caught HTTP exceptions to return them to the client
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

# Endpoint to send summary email
@openai_analyze.post("/send-summary/")
async def send_summary(email: str, session_id: str):
    try:
        # Check if the user is verified
        verified_user = await verified_collection.find_one({"email": email, "verified": True})

        if not verified_user:
            # If not verified, generate OTP
            user = await user_collection.find_one({"email": email})
            if not user:
                raise HTTPException(status_code=201, detail="User not found.")
            
            user_id = user["_id"]
            otp = generate_otp()
            otp_expiry = datetime.utcnow() + timedelta(minutes=10)
            
            await otp_collection.insert_one({
                "email": email,
                "otp": otp,
                "expiry": otp_expiry,
                "user_id": user_id,
                "session_id": session_id
            })

            # Send OTP email
            send_otp_email(email, otp)
            return {"detail": "OTP sent. Please verify your email."}

        # Retrieve the summary from the summaries collection
        summary_record = await summaries_collection.find_one({
            "user_id": verified_user["user_id"],
            "session_id": session_id
        })

        if not summary_record:
            raise HTTPException(status_code=201, detail="Summary not found for the given session_id.")

        # Extract the summary
        summary = summary_record.get("summary", "No summary available.")

        # Send the summary email
        send_summary_email(email, summary)

        return {"detail": "Summary sent successfully.", "user_email": email}

    except HTTPException as e:
        raise e  # Re-raise caught HTTP exceptions to return them to the client
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

# Endpoint to analyze conversation
@openai_analyze.get("/analyze-conversation/")
async def analyze_conversation(user_id: str, session_id: str):
    try:
        # Convert user_id to ObjectId
        user_object_id = ObjectId(user_id)

        # Query the conversation collection to find the conversation for the given user_id and session_id
        conversation = await conversations_collection.find_one({
            "user_id": user_object_id,
            "session_id": session_id
        })

        if not conversation:
            raise HTTPException(status_code=201, detail="Conversation not found for the given session_id.")

        # Extract messages from the session safely
        messages = conversation.get("session", {}).get("messages", [])
        if not messages:
            raise HTTPException(status_code=201, detail="No messages found in the conversation.")

        # Construct input content for analysis
        input_content = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])

        # Prepare the prompt for ChatGPT
        prompt = f"""{input_content}
 You are an expert language coach. Your task is to analyze a conversation between a language learner and another participant. Based on the learner's performance, evaluate their language skills according to five key factors: Listening, Pronunciation, Fluency, Spoken Production, and Spoken Interaction. Each factor should be graded based on the provided levels: A0, A1, A2, B1, B2, C1, C2, where A0 is the beginner level.

### Grading Criteria:
1. **Listening:**
   - **A0:** The learner understands very basic words or phrases when spoken slowly and clearly.
   - **A1:** The learner can recognize familiar words and very basic phrases about immediate surroundings when spoken slowly and clearly.
   - **A2:** The learner understands phrases and common vocabulary related to personal relevance and can catch the main point in simple messages.
   - **B1:** The learner understands the main points of clear standard speech on familiar topics.
   - **B2:** The learner understands extended speech and can follow complex lines of argument, provided the topic is familiar.
   - **C1:** The learner understands extended speech even when it is not clearly structured.
   - **C2:** The learner understands any kind of spoken language, even at fast native speed, with minimal difficulty.

2. **Pronunciation:**
   - **A0:** The learner's pronunciation is basic with very limited clarity.
   - **A1:** The learner's pronunciation is understandable when they speak slowly and clearly.
   - **A2:** The learner's pronunciation is generally clear but may struggle with more complex words or phrases.
   - **B1:** The learner's pronunciation is mostly clear, with occasional errors that do not affect comprehension.
   - **B2:** The learner's pronunciation is clear and natural, with minor errors that do not impede understanding.
   - **C1:** The learner's pronunciation is very clear, with accurate stress patterns and intonation, making them easy to understand even in complex situations.
   - **C2:** The learner's pronunciation is nearly native-like, with precise articulation and intonation across all speech.

3. **Fluency:**
   - **A0:** The learner can produce isolated words or short memorized phrases with significant hesitations.
   - **A1:** The learner can speak using basic phrases but with frequent pauses and hesitations.
   - **A2:** The learner can communicate in simple tasks with some fluency but with noticeable hesitations.
   - **B1:** The learner can speak with some degree of fluency and spontaneity, though there are still pauses.
   - **B2:** The learner can interact fluently and spontaneously, making regular interaction with native speakers quite possible.
   - **C1:** The learner expresses ideas fluently and spontaneously without much searching for expressions.
   - **C2:** The learner expresses ideas fluently and precisely, even in complex situations.

4. **Spoken Production:**
   - **A0:** The learner uses basic words and memorized phrases to describe simple needs.
   - **A1:** The learner uses simple phrases and sentences to describe where they live and people they know.
   - **A2:** The learner uses a series of phrases and sentences to describe simple aspects of their background and environment.
   - **B1:** The learner connects phrases to describe experiences, events, hopes, dreams, and briefly explain opinions.
   - **B2:** The learner presents clear, detailed descriptions on a wide range of subjects related to their field of interest.
   - **C1:** The learner presents clear, detailed descriptions of complex subjects, integrating sub-themes and concluding appropriately.
   - **C2:** The learner produces clear, smoothly flowing descriptions or arguments, employing an appropriate style that ensures significant points are noticed and remembered.

5. **Spoken Interaction:**
   - **A0:** The learner responds to very basic prompts or questions with memorized phrases.
   - **A1:** The learner interacts simply if the other person repeats or rephrases things slowly.
   - **A2:** The learner communicates in simple tasks, exchanging information on familiar topics.
   - **B1:** The learner deals with most situations likely to arise when traveling in an area where the language is spoken.
   - **B2:** The learner interacts fluently and spontaneously, making regular interaction with native speakers quite possible.
   - **C1:** The learner expresses themselves fluently and spontaneously without much searching for expressions, using language effectively for social and professional purposes.
   - **C2:** The learner participates effortlessly in any conversation or discussion, with a good command of idiomatic expressions and colloquialisms.

### Output Format:
{{
  "Summary": "Provide a concise summary of the learner's performance, including an overall assessment level and detailed feedback for each factor.",
  "Listening": "Assessment Level (A0, A1, A2, B1, B2, C1, C2)",
  "Pronunciation": "Assessment Level (A0, A1, A2, B1, B2, C1, C2)",
  "Fluency": "Assessment Level (A0, A1, A2, B1, B2, C1, C2)",
  "Spoken Production": "Assessment Level (A0, A1, A2, B1, B2, C1, C2)",
  "Spoken Interaction": "Assessment Level (A0, A1, A2, B1, B2, C1, C2)",
  "Overall Score": "Overall Grade (A0, A1, A2, B1, B2, C1, C2)"
}}

At the end of the assessment, summarize the learner's performance, providing feedback and practical tips for improvement.
"""

        # Get response from ChatGPT
        response = await summarize_conversation(prompt)
        
        # Assuming response is returned as a JSON string, parse it into a dictionary
        try:
            json_response = json.loads(response)
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON response from OpenAI API: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to parse JSON response from OpenAI API: {e}")
        
        # Check if the summary is empty
        summary = json_response.get("Summary", "").strip()
        if not summary:
            raise HTTPException(status_code=201, detail="The summary is empty. Please ensure the test is completed fully before requesting a summary.")

        # Store the summary in a new collection
        summary_data = {
            "user_id": user_object_id,
            "session_id": session_id,
            "summary": summary,
            "created_at": datetime.utcnow()
        }
        await summaries_collection.insert_one(summary_data)
        logging.info(f"Summary stored successfully for user_id {user_id} and session_id {session_id}.")

        result_data = {
            "user_id": user_object_id,
            "session_id": session_id,
            "result": json_response,
            "created_at": datetime.utcnow()
        }
        await results_collection.insert_one(result_data)
        logging.info(f"Result stored successfully for user_id {user_id} and session_id {session_id}.")

        # Return the complete analysis including grades
        return json_response

    except HTTPException as e:
        raise e  # Re-raise caught HTTP exceptions to return them to the client
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
