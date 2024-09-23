import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field
from pydantic_core import core_schema
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os
import io
from bson import ObjectId
from typing import List, Optional, Annotated


MONGO_URI = os.getenv('MONGO_URI')
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
    session_id: str  # Add session_id to the model
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

client = AsyncIOMotorClient(MONGO_URI)
db = client['CEFRL']
user_collection = db['users']
conversations_collection = db['conversations']
scores_collection = db['scores']

register_app = APIRouter()
@register_app.post("/register")
async def register(user: UserCreate):
    # Check if the user already exists
    existing_user = await user_collection.find_one({"email": user.email})
    
    if existing_user:
        user_id = existing_user["_id"]  # Reuse the existing user_id
    else:
        # Create a new user with a new user_id
        user_dict = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "language_interface": user.language_interface,
            "language_test": user.language_test,
            "created_at": datetime.utcnow()
        }
        result = await user_collection.insert_one(user_dict)
        user_id = result.inserted_id

    # Generate a unique session_id
    session_id = str(uuid.uuid4())

    # Return user_id and session_id
    return {"detail": "User registered successfully", "user_id": str(user_id), "session_id": session_id}

@register_app.get("/users/{user_id}", response_model=User)
async def read_user(user_id: str):
    user = await user_collection.find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user)

@register_app.put("/users/{user_id}", response_model=User)
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
    # return User(**updated_user)

@register_app.delete("/users/{user_id}")
async def delete_user(user_id: str):
    result = await user_collection.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User deleted successfully"}


#------------------------welcome Email

# import uuid
# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel, EmailStr, Field
# from pydantic_core import core_schema
# from motor.motor_asyncio import AsyncIOMotorClient
# from datetime import datetime
# import os
# from bson import ObjectId
# from typing import List, Optional, Annotated
# import sendgrid
# from sendgrid.helpers.mail import Mail, Email, To, Content
# import logging

# # Configure logging
# logging.basicConfig(level=logging.INFO)

# # Load environment variables
# MONGO_URI = os.getenv('MONGO_URI')
# SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')

# # Add a print statement to ensure the API key is loaded correctly
# print(f"SENDGRID_API_KEY is loaded: {bool(SENDGRID_API_KEY)}")

# if not SENDGRID_API_KEY:
#     logging.error("SENDGRID_API_KEY is not set. Please ensure it is correctly configured in your environment variables.")
#     raise HTTPException(status_code=500, detail="SendGrid API key is missing.")

# # Custom ObjectId Pydantic Type
# class PyObjectId(str):
#     @classmethod
#     def __get_validators__(cls):
#         yield cls.validate

#     @classmethod
#     def validate(cls, v):
#         if not ObjectId.is_valid(v):
#             raise ValueError("Invalid ObjectId")
#         return str(v)

#     @classmethod
#     def __get_pydantic_core_schema__(cls, _source_type, _handler):
#         return core_schema.json_or_python_schema(
#             json_schema=core_schema.str_schema(),
#             python_schema=core_schema.union_schema([
#                 core_schema.is_instance_schema(ObjectId),
#                 core_schema.chain_schema([
#                     core_schema.str_schema(),
#                     core_schema.no_info_plain_validator_function(cls.validate),
#                 ]),
#             ]),
#             serialization=core_schema.plain_serializer_function_ser_schema(str),
#         )
# PydanticObjectId = Annotated[PyObjectId, Field(default_factory=PyObjectId)]

# # Pydantic models
# class UserCreate(BaseModel):
#     first_name: str
#     last_name: str
#     email: EmailStr
#     language_interface: str
#     language_test: str

# class UserUpdate(BaseModel):
#     first_name: Optional[str] = None
#     last_name: Optional[str] = None
#     language_interface: Optional[str] = None
#     language_test: Optional[str] = None

# class User(BaseModel):
#     first_name: str
#     last_name: str
#     email: EmailStr
#     language_interface: str
#     language_test: str

#     model_config = {
#         "populate_by_name": True,
#         "json_encoders": {ObjectId: str},
#         "arbitrary_types_allowed": True,
#     }

# class Message(BaseModel):
#     role: str
#     content: str

# class Session(BaseModel):
#     messages: List[Message]

# class ConversationCreate(BaseModel):
#     user_id: PydanticObjectId
#     session_id: str  # Add session_id to the model
#     session: Session

