# # from fastapi import APIRouter, HTTPException
# # from pydantic import BaseModel, EmailStr, ValidationError
# # from motor.motor_asyncio import AsyncIOMotorClient
# # import os
# # from typing import List
# # import sendgrid
# # from sendgrid.helpers.mail import Mail, Email, To, Content
# # import logging

# # # Configure logging
# # logging.basicConfig(level=logging.INFO)

# # # Load environment variables
# # MONGO_URI = os.getenv('MONGO_URI')
# # SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')

# # # Ensure the API key is loaded
# # if not SENDGRID_API_KEY:
# #     logging.error("SENDGRID_API_KEY is not set. Please ensure it is correctly configured.")
# #     raise HTTPException(status_code=500, detail="SendGrid API key is missing.")

# # # MongoDB client setup
# # try:
# #     client = AsyncIOMotorClient(MONGO_URI)
# #     db = client['CEFRL']
# #     logging.info("Connected to MongoDB successfully.")
# # except Exception as e:
# #     logging.error(f"Failed to connect to MongoDB: {e}")
# #     raise HTTPException(status_code=500, detail="Database connection error")

# # InviteByAdmin_app = APIRouter()

# # # Pydantic model for invitation
# # class InviteRequest(BaseModel):
# #     emails: List[EmailStr]

# # # Function to send invitation email
# # def send_invitation_email(email: str):
# #     sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
# #     from_email = Email("ibadk6057@gmail.com")
# #     to_email = To(email)
# #     subject = "You're Invited!"
    
# #     html_content = f"""
# #     <html>
# #     <body>
# #         <h1>You're Invited!</h1>
# #         <p>You have been invited to join our platform. Click the link below to register:</p>
# #         <a href="http://yourdomain.com/register?email={email}">Register Now</a>
# #         <p>We look forward to having you with us.</p>
# #         <p>Best regards,<br>Your Team</p>
# #     </body>
# #     </html>
# #     """
    
# #     content = Content("text/html", html_content)
# #     mail = Mail(from_email, to_email, subject, content)
    
# #     try:
# #         response = sg.send(mail)
# #         logging.info(f"Invitation email sent successfully to {email}. Status Code: {response.status_code}")
# #     except Exception as e:
# #         logging.error(f"Failed to send invitation email to {email}: {e}")
# #         raise e

# # # Endpoint to send invitations
# # @InviteByAdmin_app.post("/invite")
# # async def send_invitations(invite_request: InviteRequest):
# #     emails = invite_request.emails
# #     logging.info(f"Inviting the following emails: {emails}")
    
# #     failed_emails = []
# #     successful_emails = []

# #     for email in emails:
# #         try:
# #             send_invitation_email(email)
# #             successful_emails.append(email)
# #         except Exception as e:
# #             logging.error(f"Failed to send invitation to {email}: {e}")
# #             failed_emails.append(email)

# #     if failed_emails:
# #         return {
# #             "detail": "Some invitations failed to send.",
# #             "successful_emails": successful_emails,
# #             "failed_emails": failed_emails
# #         }
# #     else:
# #         return {"detail": "All invitations sent successfully.", "successful_emails": successful_emails}



# #Improve validation



# # from fastapi import APIRouter, HTTPException
# # from pydantic import BaseModel, EmailStr, ValidationError
# # from motor.motor_asyncio import AsyncIOMotorClient
# # import os
# # from typing import List
# # import sendgrid
# # from sendgrid.helpers.mail import Mail, Email, To, Content
# # import logging
# # import re

# # # Configure logging
# # logging.basicConfig(level=logging.INFO)

# # # Load environment variables
# # MONGO_URI = os.getenv('MONGO_URI')
# # SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')

# # # Ensure the API key is loaded
# # if not SENDGRID_API_KEY:
# #     logging.error("SENDGRID_API_KEY is not set. Please ensure it is correctly configured.")
# #     raise HTTPException(status_code=500, detail="SendGrid API key is missing.")

# # # MongoDB client setup
# # try:
# #     client = AsyncIOMotorClient(MONGO_URI)
# #     db = client['CEFRL']
# #     logging.info("Connected to MongoDB successfully.")
# # except Exception as e:
# #     logging.error(f"Failed to connect to MongoDB: {e}")
# #     raise HTTPException(status_code=500, detail="Database connection error")

# # InviteByAdmin_app = APIRouter()

# # # Pydantic model for invitation
# # class InviteRequest(BaseModel):
# #     emails: List[EmailStr]

# # # Function to validate the email structure beyond basic syntax
# # def is_valid_email(email: str) -> bool:
# #     # Simple regex to check the structure beyond the basic validation provided by EmailStr
# #     regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
# #     return re.match(regex, email) is not None

# # # Function to send invitation email
# # def send_invitation_email(email: str):
# #     sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
# #     from_email = Email("ibadk6057@gmail.com")
# #     to_email = To(email)
# #     subject = "You're Invited to Take the Speaking Language Test!"

