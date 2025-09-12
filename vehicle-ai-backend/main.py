# # main.py - Complete file with ML integration and WebSocket handling
# from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Response
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse
# import asyncio
# import json
# from typing import List
# import uvicorn
# import logging
# import time
# import sys
# from pydantic import BaseModel
#
# # Fix Windows console encoding issues
# if sys.platform == "win32":
#     import codecs
#
#     try:
#         sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
#         sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())
#     except:
#         pass  # Ignore if already configured
#
# # Import routers
# from routers import climate, infotainment, lights, seats, nlp
# from models.vehicle_state import VehicleStateManager
# from services.websocket_manager import ConnectionManager
# from services.ml_parser_service import MLParserService
# from config import settings
#
# # Configure logging without emojis
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.StreamHandler(),
#         logging.FileHandler('vehicle_backend.log', encoding='utf-8')
#     ]
# )
# logger = logging.getLogger("vehicle-backend")
#
# # Initialize FastAPI app
# app = FastAPI(
#     title="Vehicle AI Backend",
#     description="Backend API for Conversational Vehicle AI",
#     version="1.0.0",
#     debug=settings.DEBUG
# )
#
# # CORS middleware for React frontend
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.ALLOWED_ORIGINS,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
#
# # Add request logging middleware
# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     start_time = time.time()
#
#     # Log incoming request
#     logger.info(f"Request: {request.method} {request.url.path} - Client: {request.client.host}")
#
#     # Log request body for POST requests
#     if request.method == "POST":
#         try:
#             body = await request.body()
#             if body:
#                 logger.info(f"Request body: {body.decode('utf-8')[:500]}")
#
#             # Re-create request with body for FastAPI to process
#             async def receive():
#                 return {"type": "http.request", "body": body}
#
#             request._receive = receive
#         except Exception as e:
#             logger.error(f"Error reading request body: {e}")
#
#     try:
#         response = await call_next(request)
#         process_time = time.time() - start_time
#         logger.info(f"Response: {response.status_code} - Time: {process_time:.3f}s")
#         return response
#     except Exception as e:
#         process_time = time.time() - start_time
#         logger.error(f"Request failed: {str(e)} - Time: {process_time:.3f}s")
#         # Return a proper error response
#         return JSONResponse(
#             status_code=500,
#             content={"detail": f"Internal server error: {str(e)}"}
#         )
#
#
# # Initialize managers
# vehicle_state = VehicleStateManager()
# connection_manager = ConnectionManager()
#
# # Make services available to routers
# app.state.vehicle_state = vehicle_state
# app.state.connection_manager = connection_manager
#
# # Include routers
# app.include_router(climate.router, prefix="/api/climate", tags=["climate"])
# app.include_router(infotainment.router, prefix="/api/infotainment", tags=["infotainment"])
# app.include_router(lights.router, prefix="/api/lights", tags=["lights"])
# app.include_router(seats.router, prefix="/api/seats", tags=["seats"])
# app.include_router(nlp.router, prefix="/api/nlp", tags=["nlp"])
#
#
# @app.get("/")
# async def root():
#     logger.info("Root endpoint accessed")
#     return {"message": "Vehicle AI Backend is running!", "status": "healthy"}
#
#
# # Add this endpoint in main.py after the root endpoint
#
# @app.get("/health")
# async def health_check():
#     """Health check endpoint for monitoring"""
#     return {
#         "status": "healthy",
#         "timestamp": time.time(),
#         "services": {
#             "vehicle_state": "healthy" if vehicle_state else "unavailable",
#             "websocket_manager": "healthy" if connection_manager else "unavailable"
#         },
#         "version": "1.0.0"
#     }
#
#
# @app.get("/api/status")
# async def get_status():
#     """Get overall vehicle status"""
#     logger.info("Status endpoint accessed")
#     try:
#         # Get the current vehicle state
#         current_state = vehicle_state.get_all_states()
#
#         return {
#             "status": "running",
#             "vehicle_state": current_state,  # This is the key the test is looking for
#             "connections": len(connection_manager.active_connections) if connection_manager else 0,
#             "timestamp": time.time()
#         }
#     except Exception as e:
#         logger.error(f"Error getting status: {e}")
#         return JSONResponse(
#             status_code=500,
#             content={"detail": f"Error getting status: {str(e)}"}
#         )
#
#
# # async def process_voice_command(text: str):
# #     """Process voice command through ML service and execute actions"""
# #     logger.info(f"Processing voice command via WebSocket: '{text}'")
# #
# #     try:
# #         # Initialize ML parser service
# #         ml_service = MLParserService()
# #
# #         # Parse command through ML service
# #         logger.info("Sending command to ML service...")
# #         ml_result = await ml_service.parse_command(text)
# #
# #         logger.info(f"ML service returned: {ml_result}")
# #
# #         # Execute the action if it's not unknown and confidence is good
# #         execution_result = None
# #
# #         if ml_result.get("action") != "unknown" and ml_result.get("confidence", 0) > 0.3:
# #             try:
# #                 # Execute the command on vehicle state
# #                 execution_result = await vehicle_state.execute_command(
# #                     ml_result["action"],
# #                     ml_result.get("parameters", {})
# #                 )
# #
# #                 logger.info(f"Command execution result: {execution_result}")
# #
# #             except Exception as e:
# #                 logger.error(f"Error executing command: {e}")
# #                 execution_result = {"success": False, "error": str(e)}
# #
# #         # Prepare response
# #         response = {
# #             "type": "command_response",
# #             "original_text": text,
# #             "action": ml_result.get("action", "unknown"),
# #             "confidence": ml_result.get("confidence", 0.0),
# #             "parameters": ml_result.get("parameters", {}),
# #             "success": execution_result.get("success", False) if execution_result else False,
# #             "execution_result": execution_result,
# #             "timestamp": time.time()
# #         }
# #
# #         # Add response text based on success
# #         if execution_result and execution_result.get("success"):
# #             response["response_text"] = f"Successfully executed: {ml_result['action']}"
# #         elif ml_result.get("action") == "unknown":
# #             response["response_text"] = "Sorry, I didn't understand that command"
# #         else:
# #             response["response_text"] = "Command understood but execution failed"
# #
# #         logger.info(f"Returning WebSocket response: {response}")
# #         return response
# #
# #     except Exception as e:
# #         logger.error(f"Error in voice command processing: {e}", exc_info=True)
# #         return {
# #             "type": "command_response",
# #             "original_text": text,
# #             "action": "error",
# #             "confidence": 0.0,
# #             "success": False,
# #             "error": str(e),
# #             "response_text": f"Error processing command: {str(e)}",
# #             "timestamp": time.time()
# #         }
#
# async def process_voice_command(text: str):
#     """Process voice command - temporary fallback without ML service"""
#     logger.info(f"Processing voice command via WebSocket: '{text}' (fallback mode)")
#
#     # Temporary fallback response
#     return {
#         "type": "command_response",
#         "original_text": text,
#         "action": "test_fallback",
#         "confidence": 0.5,
#         "parameters": {},
#         "success": False,
#         "execution_result": None,
#         "response_text": f"Fallback: I heard '{text}' but ML service is disabled",
#         "timestamp": time.time()
#     }
#
#
# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     logger.info(f"WebSocket connection attempt from {websocket.client.host}")
#     await connection_manager.connect(websocket)
#     try:
#         while True:
#             # Receive messages from client
#             data = await websocket.receive_text()
#             message = json.loads(data)
#             logger.info(f"WebSocket message received: {message}")
#
#             # Process the message based on type
#             if message.get("type") == "voice_command":
#                 # Process through NLP service
#                 response = await process_voice_command(message.get("text", ""))
#                 await connection_manager.send_personal_message(json.dumps(response), websocket)
#
#                 # If command was successful, broadcast state update to all clients
#                 if response.get("success"):
#                     state_update = {
#                         "type": "state_update",
#                         "data": vehicle_state.get_all_states(),
#                         "timestamp": time.time()
#                     }
#                     await connection_manager.broadcast(json.dumps(state_update))
#
#             elif message.get("type") == "get_state":
#                 # Send current vehicle state
#                 state = vehicle_state.get_all_states()
#                 await connection_manager.send_personal_message(json.dumps({
#                     "type": "state_update",
#                     "data": state,
#                     "timestamp": time.time()
#                 }), websocket)
#
#             elif message.get("type") == "manual_control":
#                 # Handle manual control from frontend
#                 try:
#                     system = message.get("system")
#                     action = message.get("action")
#                     parameters = message.get("parameters", {})
#
#                     execution_result = await vehicle_state.execute_command(action, parameters)
#
#                     # Send response back to client
#                     response = {
#                         "type": "manual_control_response",
#                         "system": system,
#                         "action": action,
#                         "success": execution_result.get("success", False),
#                         "execution_result": execution_result,
#                         "timestamp": time.time()
#                     }
#                     await connection_manager.send_personal_message(json.dumps(response), websocket)
#
#                     # Broadcast state update if successful
#                     if execution_result.get("success"):
#                         state_update = {
#                             "type": "state_update",
#                             "data": vehicle_state.get_all_states(),
#                             "timestamp": time.time()
#                         }
#                         await connection_manager.broadcast(json.dumps(state_update))
#
#                 except Exception as e:
#                     logger.error(f"Error processing manual control: {e}")
#                     error_response = {
#                         "type": "manual_control_response",
#                         "success": False,
#                         "error": str(e),
#                         "timestamp": time.time()
#                     }
#                     await connection_manager.send_personal_message(json.dumps(error_response), websocket)
#
#             elif message.get("type") == "ping":
#                 # Handle ping for heartbeat
#                 pong_response = {
#                     "type": "pong",
#                     "timestamp": time.time()
#                 }
#                 await connection_manager.send_personal_message(json.dumps(pong_response), websocket)
#
#             # Always broadcast general client messages (except ping)
#             if message.get("type") != "ping":
#                 await connection_manager.broadcast(json.dumps({
#                     "type": "client_message",
#                     "data": message,
#                     "timestamp": time.time()
#                 }))
#
#     except WebSocketDisconnect:
#         logger.info(f"WebSocket disconnected from {websocket.client.host}")
#         connection_manager.disconnect(websocket)
#     except Exception as e:
#         logger.error(f"WebSocket error: {e}")
#         connection_manager.disconnect(websocket)
#
#
# # Startup event
# @app.on_event("startup")
# async def startup_event():
#     logger.info("Vehicle AI Backend starting up...")
#     logger.info(f"Debug mode: {settings.DEBUG}")
#     logger.info(f"Allowed origins: {settings.ALLOWED_ORIGINS}")
#     logger.info(f"ML Service URL: {settings.ML_SERVICE_URL}")
#
#
# # Shutdown event
# @app.on_event("shutdown")
# async def shutdown_event():
#     logger.info("Vehicle AI Backend shutting down...")
#     if connection_manager:
#         await connection_manager.shutdown()
#
#
# if __name__ == "__main__":
#     logger.info("Starting Vehicle AI Backend...")
#     uvicorn.run(
#         "main:app",
#         host=settings.HOST,
#         port=settings.PORT,
#         reload=settings.DEBUG,
#         log_level="info"
#     )