# class Conversation(ConversationCreate):
#     id: PydanticObjectId = Field(alias="_id")
#     created_at: datetime = Field(default_factory=datetime.utcnow)

#     model_config = {
#         "populate_by_name": True,
#         "json_encoders": {ObjectId: str},
#         "arbitrary_types_allowed": True,
#     }

# class ScoreCreate(BaseModel):
#     conversation_id: PydanticObjectId
#     average_score: float
#     fluency: float
#     pronunciation: float
#     listening: float

# class Score(ScoreCreate):
#     id: PydanticObjectId = Field(alias="_id")

#     model_config = {
#         "populate_by_name": True,
#         "json_encoders": {ObjectId: str},
#         "arbitrary_types_allowed": True,
#     }

# # MongoDB client setup
# try:
#     client = AsyncIOMotorClient(MONGO_URI)
#     db = client['CEFRL']
#     user_collection = db['users']
#     conversations_collection = db['conversations']
#     scores_collection = db['scores']
#     logging.info("Connected to MongoDB successfully.")
# except Exception as e:
#     logging.error(f"Failed to connect to MongoDB: {e}")
#     raise HTTPException(status_code=500, detail="Database connection error")

# register_app = APIRouter()

# # Function to send a welcome email using SendGrid
# def send_welcome_email(email: str, first_name: str):
#     try:
#         logging.info("Initializing SendGrid client...")
#         sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
#     except Exception as e:
#         logging.error(f"Failed to initialize SendGrid client: {e}")
#         return

#     from_email = Email("ibadk6057@gmail.com")
#     to_email = To(email)
#     subject = "Welcome to Our Service!"

#     html_content = f"""
#     <html>
#     <body>
#         <h1>Welcome , {first_name}!</h1>
#         <p>Thank you for registering with us. We're glad to have you on board!</p>
#         <p>Best regards,<br>CEFRL Language Test</p>
#     </body>
#     </html>
#     """
    
#     logging.info(f"Email content prepared for {email}.")
    
#     content = Content("text/html", html_content)
#     mail = Mail(from_email, to_email, subject, content)
    
#     try:
#         logging.info("Sending email via SendGrid...")
#         response = sg.send(mail)
#         logging.info(f"Email sent successfully. Status Code: {response.status_code}")
#         logging.info(f"Response Body: {response.body}")
#         logging.info(f"Response Headers: {response.headers}")
#     except Exception as e:
#         logging.error(f"Failed to send email: {e}")

# # Register a new user
# @register_app.post("/register")
# async def register(user: UserCreate):
#     try:
#         existing_user = await user_collection.find_one({"email": user.email})
#         logging.info(f"Checked for existing user: {user.email}")
#     except Exception as e:
#         logging.error(f"Database query failed: {e}")
#         raise HTTPException(status_code=500, detail="Database query error")
    
#     if existing_user:
#         user_id = existing_user["_id"]  # Reuse the existing user_id
#         logging.info(f"User already exists with ID: {user_id}")
#     else:
#         try:
#             user_dict = {
#                 "first_name": user.first_name,
#                 "last_name": user.last_name,
#                 "email": user.email,
#                 "language_interface": user.language_interface,
#                 "language_test": user.language_test,
#                 "created_at": datetime.utcnow()
#             }
#             result = await user_collection.insert_one(user_dict)
#             user_id = result.inserted_id

#             logging.info(f"New user created with ID: {user_id}")

#             # Send welcome email
#             send_welcome_email(user.email, user.first_name)
#         except Exception as e:
#             logging.error(f"Failed to create user or send email: {e}")
#             raise HTTPException(status_code=500, detail="User registration failed")

#     session_id = str(uuid.uuid4())
#     logging.info(f"Generated session ID: {session_id}")

#     return {"detail": "User registered successfully", "user_id": str(user_id), "session_id": session_id}

# # Read a user by ID
# @register_app.get("/users/{user_id}", response_model=User)
# async def read_user(user_id: str):
#     try:
#         user = await user_collection.find_one({"_id": ObjectId(user_id)})
#         logging.info(f"Queried user with ID: {user_id}")
#     except Exception as e:
#         logging.error(f"Database query failed: {e}")
#         raise HTTPException(status_code=500, detail="Database query error")
    
#     if user is None:
#         logging.warning(f"User not found with ID: {user_id}")
#         raise HTTPException(status_code=404, detail="User not found")
#     return User(**user)

