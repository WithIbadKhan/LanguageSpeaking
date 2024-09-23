from fastapi import WebSocket
from typing import Dict
class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}  # {userid: websocket_connection}
    async def connect(self, websocket: WebSocket, userid: str):
        try:
            await websocket.accept()
            self.active_connections[userid] = websocket
            print(f"User {userid} connected")
            print("Active connections:", self.active_connections)
        except Exception as e:
            print(f"Error connecting user {userid}: {e}")
            await websocket.close()
    async def disconnect(self, userid: str):
        try:
            websocket = self.active_connections.pop(userid, None)
            if websocket:
                await websocket.close()
                print(f"Connection closed for userid: {userid}")
            else:
                print(f"Connection not found for userid: {userid}")
        except Exception as e:
            print(f"Error disconnecting user {userid}: {e}")
        
    async def send_json_message(self, message: dict, userid: str):
        try:
            websocket = self.active_connections.get(userid)
            if websocket:
                await websocket.send_json(message)
                print("Socket message sent")
            else:
                print(f"Connection not found for userid: {userid}")
        except Exception as e:
            print(f"Error sending JSON message to {userid}: {e}")