# main.py - Complete file with ML integration and WebSocket handling
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import json
from typing import List
import uvicorn
import logging
import time
import sys
from pydantic import BaseModel
from typing import Dict, Any, Optional, Union

# Fix Windows console encoding issues
if sys.platform == "win32":
    import codecs

    try:
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())
    except:
        pass  # Ignore if already configured

# Import routers
from routers import climate, infotainment, lights, seats, nlp
from models.vehicle_state import VehicleStateManager
from services.websocket_manager import ConnectionManager
from services.ml_parser_service import MLParserService
from config import settings



# Configure logging without emojis
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('vehicle_backend.log', encoding='utf-8')
    ]
)
logger = logging.getLogger("vehicle-backend")

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


def translate_backend_to_frontend_state(backend_state: Dict[str, Any]) -> Dict[str, Any]:
    """Translate backend state structure to match frontend expectations"""
    translated = {}

    # Translate climate
    if "climate" in backend_state:
        translated["climate"] = {
            "temperature": backend_state["climate"].get("temperature", 22),
            "temp": backend_state["climate"].get("temperature", 22),  # Frontend uses 'temp'
            "ac_enabled": backend_state["climate"].get("ac_enabled", False),
            "fan_speed": backend_state["climate"].get("fan_speed", 3),
            "heating_enabled": backend_state["climate"].get("heating_enabled", False),
            "auto_mode": backend_state["climate"].get("auto_mode", True),
            "recirculation": backend_state["climate"].get("recirculation", False)
        }

    # Translate infotainment to include both formats
    if "infotainment" in backend_state:
        translated["infotainment"] = backend_state["infotainment"]
        translated["media"] = {  # Frontend uses 'media'
            "volume": backend_state["infotainment"].get("volume", 50),
            "playing": backend_state["infotainment"].get("playing", False),
            "on": backend_state["infotainment"].get("playing", False),  # Frontend uses 'on'
            "source": backend_state["infotainment"].get("source", "radio"),
            "station": backend_state["infotainment"].get("station", "FM 101.5"),
            "track": backend_state["infotainment"].get("track"),
            "artist": backend_state["infotainment"].get("artist"),
            "muted": backend_state["infotainment"].get("muted", False)
        }

    # Lights structure matches
    if "lights" in backend_state:
        translated["lights"] = {
            "interior_lights": backend_state["lights"].get("interior_lights", True),
            "on": backend_state["lights"].get("interior_lights", True),  # Frontend uses 'on'
            "ambient_lights": backend_state["lights"].get("ambient_lights", True),
            "reading_lights": backend_state["lights"].get("reading_lights", False),
            "brightness": backend_state["lights"].get("brightness", 80),
            "ambient_color": backend_state["lights"].get("ambient_color", "white")
        }

    # Translate seats
    if "seats" in backend_state:
        translated["seats"] = {
            "driver_heating": backend_state["seats"].get("driver_heating", False),
            "heatOn": backend_state["seats"].get("driver_heating", False),  # Frontend uses 'heatOn'
            "passenger_heating": backend_state["seats"].get("passenger_heating", False),
            "driver_massage": backend_state["seats"].get("driver_massage", False),
            "passenger_massage": backend_state["seats"].get("passenger_massage", False),
            "driver_position": backend_state["seats"].get("driver_position", {"height": 50, "tilt": 50, "lumbar": 50}),
            "passenger_position": backend_state["seats"].get("passenger_position",
                                                             {"height": 50, "tilt": 50, "lumbar": 50}),
            "position": 3  # Default position for frontend slider
        }

    translated["last_updated"] = backend_state.get("last_updated", time.time())

    return translated



# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # Log incoming request
    logger.info(f"Request: {request.method} {request.url.path} - Client: {request.client.host}")

    # Log request body for POST requests
    if request.method == "POST":
        try:
            body = await request.body()
            if body:
                logger.info(f"Request body: {body.decode('utf-8')[:500]}")

            # Re-create request with body for FastAPI to process
            async def receive():
                return {"type": "http.request", "body": body}

            request._receive = receive
        except Exception as e:
            logger.error(f"Error reading request body: {e}")

    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(f"Response: {response.status_code} - Time: {process_time:.3f}s")
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"Request failed: {str(e)} - Time: {process_time:.3f}s")
        # Return a proper error response
        return JSONResponse(
            status_code=500,
            content={"detail": f"Internal server error: {str(e)}"}
        )


# Initialize managers
vehicle_state = VehicleStateManager()
connection_manager = ConnectionManager()

# Make services available to routers
app.state.vehicle_state = vehicle_state
app.state.connection_manager = connection_manager

# Include routers
app.include_router(climate.router, prefix="/api/climate", tags=["climate"])
app.include_router(infotainment.router, prefix="/api/infotainment", tags=["infotainment"])
app.include_router(lights.router, prefix="/api/lights", tags=["lights"])
app.include_router(seats.router, prefix="/api/seats", tags=["seats"])
app.include_router(nlp.router, prefix="/api/nlp", tags=["nlp"])