# # Update a user by ID
# @register_app.put("/users/{user_id}", response_model=User)
# async def update_user(user_id: str, user: UserUpdate):
#     try:
#         update_data = {k: v for k, v in user.model_dump().items() if v is not None}
#         if len(update_data) == 0:
#             raise HTTPException(status_code=200, detail="No fields to update")
#         result = await user_collection.update_one(
#             {"_id": ObjectId(user_id)}, {"$set": update_data}
#         )
#         logging.info(f"Attempted to update user with ID: {user_id}")

#         if result.modified_count == 0:
#             logging.warning(f"No updates made for user with ID: {user_id}")
#             raise HTTPException(status_code=404, detail="User not found")
#         updated_user = await user_collection.find_one({"_id": ObjectId(user_id)})
#         return User(**updated_user)
#     except Exception as e:
#         logging.error(f"Failed to update user: {e}")
#         raise HTTPException(status_code=500, detail="User update failed")

# # Delete a user by ID
# @register_app.delete("/users/{user_id}")
# async def delete_user(user_id: str):
#     try:
#         result = await user_collection.delete_one({"_id": ObjectId(user_id)})
#         logging.info(f"Attempted to delete user with ID: {user_id}")
#         if result.deleted_count == 0:
#             logging.warning(f"User not found for deletion with ID: {user_id}")
#             raise HTTPException(status_code=404, detail="User not found")
#         return {"detail": "User deleted successfully"}
#     except Exception as e:
#         logging.error(f"Failed to delete user: {e}")
#         raise HTTPException(status_code=500, detail="User deletion failed")



#------------------OTP


# import random
# import string
# import uuid
# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel, EmailStr, Field
# from pydantic_core import core_schema
# from motor.motor_asyncio import AsyncIOMotorClient
# from datetime import datetime, timedelta
# import os
# from bson import ObjectId
# from typing import List, Optional, Annotated
# import sendgrid
# from sendgrid.helpers.mail import Mail, Email, To, Content
# import logging

# # Configure logging
# logging.basicConfig(level=logging.INFO)

# # Load environment variables
# MONGO_URI = os.getenv('MONGO_URI')
# SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')

# # Ensure the API key is loaded
# if not SENDGRID_API_KEY:
#     logging.error("SENDGRID_API_KEY is not set. Please ensure it is correctly configured.")
#     raise HTTPException(status_code=500, detail="SendGrid API key is missing.")

# # Custom ObjectId Pydantic Type
# class PyObjectId(str):
#     @classmethod
#     def __get_validators__(cls):
#         yield cls.validate

#     @classmethod
#     def validate(cls, v):
#         if not ObjectId.is_valid(v):
#             raise ValueError("Invalid ObjectId")
#         return str(v)

#     @classmethod
#     def __get_pydantic_core_schema__(cls, _source_type, _handler):
#         return core_schema.json_or_python_schema(
#             json_schema=core_schema.str_schema(),
#             python_schema=core_schema.union_schema([
#                 core_schema.is_instance_schema(ObjectId),
#                 core_schema.chain_schema([
#                     core_schema.str_schema(),
#                     core_schema.no_info_plain_validator_function(cls.validate),
#                 ]),
#             ]),
#             serialization=core_schema.plain_serializer_function_ser_schema(str),
#         )
# PydanticObjectId = Annotated[PyObjectId, Field(default_factory=PyObjectId)]

# # Pydantic models
# class UserCreate(BaseModel):
#     first_name: str
#     last_name: str
#     email: EmailStr
#     language_interface: str
#     language_test: str

# class UserUpdate(BaseModel):
#     first_name: Optional[str] = None
#     last_name: Optional[str] = None
#     language_interface: Optional[str] = None
#     language_test: Optional[str] = None

# class User(BaseModel):
#     first_name: str
#     last_name: str
#     email: EmailStr
#     language_interface: str
#     language_test: str
#     verified: bool = False  # Add verified field to the user model

#     model_config = {
#         "populate_by_name": True,
#         "json_encoders": {ObjectId: str},
#         "arbitrary_types_allowed": True,
#     }

# class Message(BaseModel):
#     role: str
#     content: str

# class Session(BaseModel):
#     messages: List[Message]

# class ConversationCreate(BaseModel):
#     user_id: PydanticObjectId
#     session_id: str  # Add session_id to the model
#     session: Session

# class Conversation(ConversationCreate):
#     id: PydanticObjectId = Field(alias="_id")
#     created_at: datetime = Field(default_factory=datetime.utcnow)

#     model_config = {
#         "populate_by_name": True,
#         "json_encoders": {ObjectId: str},
#         "arbitrary_types_allowed": True,
#     }

# class ScoreCreate(BaseModel):
#     conversation_id: PydanticObjectId
#     average_score: float
#     fluency: float
#     pronunciation: float
#     listening: float

# class Score(ScoreCreate):
#     id: PydanticObjectId = Field(alias="_id")

#     model_config = {
#         "populate_by_name": True,
#         "json_encoders": {ObjectId: str},
#         "arbitrary_types_allowed": True,
#     }

# # MongoDB client setup
# try:
#     client = AsyncIOMotorClient(MONGO_URI)
#     db = client['CEFRL']
#     user_collection = db['users']
#     otp_collection = db['otps']  # Create a collection to store OTPs
#     logging.info("Connected to MongoDB successfully.")
# except Exception as e:
#     logging.error(f"Failed to connect to MongoDB: {e}")
#     raise HTTPException(status_code=500, detail="Database connection error")

# register_app = APIRouter()

# # Function to generate a random OTP
# def generate_otp(length=6):
#     return ''.join(random.choices(string.digits, k=length))

# # Function to send OTP via email using SendGrid
# def send_otp_email(email: str, otp: str):
#     sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
#     from_email = Email("ibadk6057@gmail.com")
#     to_email = To(email)
#     subject = "Your OTP Code"
    
#     html_content = f"""
#     <html>
#     <body>
#         <h1>Your OTP Code</h1>
#         <p>Your OTP code is <strong>{otp}</strong>. Please use this code to complete your registration.</p>
#         <p>This code is valid for 10 minutes.</p>
#         <p>Best regards,<br>CEFRL Language Test</p>
#     </body>
#     </html>
#     """
    
#     content = Content("text/html", html_content)
#     mail = Mail(from_email, to_email, subject, content)
    
#     try:
#         response = sg.send(mail)
#         logging.info(f"OTP email sent successfully. Status Code: {response.status_code}")
#     except Exception as e:
#         logging.error(f"Failed to send OTP email: {e}")

# # Register a new user and send OTP
# @register_app.post("/register")
# async def register(user: UserCreate):
#     try:
#         existing_user = await user_collection.find_one({"email": user.email})
#         logging.info(f"Checked for existing user: {user.email}")
#     except Exception as e:
#         logging.error(f"Database query failed: {e}")
#         raise HTTPException(status_code=500, detail="Database query error")
    
#     if existing_user:
#         # Check if the user is already verified
#         if existing_user.get("verified", False):
#             logging.info(f"User is already verified: {existing_user['_id']}")
#             session_id = str(uuid.uuid4())
#             logging.info(f"Generated session ID: {session_id}")
#             return {"detail": "User is already registered and verified.", "user_id": str(existing_user['_id']), "session_id": session_id}
#         else:
#             logging.info(f"User is registered but not verified: {existing_user['_id']}")
#             # Optionally, resend the OTP if the user is not verified
#             otp = generate_otp()
#             otp_expiry = datetime.utcnow() + timedelta(minutes=10)
#             await otp_collection.update_one(
#                 {"email": user.email},
#                 {"$set": {"otp": otp, "expiry": otp_expiry, "verified": False}},
#                 upsert=True
#             )
#             send_otp_email(user.email, otp)
#             return {"detail": "OTP sent again. Please verify your account."}

#     try:
#         # Generate OTP
#         otp = generate_otp()
#         otp_expiry = datetime.utcnow() + timedelta(minutes=10)

#         # Store OTP in the database
#         await otp_collection.insert_one({
#             "email": user.email,
#             "otp": otp,
#             "expiry": otp_expiry,
#             "verified": False
#         })

#         # Send OTP via email
#         send_otp_email(user.email, otp)

#         # Create user but set as unverified
#         user_dict = {
#             "first_name": user.first_name,
#             "last_name": user.last_name,
#             "email": user.email,
#             "language_interface": user.language_interface,
#             "language_test": user.language_test,
#             "created_at": datetime.utcnow(),
#             "verified": False  # User is not verified until OTP is validated
#         }
#         result = await user_collection.insert_one(user_dict)
#         user_id = result.inserted_id

#         logging.info(f"New user created with ID: {user_id}")