# #     html_content = f"""
# #     <html>
# #     <body>
# #         <h1>You're Invited to Take the Speaking Language Test!</h1>
# #         <p>You have been invited by CEFRL to participate in our Speaking Language Test.</p>
# #         <p>Click the link below to register and begin your test:</p>
# #         <a href="https://ceran-87530.bubbleapps.io/version-test/register?email={email}">Register Now</a>
# #         <p>We look forward to helping you improve your language skills.</p>
# #         <p>Best regards,<br>The CEFRL Team</p>
# #         <p><small>This app is powered by Octaloop Technologies.</small></p>
# #     </body>
# #     </html>
# #     """

# #     content = Content("text/html", html_content)
# #     mail = Mail(from_email, to_email, subject, content)
    
# #     try:
# #         response = sg.send(mail)
# #         logging.info(f"Invitation email sent successfully to {email}. Status Code: {response.status_code}")
# #         return True  # Email sent successfully
# #     except Exception as e:
# #         logging.error(f"Failed to send invitation email to {email}: {e}")
# #         return False  # Email failed to send


# # # Endpoint to send invitations
# # @InviteByAdmin_app.post("/invite")
# # async def send_invitations(invite_request: InviteRequest):
# #     emails = invite_request.emails
# #     logging.info(f"Inviting the following emails: {emails}")
    
# #     failed_emails = []
# #     successful_emails = []

# #     for email in emails:
# #         if not is_valid_email(email):
# #             logging.error(f"Invalid email format detected: {email}")
# #             failed_emails.append(email)
# #             continue
        
# #         if send_invitation_email(email):
# #             successful_emails.append(email)
# #         else:
# #             failed_emails.append(email)

# #     if failed_emails:
# #         return {
# #             "detail": "Some invitations failed to send.",
# #             "successful_emails": successful_emails,
# #             "failed_emails": failed_emails
# #         }
# #     else:
# #         return {"detail": "All invitations sent successfully.", "successful_emails": successful_emails}



# #Custom Content


# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel, EmailStr, ValidationError
# from motor.motor_asyncio import AsyncIOMotorClient
# import os
# from typing import List, Optional
# import sendgrid
# from sendgrid.helpers.mail import Mail, Email, To, Content
# import logging
# import re

# # Configure logging
# logging.basicConfig(level=logging.INFO)

# # Load environment variables
# MONGO_URI = os.getenv('MONGO_URI')
# SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')

# # Ensure the API key is loaded
# if not SENDGRID_API_KEY:
#     logging.error("SENDGRID_API_KEY is not set. Please ensure it is correctly configured.")
#     raise HTTPException(status_code=500, detail="SendGrid API key is missing.")

# # MongoDB client setup
# try:
#     client = AsyncIOMotorClient(MONGO_URI)
#     db = client['CEFRL']
#     logging.info("Connected to MongoDB successfully.")
# except Exception as e:
#     logging.error(f"Failed to connect to MongoDB: {e}")
#     raise HTTPException(status_code=500, detail="Database connection error")

# InviteByAdmin_app = APIRouter()

# # Pydantic model for invitation
# class InviteRequest(BaseModel):
#     emails: List[EmailStr]
#     custom_message: Optional[str] = None  # Allow admin to provide a custom message

# # Function to validate the email structure beyond basic syntax
# def is_valid_email(email: str) -> bool:
#     # Simple regex to check the structure beyond the basic validation provided by EmailStr
#     regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
#     return re.match(regex, email) is not None

# # Function to extract the username from the email
# def extract_username(email: str) -> str:
#     return email.split('@')[0]

# # Function to send invitation email
# def send_invitation_email(email: str, custom_message: Optional[str] = None):
#     sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
#     from_email = Email("ibadk6057@gmail.com")
#     to_email = To(email)
#     username = extract_username(email)
#     subject = "You're Invited to Take the Speaking Language Test!"

#     if custom_message:
#         # Replace {username} in the custom message with the actual username
#         html_content = custom_message.replace("{username}", username)
#     else:
#         # Default email content if no custom message is provided
#         html_content = f"""
#         <html>
#         <body>
#             <h1>Hello {username},</h1>
#             <p>You have been invited by CEFRL to participate in our Speaking Language Test.</p>
#             <p>Click the link below to register and begin your test:</p>
#             <a href="https://ceran-87530.bubbleapps.io/version-test/register?email={email}">Register Now</a>
#             <p>We look forward to helping you improve your language skills.</p>
#             <p>Best regards,<br>The CEFRL Team</p>
#             <p><small>This app is powered by Octaloop Technologies.</small></p>
#         </body>
#         </html>
#         """

#     content = Content("text/html", html_content)
#     mail = Mail(from_email, to_email, subject, content)
    
#     try:
#         response = sg.send(mail)
#         logging.info(f"Invitation email sent successfully to {email}. Status Code: {response.status_code}")
#         return True  # Email sent successfully
#     except Exception as e:
#         logging.error(f"Failed to send invitation email to {email}: {e}")
#         return False  # Email failed to send

# # Endpoint to send invitations
# @InviteByAdmin_app.post("/invite")
# async def send_invitations(invite_request: InviteRequest):
#     emails = invite_request.emails
#     custom_message = invite_request.custom_message
#     logging.info(f"Inviting the following emails: {emails}")
    
#     successful_emails = []

#     for email in emails:
#         if not is_valid_email(email):
#             logging.error(f"Invalid email format detected: {email}")
#             continue
        
#         if send_invitation_email(email, custom_message):
#             successful_emails.append(email)

#     return {"detail": "Invitations processed.", "successful_emails": successful_emails}


#Update for single emaile
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from motor.motor_asyncio import AsyncIOMotorClient
import os
from typing import Optional
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
MONGO_URI = os.getenv('MONGO_URI')
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')

# Ensure the API key is loaded
if not SENDGRID_API_KEY:
    logging.error("SENDGRID_API_KEY is not set. Please ensure it is correctly configured.")
    raise HTTPException(status_code=500, detail="SendGrid API key is missing.")

# MongoDB client setup
try:
    client = AsyncIOMotorClient(MONGO_URI)
    db = client['CEFRL']
    logging.info("Connected to MongoDB successfully.")
except Exception as e:
    logging.error(f"Failed to connect to MongoDB: {e}")
    raise HTTPException(status_code=500, detail="Database connection error")

InviteByAdmin_app = APIRouter()

# Pydantic model for invitation
class InviteRequest(BaseModel):
    email: EmailStr
    custom_message: Optional[str] = None  # Allow admin to provide a custom message

# Function to validate the email structure beyond basic syntax
def is_valid_email(email: str) -> bool:
    # Simple regex to check the structure beyond the basic validation provided by EmailStr
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(regex, email) is not None

# Function to extract the username from the email
def extract_username(email: str) -> str:
    return email.split('@')[0]

def apply_formatting(text):
    # Define the replacement patterns for each formatting flag
    replacements = [
        (r'\[size=(\d+)\](.*?)\[/size\]', lambda m: f'<span style="font-size:{m.group(1)}px;">{m.group(2)}</span>'),
        (r'\[b\](.*?)\[/b\]', lambda m: f'<strong>{m.group(1)}</strong>'),
        (r'\[i\](.*?)\[/i\]', lambda m: f'<em>{m.group(1)}</em>'),
    ]
    
    # Apply the replacements using regex
    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text)
    
    # Split the text by lines and add a <br/> to the end of each line
    lines = text.split('\n')
    formatted_lines = [line.strip() + '<br/>' for line in lines if line.strip()]
    
    # Join the lines back together
    return '\n'.join(formatted_lines)

def send_invitation_email(email: str, custom_message: Optional[str] = None):
    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
    from_email = Email("jdevilleneuve@CERAN.com")
    to_email = To(email)
    username = extract_username(email)
    subject = "You're Invited to Take the Speaking Language Test!"

    # Default email content
    default_template = f"""
    <html>
    <body>
        <h1>Hello {username},</h1>
        <p>You have been invited by CEFRL to participate in our Speaking Language Test.</p>
        <p>Click the link below to register and begin your test:</p>
        <a href="https://ceran-87530.bubbleapps.io/version-test/register?email={email}">Register Now</a>
        <p>We look forward to helping you improve your language skills.</p>
        <p>Best regards,<br>The CEFRL Team</p>
        <p><small>This app is powered by Octaloop Technologies.</small></p>
    </body>
    </html>
    """

    # If the custom_message is empty or None, set it to the default template
    if not custom_message:
        custom_message = default_template
    else:
        # Apply formatting to the custom_message if it's provided
        custom_message = apply_formatting(custom_message)

    content = Content("text/html", custom_message)
    mail = Mail(from_email, to_email, subject, content)
    
    try:
        response = sg.send(mail)
        logging.info(f"Invitation email sent successfully to {email}. Status Code: {response.status_code}")
        return True  # Email sent successfully
    except Exception as e:
        logging.error(f"Failed to send invitation email to {email}: {e}")
        return False  # Email failed to send

# Endpoint to send invitations
@InviteByAdmin_app.post("/invite")
async def send_invitation(invite_request: InviteRequest):
    email = invite_request.email
    custom_message = invite_request.custom_message
    
    logging.info(f"Inviting the email: {email}")
    
    if not is_valid_email(email):
        logging.error(f"Invalid email format detected: {email}")
        raise HTTPException(status_code=400, detail="Invalid email format.")
    
    if send_invitation_email(email, custom_message):
        return {"detail": "Invitation sent successfully.", "email": email}
    else:
        raise HTTPException(status_code=500, detail="Failed to send the invitation.")