@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Vehicle AI Backend is running!", "status": "healthy"}


# Add this endpoint in main.py after the root endpoint

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "services": {
            "vehicle_state": "healthy" if vehicle_state else "unavailable",
            "websocket_manager": "healthy" if connection_manager else "unavailable"
        },
        "version": "1.0.0"
    }


@app.get("/api/status")
async def get_status():
    """Get overall vehicle status"""
    logger.info("Status endpoint accessed")
    try:
        # Get the current vehicle state
        current_state = vehicle_state.get_all_states()

        return {
            "status": "running",
            "vehicle_state": current_state,  # This is the key the test is looking for
            "connections": len(connection_manager.active_connections) if connection_manager else 0,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error getting status: {str(e)}"}
        )


# async def process_voice_command(text: str):
#     """Process voice command through ML service and execute actions"""
#     logger.info(f"Processing voice command via WebSocket: '{text}'")
#
#     try:
#         # Initialize ML parser service
#         ml_service = MLParserService()
#
#         # Parse command through ML service
#         logger.info("Sending command to ML service...")
#         ml_result = await ml_service.parse_command(text)
#
#         logger.info(f"ML service returned: {ml_result}")
#
#         # Execute the action if it's not unknown and confidence is good
#         execution_result = None
#
#         if ml_result.get("action") != "unknown" and ml_result.get("confidence", 0) > 0.3:
#             try:
#                 # Execute the command on vehicle state
#                 execution_result = await vehicle_state.execute_command(
#                     ml_result["action"],
#                     ml_result.get("parameters", {})
#                 )
#
#                 logger.info(f"Command execution result: {execution_result}")
#
#             except Exception as e:
#                 logger.error(f"Error executing command: {e}")
#                 execution_result = {"success": False, "error": str(e)}
#
#         # Prepare response
#         response = {
#             "type": "command_response",
#             "original_text": text,
#             "action": ml_result.get("action", "unknown"),
#             "confidence": ml_result.get("confidence", 0.0),
#             "parameters": ml_result.get("parameters", {}),
#             "success": execution_result.get("success", False) if execution_result else False,
#             "execution_result": execution_result,
#             "timestamp": time.time()
#         }
#
#         # Add response text based on success
#         if execution_result and execution_result.get("success"):
#             response["response_text"] = f"Successfully executed: {ml_result['action']}"
#         elif ml_result.get("action") == "unknown":
#             response["response_text"] = "Sorry, I didn't understand that command"
#         else:
#             response["response_text"] = "Command understood but execution failed"
#
#         logger.info(f"Returning WebSocket response: {response}")
#         return response
#
#     except Exception as e:
#         logger.error(f"Error in voice command processing: {e}", exc_info=True)
#         return {
#             "type": "command_response",
#             "original_text": text,
#             "action": "error",
#             "confidence": 0.0,
#             "success": False,
#             "error": str(e),
#             "response_text": f"Error processing command: {str(e)}",
#             "timestamp": time.time()
#         }