#     except Exception as e:
#         logging.error(f"Failed to create user or send OTP: {e}")
#         raise HTTPException(status_code=500, detail="User registration failed")

#     session_id = str(uuid.uuid4())
#     logging.info(f"Generated session ID: {session_id}")

#     return {"detail": "User registered successfully. Please check your email for the OTP.", "user_id": str(user_id), "session_id": session_id}

# # Endpoint to verify the OTP
# @register_app.post("/verify-otp")
# async def verify_otp(email: str, otp: str):
#     try:
#         otp_record = await otp_collection.find_one({"email": email, "otp": otp})
#         if not otp_record:
#             raise HTTPException(status_code=201, detail="Invalid OTP")

#         # Check if OTP is expired
#         if datetime.utcnow() > otp_record["expiry"]:
#             raise HTTPException(status_code=201, detail="OTP has expired")

#         # Mark user as verified
#         await user_collection.update_one({"email": email}, {"$set": {"verified": True}})
#         await otp_collection.update_one({"email": email, "otp": otp}, {"$set": {"verified": True}})

#         return {"detail": "OTP verified successfully. Your account is now verified."}

#     except Exception as e:
#         logging.error(f"Failed to verify OTP: {e}")
#         raise HTTPException(status_code=500, detail="OTP verification failed")

# # Example user model update for verification
# class User(BaseModel):
#     first_name: str
#     last_name: str
#     email: EmailStr
#     language_interface: str
#     language_test: str
#     verified: bool = False  # Add verified field to the user model

#     model_config = {
#         "populate_by_name": True,
#         "json_encoders": {ObjectId: str},
#         "arbitrary_types_allowed": True,
#     }




#Second case OTP


# import random
# import string
# import uuid
# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel, EmailStr, Field
# from pydantic_core import core_schema
# from motor.motor_asyncio import AsyncIOMotorClient
# from datetime import datetime, timedelta
# import os
# from bson import ObjectId
# from typing import List, Optional, Annotated
# import sendgrid
# from sendgrid.helpers.mail import Mail, Email, To, Content
# import logging

# # Configure logging
# logging.basicConfig(level=logging.INFO)

# # Load environment variables
# MONGO_URI = os.getenv('MONGO_URI')
# SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')



# class OTPRequest(BaseModel):
#     email: EmailStr
#     otp: str
# # Ensure the API key is loaded
# if not SENDGRID_API_KEY:
#     logging.error("SENDGRID_API_KEY is not set. Please ensure it is correctly configured.")
#     raise HTTPException(status_code=500, detail="SendGrid API key is missing.")

# # Custom ObjectId Pydantic Type
# class PyObjectId(str):
#     @classmethod
#     def __get_validators__(cls):
#         yield cls.validate

#     @classmethod
#     def validate(cls, v):
#         if not ObjectId.is_valid(v):
#             raise ValueError("Invalid ObjectId")
#         return str(v)

#     @classmethod
#     def __get_pydantic_core_schema__(cls, _source_type, _handler):
#         return core_schema.json_or_python_schema(
#             json_schema=core_schema.str_schema(),
#             python_schema=core_schema.union_schema([
#                 core_schema.is_instance_schema(ObjectId),
#                 core_schema.chain_schema([
#                     core_schema.str_schema(),
#                     core_schema.no_info_plain_validator_function(cls.validate),
#                 ]),
#             ]),
#             serialization=core_schema.plain_serializer_function_ser_schema(str),
#         )
# PydanticObjectId = Annotated[PyObjectId, Field(default_factory=PyObjectId)]

# # Pydantic models
# class UserCreate(BaseModel):
#     first_name: str
#     last_name: str
#     email: EmailStr
#     language_interface: str
#     language_test: str

# class User(BaseModel):
#     first_name: str
#     last_name: str
#     email: EmailStr
#     language_interface: str
#     language_test: str
#     verified: bool = False  # Add verified field to the user model

#     model_config = {
#         "populate_by_name": True,
#         "json_encoders": {ObjectId: str},
#         "arbitrary_types_allowed": True,
#     }

# # MongoDB client setup
# try:
#     client = AsyncIOMotorClient(MONGO_URI)
#     db = client['CEFRL']
#     user_collection = db['users']
#     otp_collection = db['otps']  # Create a collection to store OTPs
#     logging.info("Connected to MongoDB successfully.")
# except Exception as e:
#     logging.error(f"Failed to connect to MongoDB: {e}")
#     raise HTTPException(status_code=500, detail="Database connection error")

# register_app = APIRouter()

# # Function to generate a random OTP
# def generate_otp(length=6):
#     return ''.join(random.choices(string.digits, k=length))

# # Function to send OTP via email using SendGrid
# def send_otp_email(email: str, otp: str):
#     sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
#     from_email = Email("ibadk6057@gmail.com")
#     to_email = To(email)
#     subject = "Your OTP Code"
    
#     html_content = f"""
#     <html>
#     <body>
#         <h1>Your OTP Code</h1>
#         <p>Your OTP code is <strong>{otp}</strong>. Please use this code to complete your registration.</p>
#         <p>This code is valid for 10 minutes.</p>
#         <p>Best regards,<br>CEFRL Language Test</p>
#     </body>
#     </html>
#     """
    
#     content = Content("text/html", html_content)
#     mail = Mail(from_email, to_email, subject, content)
    
#     try:
#         response = sg.send(mail)
#         logging.info(f"OTP email sent successfully. Status Code: {response.status_code}")
#     except Exception as e:
#         logging.error(f"Failed to send OTP email: {e}")

# # Register a new user and send OTP if necessary
# @register_app.post("/register")
# async def register(user: UserCreate):
#     try:
#         existing_user = await user_collection.find_one({"email": user.email})
#         logging.info(f"Checked for existing user: {user.email}")
#     except Exception as e:
#         logging.error(f"Database query failed: {e}")
#         raise HTTPException(status_code=500, detail="Database query error")
    
#     if existing_user:
#         # If the user is already verified, they are considered registered
#         if existing_user.get("verified", False):
#             logging.info(f"User is already verified: {existing_user['_id']}")
#             session_id = str(uuid.uuid4())
#             logging.info(f"Generated session ID: {session_id}")
#             return {"detail": "User is already registered and verified.", "user_id": str(existing_user['_id']), "session_id": session_id}
#         else:
#             # If the user exists but is not verified, resend the OTP
#             logging.info(f"User is registered but not verified: {existing_user['_id']}")
#             otp = generate_otp()
#             otp_expiry = datetime.utcnow() + timedelta(minutes=10)
#             await otp_collection.update_one(
#                 {"email": user.email},
#                 {"$set": {"otp": otp, "expiry": otp_expiry, "verified": False}},
#                 upsert=True
#             )
#             send_otp_email(user.email, otp)
#             return {"detail": "OTP sent again. Please verify your account."}

#     # If the user is not registered at all, proceed with registration and OTP
#     try:
#         otp = generate_otp()
#         otp_expiry = datetime.utcnow() + timedelta(minutes=10)

#         await otp_collection.insert_one({
#             "email": user.email,
#             "otp": otp,
#             "expiry": otp_expiry,
#             "verified": False
#         })

#         send_otp_email(user.email, otp)

#         user_dict = {
#             "first_name": user.first_name,
#             "last_name": user.last_name,
#             "email": user.email,
#             "language_interface": user.language_interface,
#             "language_test": user.language_test,
#             "created_at": datetime.utcnow(),
#             "verified": False
#         }
#         result = await user_collection.insert_one(user_dict)
#         user_id = result.inserted_id

#         logging.info(f"New user created with ID: {user_id}")

#     except Exception as e:
#         logging.error(f"Failed to create user or send OTP: {e}")
#         raise HTTPException(status_code=500, detail="User registration failed")

#     return {"detail": "User registered successfully. Please check your email for the OTP.", "user_id": str(user_id)}
# # Endpoint to verify the OTP
# @register_app.post("/verify-otp")
# async def verify_otp(otp_request: OTPRequest):
#     email = otp_request.email
#     otp = otp_request.otp
#     logging.info(f"Received email: {email}, OTP: {otp}")
    
#     try:
#         # First, check if the user is already verified
#         user = await user_collection.find_one({"email": email})
#         if user and user.get("verified", False):
#             return {"detail": "User is already verified. No need to verify OTP again."}

#         # If the user is not verified, proceed with OTP verification
#         otp_record = await otp_collection.find_one({"email": email, "otp": otp})
#         if not otp_record:
#             raise HTTPException(status_code=201, detail="Invalid OTP")

#         # Check if OTP is expired
#         if datetime.utcnow() > otp_record["expiry"]:
#             raise HTTPException(status_code=201, detail="OTP has expired")

