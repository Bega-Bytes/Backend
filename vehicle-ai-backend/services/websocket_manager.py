import json
import asyncio
from typing import List
from fastapi import WebSocket

class ConnectionManager:
    """Manages WebSocket connections for real-time communication"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"Client connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"Client disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific client"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            print(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        """Broadcast a message to all connected clients"""
        disconnected_clients = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"Error broadcasting to client: {e}")
                disconnected_clients.append(connection)
        
        # Remove disconnected clients
        for client in disconnected_clients:
            self.disconnect(client)
    
    async def broadcast_state_update(self, state_data: dict):
        """Broadcast vehicle state update to all clients"""
        message = {
            "type": "state_update",
            "data": state_data,
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.broadcast(json.dumps(message))
    
    async def broadcast_command_result(self, command: str, result: dict, success: bool = True):
        """Broadcast command execution result to all clients"""
        message = {
            "type": "command_result",
            "command": command,
            "result": result,
            "success": success,
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.broadcast(json.dumps(message))
    
    async def send_chat_message(self, message: str, sender: str = "system"):
        """Send a chat message to all clients"""
        chat_message = {
            "type": "chat_message",
            "sender": sender,
            "message": message,
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.broadcast(json.dumps(chat_message))