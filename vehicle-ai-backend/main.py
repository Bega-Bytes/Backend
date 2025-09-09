from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import json
from typing import List
import uvicorn

# Import routers
from routers import climate, infotainment, lights, seats, nlp
from models.vehicle_state import VehicleStateManager
from services.websocket_manager import ConnectionManager
from config import settings

# Initialize FastAPI app
app = FastAPI(
    title="Vehicle AI Backend",
    description="Backend API for Conversational Vehicle AI",
    version="1.0.0",
    debug=settings.DEBUG
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers
vehicle_state = VehicleStateManager()
connection_manager = ConnectionManager()

# Include routers
app.include_router(climate.router, prefix="/api/climate", tags=["climate"])
app.include_router(infotainment.router, prefix="/api/infotainment", tags=["infotainment"])
app.include_router(lights.router, prefix="/api/lights", tags=["lights"])
app.include_router(seats.router, prefix="/api/seats", tags=["seats"])
app.include_router(nlp.router, prefix="/api/nlp", tags=["nlp"])

@app.get("/")
async def root():
    return {"message": "Vehicle AI Backend is running!"}

@app.get("/api/status")
async def get_status():
    """Get overall vehicle status"""
    return {
        "status": "running",
        "vehicle_state": vehicle_state.get_all_states(),
        "connected_clients": len(connection_manager.active_connections)
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await connection_manager.connect(websocket)
    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Process the message based on type
            if message.get("type") == "voice_command":
                # This will be processed by NLP service
                response = await process_voice_command(message.get("text", ""))
                await connection_manager.send_personal_message(json.dumps(response), websocket)
            
            elif message.get("type") == "get_state":
                # Send current vehicle state
                state = vehicle_state.get_all_states()
                await connection_manager.send_personal_message(json.dumps({
                    "type": "state_update",
                    "data": state
                }), websocket)
            
            # Broadcast to all connected clients
            await connection_manager.broadcast(json.dumps({
                "type": "client_message",
                "data": message
            }))
            
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)

async def process_voice_command(text: str):
    """Process voice command through NLP"""
    # This will integrate with your NLP service
    return {
        "type": "command_response",
        "original_text": text,
        "processed": True,
        "timestamp": asyncio.get_event_loop().time()
    }

# Make vehicle_state and connection_manager available to routers
app.state.vehicle_state = vehicle_state
app.state.connection_manager = connection_manager

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)