#         # Mark user as verified and fully registered
#         await user_collection.update_one({"email": email}, {"$set": {"verified": True}})
#         await otp_collection.update_one({"email": email, "otp": otp}, {"$set": {"verified": True}})

#         logging.info(f"User {email} has been verified and registered.")

#         return {"detail": "OTP verified successfully. Your account is now registered and verified."}

#     except Exception as e:
#         logging.error(f"Failed to verify OTP: {e}")
#         raise HTTPException(status_code=500, detail="OTP verification failed")

#####TEST RESEND OTP

# import random
# import string
# import uuid
# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel, EmailStr, Field
# from pydantic_core import core_schema
# from motor.motor_asyncio import AsyncIOMotorClient
# from datetime import datetime, timedelta
# import os
# from bson import ObjectId
# from typing import List, Optional, Annotated
# import sendgrid
# from sendgrid.helpers.mail import Mail, Email, To, Content
# import logging

# # Configure logging
# logging.basicConfig(level=logging.INFO)

# # Load environment variables
# MONGO_URI = os.getenv('MONGO_URI')
# SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')

# # Ensure the API key is loaded
# if not SENDGRID_API_KEY:
#     logging.error("SENDGRID_API_KEY is not set. Please ensure it is correctly configured.")
#     raise HTTPException(status_code=500, detail="SendGrid API key is missing.")

# # Custom ObjectId Pydantic Type
# class PyObjectId(str):
#     @classmethod
#     def __get_validators__(cls):
#         yield cls.validate

#     @classmethod
#     def validate(cls, v):
#         if not ObjectId.is_valid(v):
#             raise ValueError("Invalid ObjectId")
#         return str(v)

#     @classmethod
#     def __get_pydantic_core_schema__(cls, _source_type, _handler):
#         return core_schema.json_or_python_schema(
#             json_schema=core_schema.str_schema(),
#             python_schema=core_schema.union_schema([
#                 core_schema.is_instance_schema(ObjectId),
#                 core_schema.chain_schema([
#                     core_schema.str_schema(),
#                     core_schema.no_info_plain_validator_function(cls.validate),
#                 ]),
#             ]),
#             serialization=core_schema.plain_serializer_function_ser_schema(str),
#         )

# PydanticObjectId = Annotated[PyObjectId, Field(default_factory=PyObjectId)]

# # Pydantic models
# class UserCreate(BaseModel):
#     first_name: str
#     last_name: str
#     email: EmailStr
#     language_interface: str
#     language_test: str

# class OTPRequest(BaseModel):
#     email: EmailStr
#     otp: str

# # MongoDB client setup
# try:
#     client = AsyncIOMotorClient(MONGO_URI)
#     db = client['CEFRL']
#     otp_collection = db['otps']  # Collection to store OTPs temporarily
#     user_collection = db['users']  # Collection for user data
#     logging.info("Connected to MongoDB successfully.")
# except Exception as e:
#     logging.error(f"Failed to connect to MongoDB: {e}")
#     raise HTTPException(status_code=500, detail="Database connection error")

# register_app = APIRouter()

# # Function to generate a random OTP
# def generate_otp(length=6):
#     return ''.join(random.choices(string.digits, k=length))

# # Function to send OTP via email using SendGrid
# def send_otp_email(email: str, otp: str):
#     sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
#     from_email = Email("ibadk6057@gmail.com")
#     to_email = To(email)
#     subject = "Your OTP Code"
    
#     html_content = f"""
#     <html>
#     <body>
#         <h1>Your OTP Code</h1>
#         <p>Your OTP code is <strong>{otp}</strong>. Please use this code to complete your registration.</p>
#         <p>This code is valid for 10 minutes.</p>
#         <p>Best regards,<br>CEFRL Language Test</p>
#     </body>
#     </html>
#     """
    
#     content = Content("text/html", html_content)
#     mail = Mail(from_email, to_email, subject, content)
    
#     try:
#         response = sg.send(mail)
#         logging.info(f"OTP email sent successfully. Status Code: {response.status_code}")
#     except Exception as e:
#         logging.error(f"Failed to send OTP email: {e}")

# # Initiate registration and send OTP if necessary
# @register_app.post("/register")
# async def register(user: UserCreate):
#     try:
#         existing_user = await user_collection.find_one({"email": user.email})
#         logging.info(f"Checked for existing user: {user.email}")