async def process_voice_command(text: str):
    """Process voice command - temporary fallback without ML service"""
    logger.info(f"Processing voice command via WebSocket: '{text}' (fallback mode)")

    # Temporary fallback response
    return {
        "type": "command_response",
        "original_text": text,
        "action": "test_fallback",
        "confidence": 0.5,
        "parameters": {},
        "success": False,
        "execution_result": None,
        "response_text": f"Fallback: I heard '{text}' but ML service is disabled",
        "timestamp": time.time()
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    logger.info(f"WebSocket connection attempt from {websocket.client.host}")
    await connection_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            logger.info(f"WebSocket message received: {message}")

            if message.get("type") == "voice_command":
                response = await process_voice_command(message.get("text", ""))
                await connection_manager.send_personal_message(json.dumps(response), websocket)

                if response.get("success"):
                    # Translate state before broadcasting
                    backend_state = vehicle_state.get_all_states()
                    frontend_state = translate_backend_to_frontend_state(backend_state)

                    state_update = {
                        "type": "state_update",
                        "data": frontend_state,
                        "timestamp": time.time()
                    }
                    await connection_manager.broadcast(json.dumps(state_update))

            elif message.get("type") == "get_state":
                # Send translated state
                backend_state = vehicle_state.get_all_states()
                frontend_state = translate_backend_to_frontend_state(backend_state)

                await connection_manager.send_personal_message(json.dumps({
                    "type": "state_update",
                    "data": frontend_state,
                    "timestamp": time.time()
                }), websocket)

            elif message.get("type") == "manual_control":
                try:
                    system = message.get("system")
                    action = message.get("action")
                    parameters = message.get("parameters", {})

                    execution_result = await vehicle_state.execute_command(action, parameters)

                    response = {
                        "type": "manual_control_response",
                        "system": system,
                        "action": action,
                        "success": execution_result.get("success", False),
                        "execution_result": execution_result,
                        "timestamp": time.time()
                    }
                    await connection_manager.send_personal_message(json.dumps(response), websocket)

                    if execution_result.get("success"):
                        # Translate state before broadcasting
                        backend_state = vehicle_state.get_all_states()
                        frontend_state = translate_backend_to_frontend_state(backend_state)

                        state_update = {
                            "type": "state_update",
                            "data": frontend_state,
                            "timestamp": time.time()
                        }
                        await connection_manager.broadcast(json.dumps(state_update))

                except Exception as e:
                    logger.error(f"Error processing manual control: {e}")
                    error_response = {
                        "type": "manual_control_response",
                        "success": False,
                        "error": str(e),
                        "timestamp": time.time()
                    }
                    await connection_manager.send_personal_message(json.dumps(error_response), websocket)

            elif message.get("type") in ["ping", "pong"]:
                await connection_manager.broadcast(json.dumps(message))

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected from {websocket.client.host}")
        connection_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        connection_manager.disconnect(websocket)


# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Vehicle AI Backend starting up...")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Allowed origins: {settings.ALLOWED_ORIGINS}")
    logger.info(f"ML Service URL: {settings.ML_SERVICE_URL}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Vehicle AI Backend shutting down...")
    if connection_manager:
        await connection_manager.shutdown()


if __name__ == "__main__":
    logger.info("Starting Vehicle AI Backend...")
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )