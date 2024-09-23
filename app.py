#new
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from socket_manager.socket_router import socket_app
from openai_code.routers import openai_analyze
from auth.register import register_app
from db.display_text import display_app
from Admin.invitatioEmail import InviteByAdmin_app
from Admin.historyUser import UserData_Admin
from Admin.admin_login import admin_login_app
from Admin.dashboardAnalysis import DashboardData

app = FastAPI()

app.include_router(socket_app)
app.include_router(openai_analyze)
app.include_router(register_app)
app.include_router(display_app)
app.include_router(InviteByAdmin_app)
app.include_router(UserData_Admin)
app.include_router(admin_login_app)
app.include_router(DashboardData)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
print("Server starting...")
if __name__ == '__main__':
    import uvicorn
    uvicorn.run("app:app",reload=True)