#         session_id = str(uuid.uuid4())  # Generate a new session ID every time

#         if existing_user:
#             user_id = str(existing_user['_id'])
#             # If the user is already registered and verified, return with a new session ID
#             if existing_user.get("verified", False):
#                 logging.info(f"User is already verified: {user_id}")
#                 return {
#                     "detail": "User is already registered and verified. No need to generate OTP.",
#                     "user_id": user_id,
#                     "session_id": session_id
#                 }
#             else:
#                 return {
#                     "detail": "User is already registered but not verified. Please verify your account.",
#                     "user_id": user_id,
#                     "session_id": session_id
#                 }

#         # If the user is not registered, proceed with OTP generation
#         otp = generate_otp()
#         otp_expiry = datetime.utcnow() + timedelta(minutes=10)

#         otp_record = {
#             "email": user.email,
#             "otp": otp,
#             "expiry": otp_expiry,
#             "user_data": user.dict(),
#             "session_id": session_id  # Store the session ID with the OTP
#         }

#         result = await otp_collection.insert_one(otp_record)
#         user_id = str(result.inserted_id)

#         send_otp_email(user.email, otp)

#     except Exception as e:
#         logging.error(f"Failed to initiate registration: {e}")
#         raise HTTPException(status_code=500, detail="User registration initiation failed")

#     return {
#         "detail": "OTP sent successfully. Please verify your account to complete registration.",
#         "user_id": user_id,
#         "session_id": session_id
#     }

# # Verify OTP and complete registration
# @register_app.post("/verify-otp")
# async def verify_otp(otp_request: OTPRequest):
#     email = otp_request.email
#     otp = otp_request.otp
#     logging.info(f"Received email: {email}, OTP: {otp}")
    
#     try:
#         # Verify OTP
#         otp_record = await otp_collection.find_one({"email": email, "otp": otp})
#         if not otp_record:
#             raise HTTPException(status_code=400, detail="Invalid OTP")

#         # Check if OTP is expired
#         if datetime.utcnow() > otp_record["expiry"]:
#             raise HTTPException(status_code=400, detail="OTP has expired")

#         # Register the user and mark them as verified
#         user_data = otp_record["user_data"]
#         user_data["verified"] = True
#         user_data["created_at"] = datetime.utcnow()

#         result = await user_collection.insert_one(user_data)
#         user_id = str(result.inserted_id)

#         # Delete the OTP record after successful registration
#         await otp_collection.delete_one({"email": email, "otp": otp})

#         logging.info(f"User {email} has been verified and registered with ID: {user_id}.")

#         return {
#             "detail": "OTP verified successfully. Your account is now registered and verified.",
#             "user_id": user_id,
#             "session_id": otp_record["session_id"]  # Return the session ID used during registration
#         }

#     except Exception as e:
#         logging.error(f"Failed to verify OTP: {e}")
#         raise HTTPException(status_code=500, detail="OTP verification failed")

# # Resend OTP if expired
# @register_app.post("/resend-otp")
# async def resend_otp(email: EmailStr):
#     try:
#         otp_record = await otp_collection.find_one({"email": email})
        
#         if not otp_record:
#             raise HTTPException(status_code=404, detail="No OTP record found. Please register first.")

#         # Check if the OTP is still valid
#         if datetime.utcnow() < otp_record["expiry"]:
#             remaining_time = otp_record["expiry"] - datetime.utcnow()
#             return {
#                 "detail": f"OTP is still valid. Please use the existing OTP. Time remaining: {remaining_time}",
#                 "user_id": str(otp_record['_id']),
#                 "session_id": otp_record["session_id"]
#             }

#         # Generate a new OTP and update the expiry
#         new_otp = generate_otp()
#         new_expiry = datetime.utcnow() + timedelta(minutes=10)

#         await otp_collection.update_one(
#             {"email": email},
#             {"$set": {"otp": new_otp, "expiry": new_expiry}}
#         )

#         send_otp_email(email, new_otp)

#         logging.info(f"Resent OTP for email: {email}")

#         return {
#             "detail": "New OTP has been sent successfully.",
#             "user_id": str(otp_record['_id']),
#             "session_id": otp_record["session_id"]
#         }

#     except Exception as e:
#         logging.error(f"Failed to resend OTP: {e}")
#         raise HTTPException(status_code=500, detail="Failed to resend OTP")
