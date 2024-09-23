from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import os
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import HTTPException, APIRouter

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

# Initialize FastAPI app
admin_login_app = APIRouter()


ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

class Login(BaseModel):
    email: str
    password: str

@admin_login_app.post("/admin/login")
async def admin_login(form_data:Login):
    if form_data.email != ADMIN_EMAIL or form_data.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=201, detail="Invalid credentials")
    if form_data.email == ADMIN_EMAIL and form_data.password == ADMIN_PASSWORD:
        return JSONResponse(content={"detail": "success"}, status_code=200)
    return JSONResponse(content="Some error occure" , status_code=201)

# # # Protected route example

# @admin_login_app.get("/admin/dashboard")
# async def read_admin_dashboard(token: str ):
#     if token != "fake-jwt-token":
#         raise HTTPException(status_code=201, detail="Invalid token")
#     return {"message": "Welcome to the admin dashboard"}

