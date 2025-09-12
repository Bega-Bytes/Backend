# # # # routers/nlp.py - Complete file with ML integration
# # # from fastapi import APIRouter, Request, HTTPException
# # # from pydantic import BaseModel
# # # from services.ml_parser_service import MLParserService
# # # import logging
# # # import time
# # # import json
# # # from typing import Optional, Dict, Any
# # #
# # # logger = logging.getLogger("nlp-router")
# # # router = APIRouter()
# # #
# # #
# # # class VoiceCommand(BaseModel):
# # #     text: str
# # #     timestamp: Optional[float] = None
# # #
# # #
# # # class VoiceResponse(BaseModel):
# # #     success: bool
# # #     action: str
# # #     confidence: float
# # #     parameters: Dict[str, Any]
# # #     response_text: str
# # #     timestamp: float
# # #     execution_result: Optional[Dict[str, Any]] = None
# # #     error: Optional[str] = None
# # #
# # #
# # # @router.get("/test")
# # # async def test_nlp():
# # #     """Test endpoint for NLP service"""
# # #     logger.info("NLP test endpoint accessed")
# # #     return {
# # #         "status": "healthy",
# # #         "message": "NLP router is working",
# # #         "ml_service_url": "http://localhost:8001",
# # #         "timestamp": time.time()
# # #     }
# # #
# # #
# # # @router.post("/process-voice", response_model=VoiceResponse)
# # # async def process_voice_command(command: VoiceCommand, request: Request):
# # #     """Process voice command using ML service"""
# # #     if not command.timestamp:
# # #         command.timestamp = time.time()
# # #
# # #     logger.info(f"Processing voice command: '{command.text}'")
# # #
# # #     try:
# # #         # Initialize ML parser service
# # #         ml_service = MLParserService()
# # #
# # #         # Parse command using ML service
# # #         ml_result = await ml_service.parse_command(command.text)
# # #
# # #         # Get vehicle state and connection manager from app state
# # #         vehicle_state = request.app.state.vehicle_state
# # #         connection_manager = request.app.state.connection_manager
# # #
# # #         # Execute the action based on ML result
# # #         execution_result = await execute_vehicle_action(
# # #             ml_result, vehicle_state, connection_manager
# # #         )
# # #
# # #         return VoiceResponse(
# # #             success=True,
# # #             action=ml_result.get("action", "unknown"),
# # #             confidence=ml_result.get("confidence", 0.0),
# # #             parameters=ml_result.get("parameters", {}),
# # #             response_text=f"Executed: {command.text}",
# # #             timestamp=time.time(),
# # #             execution_result=execution_result
# # #         )
# # #
# # #     except Exception as e:
# # #         logger.error(f"Error processing voice command: {e}")
# # #         return VoiceResponse(
# # #             success=False,
# # #             action="error",
# # #             confidence=0.0,
# # #             parameters={},
# # #             response_text=f"Failed to process: {command.text}",
# # #             timestamp=time.time(),
# # #             error=str(e)
# # #         )
# # #
# # #
# # # async def execute_vehicle_action(ml_result: Dict, vehicle_state, connection_manager) -> Dict:
# # #     """Execute vehicle action based on ML parsing result"""
# # #     action = ml_result.get("action", "")
# # #     parameters = ml_result.get("parameters", {})
# # #
# # #     logger.info(f"Executing action: {action} with parameters: {parameters}")
# # #
# # #     try:
# # #         # Map ML actions to VehicleStateManager actions
# # #         action_mapping = {
# # #             # Climate actions
# # #             "climate_set": "climate_set_temperature",
# # #             "climate_turn_on": "climate_turn_on_ac",
# # #             "climate_turn_off": "climate_turn_off_ac",
# # #             "climate_increase": "climate_increase_temperature",
# # #             "climate_decrease": "climate_decrease_temperature",
# # #
# # #             # Lights actions
# # #             "lights_turn_on": "lights_turn_on",
# # #             "lights_turn_off": "lights_turn_off",
# # #             "lights_brighten": "lights_brighten",
# # #             "lights_dim": "lights_dim",
# # #
# # #             # Seats actions
# # #             "seats_heat_on": "seats_heat_on",
# # #             "seats_heat_off": "seats_heat_off",
# # #             "seats_adjust": "seats_adjust_position",
# # #
# # #             # Infotainment actions
# # #             "infotainment_play": "infotainment_play",
# # #             "infotainment_pause": "infotainment_pause",
# # #             "infotainment_volume_up": "infotainment_volume_up",
# # #             "infotainment_volume_down": "infotainment_volume_down",
# # #             "infotainment_set_volume": "infotainment_set_volume"
# # #         }
# # #
# # #         # Map the action
# # #         mapped_action = action_mapping.get(action, action)
# # #
# # #         # For climate_set, ensure we have temperature parameter
# # #         if mapped_action == "climate_set_temperature":
# # #             if "temperature" not in parameters:
# # #                 # Try to extract from other possible keys
# # #                 temp = parameters.get("temp", parameters.get("value", 22))
# # #                 parameters = {"temperature": temp}
# # #
# # #         # For seats actions, add seat parameter if missing
# # #         if mapped_action.startswith("seats_"):
# # #             if "seat" not in parameters:
# # #                 parameters["seat"] = "driver"  # Default to driver
# # #
# # #         # Execute the command using VehicleStateManager's execute_command method
# # #         result = await vehicle_state.execute_command(mapped_action, parameters)
# # #
# # #         # Broadcast state update via WebSocket if successful
# # #         if result.get("success", True):  # Some results might not have success field
# # #             try:
# # #                 updated_state = vehicle_state.get_all_states()
# # #                 await connection_manager.broadcast(json.dumps({
# # #                     "type": "state_update",
# # #                     "data": updated_state,
# # #                     "timestamp": time.time()
# # #                 }))
# # #                 logger.info("State update broadcasted via WebSocket")
# # #             except Exception as broadcast_error:
# # #                 logger.warning(f"Failed to broadcast state update: {broadcast_error}")
# # #
# # #         return {
# # #             "success": True,
# # #             "action_executed": mapped_action,
# # #             "original_action": action,
# # #             "parameters_used": parameters,
# # #             "execution_result": result,
# # #             "message": f"Successfully executed {mapped_action}"
# # #         }
# # #
# # #     except Exception as e:
# # #         logger.error(f"Error executing action {action}: {e}")
# # #         return {
# # #             "success": False,
# # #             "error": str(e),
# # #             "action_attempted": action,
# # #             "mapped_action": action_mapping.get(action, action)
# # #         }
# # #
# # #
# # # @router.get("/status")
# # # async def get_nlp_status():
# # #     """Get NLP service status"""
# # #     try:
# # #         ml_service = MLParserService()
# # #         # Test ML service connection
# # #         test_result = await ml_service.parse_command("test")
# # #
# # #         return {
# # #             "status": "healthy",
# # #             "ml_service_available": True,
# # #             "ml_service_url": ml_service.ml_service_url,
# # #             "test_result": test_result,
# # #             "timestamp": time.time()
# # #         }
# # #     except Exception as e:
# # #         return {
# # #             "status": "degraded",
# # #             "ml_service_available": False,
# # #             "error": str(e),
# # #             "timestamp": time.time()
# # #         }
# #
# #
# # routers/nlp.py - Fixed version with proper data translation
# from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Form
# from fastapi.responses import JSONResponse
# from pydantic import BaseModel
# from services.ml_parser_service import MLParserService
# import logging
# import time
# import json  # Make sure json is imported
# from typing import Optional, Dict, Any
#
# # Add this import to your existing imports
# from services.speech_service import SpeechService
#
# logger = logging.getLogger("nlp-router")
# router = APIRouter()
#
# # Initialize speech service
# speech_service = SpeechService()
#
#
# class VoiceCommand(BaseModel):
#     text: str
#     timestamp: Optional[float] = None
#
#
# class VoiceResponse(BaseModel):
#     success: bool
#     action: str
#     confidence: float
#     parameters: Dict[str, Any]
#     response_text: str
#     timestamp: float
#     execution_result: Optional[Dict[str, Any]] = None
#     error: Optional[str] = None
#
#
# def translate_backend_to_frontend_state(backend_state: Dict[str, Any]) -> Dict[str, Any]:
#     """Translate backend state structure to match frontend expectations"""
#     translated = {}
#
#     # Translate climate
#     if "climate" in backend_state:
#         translated["climate"] = {
#             "temperature": backend_state["climate"].get("temperature", 22),  # Keep as 'temperature' for backend
#             "temp": backend_state["climate"].get("temperature", 22),  # Add 'temp' for frontend
#             "ac_enabled": backend_state["climate"].get("ac_enabled", False),
#             "fan_speed": backend_state["climate"].get("fan_speed", 3),
#             "heating_enabled": backend_state["climate"].get("heating_enabled", False),
#             "auto_mode": backend_state["climate"].get("auto_mode", True),
#             "recirculation": backend_state["climate"].get("recirculation", False)
#         }
#
#     # Translate infotainment to media (frontend uses 'media' not 'infotainment')
#     if "infotainment" in backend_state:
#         translated["infotainment"] = backend_state["infotainment"]  # Keep original for other systems
#         translated["media"] = {  # Add media for frontend
#             "volume": backend_state["infotainment"].get("volume", 50),
#             "playing": backend_state["infotainment"].get("playing", False),
#             "source": backend_state["infotainment"].get("source", "radio"),
#             "station": backend_state["infotainment"].get("station", "FM 101.5"),
#             "track": backend_state["infotainment"].get("track"),
#             "artist": backend_state["infotainment"].get("artist"),
#             "muted": backend_state["infotainment"].get("muted", False)
#         }
#
#     # Lights remain the same (structure matches)
#     if "lights" in backend_state:
#         translated["lights"] = backend_state["lights"]
#
#     # Translate seats
#     if "seats" in backend_state:
#         translated["seats"] = {
#             "driver_heating": backend_state["seats"].get("driver_heating", False),
#             "heatOn": backend_state["seats"].get("driver_heating", False),  # Add heatOn for frontend
#             "passenger_heating": backend_state["seats"].get("passenger_heating", False),
#             "driver_massage": backend_state["seats"].get("driver_massage", False),
#             "passenger_massage": backend_state["seats"].get("passenger_massage", False),
#             "driver_position": backend_state["seats"].get("driver_position", {"height": 50, "tilt": 50, "lumbar": 50}),
#             "passenger_position": backend_state["seats"].get("passenger_position",
#                                                              {"height": 50, "tilt": 50, "lumbar": 50}),
#             "position": 3  # Default position for frontend slider
#         }
#
#     # Include other fields
#     translated["last_updated"] = backend_state.get("last_updated", time.time())
#
#     return translated
#
#
# @router.get("/test")
# async def test_nlp():
#     """Test endpoint for NLP service"""
#     logger.info("NLP test endpoint accessed")
#     return {
#         "status": "healthy",
#         "message": "NLP router is working",
#         "ml_service_url": "http://localhost:8001",
#         "timestamp": time.time()
#     }
#
#
# @router.post("/process-voice", response_model=VoiceResponse)
# async def process_voice_command(command: VoiceCommand, request: Request):
#     """Process voice command using ML service"""
#     if not command.timestamp:
#         command.timestamp = time.time()
#
#     logger.info(f"Processing voice command: '{command.text}'")
#
#     try:
#         # Initialize ML parser service
#         ml_service = MLParserService()
#
#         # Parse command using ML service
#         ml_result = await ml_service.parse_command(command.text)
#
#         # Get vehicle state and connection manager from app state
#         vehicle_state = request.app.state.vehicle_state
#         connection_manager = request.app.state.connection_manager
#
#         # Execute the action based on ML result
#         execution_result = await execute_vehicle_action(
#             ml_result, vehicle_state, connection_manager
#         )
#
#         return VoiceResponse(
#             success=True,
#             action=ml_result.get("action", "unknown"),
#             confidence=ml_result.get("confidence", 0.0),
#             parameters=ml_result.get("parameters", {}),
#             response_text=f"Executed: {command.text}",
#             timestamp=time.time(),
#             execution_result=execution_result
#         )
#
#     except Exception as e:
#         logger.error(f"Error processing voice command: {e}")
#         return VoiceResponse(
#             success=False,
#             action="error",
#             confidence=0.0,
#             parameters={},
#             response_text=f"Failed to process: {command.text}",
#             timestamp=time.time(),
#             error=str(e)
#         )
#
#
# async def execute_vehicle_action(ml_result: Dict, vehicle_state, connection_manager) -> Dict:
#     """Execute vehicle action based on ML parsing result"""
#     action = ml_result.get("action", "")
#     parameters = ml_result.get("parameters", {})
#
#     logger.info(f"Executing action: {action} with parameters: {parameters}")
#
#     try:
#         # Map ML actions to VehicleStateManager actions with proper fixes
#         action_mapping = {
#             # Climate actions
#             "climate_set": "climate_set_temperature",
#             "climate_set_temperature": "climate_set_temperature",
#             "climate_turn_on": "climate_turn_on_ac",
#             "climate_turn_off": "climate_turn_off_ac",
#             "climate_increase": "climate_increase_temperature",
#             "climate_decrease": "climate_decrease_temperature",
#
#             # Lights actions - ensure proper mapping
#             "lights_turn_on": "lights_turn_on",
#             "lights_turn_off": "lights_turn_off",
#             "lights_brighten": "lights_brighten",
#             "lights_dim": "lights_dim",
#
#             # Seats actions - ensure proper mapping
#             "seats_heat_on": "seats_heat_on",
#             "seats_heat_off": "seats_heat_off",
#             "seats_adjust": "seats_adjust_position",
#
#             # Infotainment actions - ensure proper mapping
#             "infotainment_play": "infotainment_play",
#             "infotainment_pause": "infotainment_pause",
#             "infotainment_stop": "infotainment_pause",  # Map stop to pause
#             "infotainment_volume_up": "infotainment_volume_up",
#             "infotainment_volume_down": "infotainment_volume_down",
#             "infotainment_set_volume": "infotainment_set_volume",
#             "infotainment_increase": "infotainment_volume_up",  # Handle variations
#             "infotainment_decrease": "infotainment_volume_down"
#         }
#
#         # Map the action
#         mapped_action = action_mapping.get(action, action)
#
#         # Ensure parameters are properly formatted
#         if mapped_action == "climate_set_temperature":
#             if "temperature" not in parameters:
#                 temp = parameters.get("temp", parameters.get("value", 22))
#                 parameters = {"temperature": temp}
#
#         if mapped_action.startswith("seats_"):
#             if "seat" not in parameters:
#                 parameters["seat"] = "driver"
#
#         # Execute the command
#         result = await vehicle_state.execute_command(mapped_action, parameters)
#
#         # Broadcast state update via WebSocket if successful
#         if result.get("success", False):
#             try:
#                 # Get the updated state and translate it for frontend
#                 updated_state = vehicle_state.get_all_states()
#                 translated_state = translate_backend_to_frontend_state(updated_state)
#
#                 # Broadcast the translated state
#                 await connection_manager.broadcast(json.dumps({
#                     "type": "state_update",
#                     "data": translated_state,
#                     "timestamp": time.time()
#                 }))
#                 logger.info("State update broadcasted via WebSocket")
#             except Exception as broadcast_error:
#                 logger.warning(f"Failed to broadcast state update: {broadcast_error}")
#
#         return {
#             "success": True,
#             "action_executed": mapped_action,
#             "original_action": action,
#             "parameters_used": parameters,
#             "execution_result": result,
#             "message": f"Successfully executed {mapped_action}"
#         }
#
#     except Exception as e:
#         logger.error(f"Error executing action {action}: {e}")
#         return {
#             "success": False,
#             "error": str(e),
#             "action_attempted": action,
#             "mapped_action": action_mapping.get(action, action)
#         }
#
#
# @router.get("/status")
# async def get_nlp_status():
#     """Get NLP service status"""
#     try:
#         ml_service = MLParserService()
#         test_result = await ml_service.parse_command("test")
#
#         return {
#             "status": "healthy",
#             "ml_service_available": True,
#             "ml_service_url": ml_service.ml_service_url,
#             "test_result": test_result,
#             "timestamp": time.time()
#         }
#     except Exception as e:
#         return {
#             "status": "degraded",
#             "ml_service_available": False,
#             "error": str(e),
#             "timestamp": time.time()
#         }
#
#
# @router.post("/transcribe-audio")
# async def transcribe_audio(
#         audio: UploadFile = File(...),
#         format: Optional[str] = Form("webm")
# ):
#     """
#     Transcribe audio file to text using OpenAI Whisper
#
#     Args:
#         audio: Audio file upload
#         format: Audio format (webm, mp3, wav, etc.)
#
#     Returns:
#         JSON with transcription result
#     """
#     start_time = time.time()
#
#     try:
#         logger.info(f"🎤 Received audio transcription request: {audio.filename}, format: {format}")
#
#         if not speech_service.is_available():
#             raise HTTPException(
#                 status_code=503,
#                 detail="Speech-to-text service not available. Please check OpenAI API key configuration."
#             )
#
#         # Validate file size (max 25MB for OpenAI Whisper)
#         audio_data = await audio.read()
#         if len(audio_data) > 25 * 1024 * 1024:  # 25MB limit
#             raise HTTPException(
#                 status_code=413,
#                 detail="Audio file too large. Maximum size is 25MB."
#             )
#
#         if len(audio_data) == 0:
#             raise HTTPException(
#                 status_code=400,
#                 detail="Empty audio file received"
#             )
#
#         # Transcribe audio
#         result = await speech_service.transcribe_audio(audio_data, format)
#
#         processing_time = time.time() - start_time
#
#         if result["success"]:
#             logger.info(f"✅ Transcription completed: '{result['text']}' (time: {processing_time:.3f}s)")
#
#             return {
#                 "success": True,
#                 "text": result["text"],
#                 "duration": result.get("duration"),
#                 "language": result.get("language", "en"),
#                 "confidence": result.get("confidence", 0.8),
#                 "word_count": result.get("word_count", 0),
#                 "processing_time": processing_time
#             }
#         else:
#             logger.error(f"❌ Transcription failed: {result.get('error', 'Unknown error')}")
#             raise HTTPException(
#                 status_code=500,
#                 detail=f"Transcription failed: {result.get('error', 'Unknown error')}"
#             )
#
#     except HTTPException:
#         raise
#     except Exception as e:
#         processing_time = time.time() - start_time
#         logger.error(f"❌ Unexpected error in transcription: {e}")
#         raise HTTPException(
#             status_code=500,
#             detail=f"Internal server error: {str(e)}"
#         )
#
#
# @router.post("/process-voice-audio")
# async def process_voice_audio(
#         audio: UploadFile = File(...),
#         format: Optional[str] = Form("webm"),
#         request: Request = None
# ):
#     """
#     Complete voice processing pipeline: transcribe audio then process command
#
#     Args:
#         audio: Audio file upload
#         format: Audio format
#         request: FastAPI request object
#
#     Returns:
#         JSON with transcription and command processing results
#     """
#     start_time = time.time()
#
#     try:
#         logger.info(f"🎤 Processing complete voice pipeline: {audio.filename}")
#
#         # Step 1: Transcribe audio
#         audio_data = await audio.read()
#         transcription_result = await speech_service.transcribe_audio(audio_data, format)
#
#         if not transcription_result["success"]:
#             raise HTTPException(
#                 status_code=500,
#                 detail=f"Transcription failed: {transcription_result.get('error', 'Unknown error')}"
#             )
#
#         transcribed_text = transcription_result["text"]
#         logger.info(f"🎯 Transcribed: '{transcribed_text}'")
#
#         if not transcribed_text.strip():
#             return {
#                 "success": False,
#                 "transcription": transcription_result,
#                 "command_result": None,
#                 "error": "No speech detected in audio"
#             }
#
#         # Step 2: Process the transcribed command using existing logic
#         # Import your existing ML parser service
#         from services.ml_parser_service import MLParserService
#
#         ml_service = MLParserService()
#         ml_result = await ml_service.parse_command(transcribed_text)
#
#         # Step 3: Execute command if confidence is high enough
#         vehicle_state = request.app.state.vehicle_state
#         connection_manager = request.app.state.connection_manager
#
#         execution_result = None
#         if ml_result and ml_result.get("confidence", 0) > 0.5:
#             action = ml_result.get("action")
#             parameters = ml_result.get("parameters", {})
#
#             logger.info(f"Executing action: {action} with parameters: {parameters}")
#
#             # Execute the command
#             execution_result = vehicle_state.execute_command(action, parameters)
#
#             # Broadcast state changes via WebSocket
#             if execution_result.get("success", False):
#                 current_state = vehicle_state.get_full_state()
#                 await connection_manager.broadcast({
#                     "type": "state_update",
#                     "data": current_state,
#                     "timestamp": time.time()
#                 })
#                 logger.info("State update broadcasted via WebSocket")
#
#         processing_time = time.time() - start_time
#
#         return {
#             "success": True,
#             "transcription": transcription_result,
#             "command_result": ml_result,
#             "execution_result": execution_result,
#             "processing_time": processing_time
#         }
#
#     except HTTPException:
#         raise
#     except Exception as e:
#         processing_time = time.time() - start_time
#         logger.error(f"❌ Error in voice processing pipeline: {e}")
#         raise HTTPException(
#             status_code=500,
#             detail=f"Voice processing failed: {str(e)}"
#         )
#
#
# # Health check for speech service
# @router.get("/speech-status")
# async def get_speech_status():
#     """Get status of speech-to-text service"""
#     return {
#         "available": speech_service.is_available(),
#         "model": speech_service.model if speech_service.is_available() else None,
#         "connection_test": speech_service.test_connection() if speech_service.is_available() else False
#     }


# routers/nlp.py - Fixed version with working audio processing
from fastapi import APIRouter, Request, HTTPException, File, UploadFile, Form
from pydantic import BaseModel
from services.ml_parser_service import MLParserService
from services.speech_service import SpeechService
import logging
import time
import json
from typing import Optional, Dict, Any

logger = logging.getLogger("nlp-router")
router = APIRouter()


class VoiceCommand(BaseModel):
    text: str
    timestamp: Optional[float] = None


class VoiceResponse(BaseModel):
    success: bool
    action: str
    confidence: float
    parameters: Dict[str, Any]
    response_text: str
    timestamp: float
    execution_result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


def translate_backend_to_frontend_state(backend_state: Dict[str, Any]) -> Dict[str, Any]:
    """Translate backend state structure to match frontend expectations"""
    translated = {}

    if "climate" in backend_state:
        translated["climate"] = {
            "temperature": backend_state["climate"].get("temperature", 22),
            "temp": backend_state["climate"].get("temperature", 22),
            "ac_enabled": backend_state["climate"].get("ac_enabled", False),
            "fan_speed": backend_state["climate"].get("fan_speed", 3),
            "heating_enabled": backend_state["climate"].get("heating_enabled", False),
            "auto_mode": backend_state["climate"].get("auto_mode", True),
            "recirculation": backend_state["climate"].get("recirculation", False)
        }

    if "infotainment" in backend_state:
        translated["infotainment"] = backend_state["infotainment"]
        translated["media"] = {
            "volume": backend_state["infotainment"].get("volume", 50),
            "playing": backend_state["infotainment"].get("playing", False),
            "source": backend_state["infotainment"].get("source", "radio"),
            "station": backend_state["infotainment"].get("station", "FM 101.5"),
            "track": backend_state["infotainment"].get("track"),
            "artist": backend_state["infotainment"].get("artist"),
            "muted": backend_state["infotainment"].get("muted", False)
        }

    if "lights" in backend_state:
        translated["lights"] = backend_state["lights"]

    if "seats" in backend_state:
        translated["seats"] = {
            "driver_heating": backend_state["seats"].get("driver_heating", False),
            "heatOn": backend_state["seats"].get("driver_heating", False),
            "passenger_heating": backend_state["seats"].get("passenger_heating", False),
            "driver_massage": backend_state["seats"].get("driver_massage", False),
            "passenger_massage": backend_state["seats"].get("passenger_massage", False),
            "driver_position": backend_state["seats"].get("driver_position", {"height": 50, "tilt": 50, "lumbar": 50}),
            "passenger_position": backend_state["seats"].get("passenger_position",
                                                             {"height": 50, "tilt": 50, "lumbar": 50}),
            "position": 3
        }

    translated["last_updated"] = backend_state.get("last_updated", time.time())
    return translated


@router.get("/test")
async def test_nlp():
    """Test endpoint for NLP service"""
    logger.info("NLP test endpoint accessed")
    return {
        "status": "healthy",
        "message": "NLP router is working",
        "ml_service_url": "http://localhost:8001",
        "timestamp": time.time()
    }


@router.post("/process-voice-audio")
async def process_voice_audio(
        request: Request,
        audio: UploadFile = File(...),
        format: Optional[str] = Form("webm")
):
    """Process audio file through complete voice pipeline"""
    start_time = time.time()

    try:
        logger.info(f"🎯 Processing audio file: {audio.filename}, size: {audio.size} bytes")

        # Initialize speech service
        speech_service = SpeechService()

        if not speech_service.is_available():
            raise HTTPException(
                status_code=503,
                detail="Speech-to-text service not available. Please check OpenAI API key."
            )

        # Read audio data
        audio_data = await audio.read()
        logger.info(f"🎯 Read {len(audio_data)} bytes of audio data")

        # Determine file format
        file_format = format or "webm"
        if audio.filename:
            if audio.filename.endswith('.mp3'):
                file_format = "mp3"
            elif audio.filename.endswith('.wav'):
                file_format = "wav"
            elif audio.filename.endswith('.m4a'):
                file_format = "m4a"

        # Step 1: Transcribe audio to text
        logger.info("🎯 Starting speech-to-text transcription...")
        transcription_result = await speech_service.transcribe_audio(audio_data, file_format)

        if not transcription_result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Transcription failed: {transcription_result.get('error', 'Unknown error')}"
            )

        transcribed_text = transcription_result.get("text", "").strip()
        logger.info(f"🎯 Transcribed: '{transcribed_text}'")

        if not transcribed_text:
            return {
                "success": False,
                "transcription": transcription_result,
                "command_result": None,
                "execution_result": None,
                "error": "No speech detected in audio"
            }

        # Step 2: Process the transcribed text through ML service
        logger.info("📤 Sending to ML service...")
        ml_service = MLParserService()
        ml_result = await ml_service.parse_command(transcribed_text)

        # Step 3: Execute the action
        vehicle_state = request.app.state.vehicle_state
        connection_manager = request.app.state.connection_manager

        execution_result = await execute_vehicle_action(
            ml_result, vehicle_state, connection_manager
        )

        processing_time = time.time() - start_time

        return {
            "success": True,
            "transcription": transcription_result,
            "command_result": ml_result,
            "execution_result": execution_result,
            "processing_time": processing_time
        }

    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"❌ Error in voice processing pipeline: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Voice processing failed: {str(e)}"
        )


@router.post("/process-voice", response_model=VoiceResponse)
async def process_voice_command(command: VoiceCommand, request: Request):
    """Process voice command using ML service"""
    if not command.timestamp:
        command.timestamp = time.time()

    logger.info(f"Processing voice command: '{command.text}'")

    try:
        ml_service = MLParserService()
        ml_result = await ml_service.parse_command(command.text)

        vehicle_state = request.app.state.vehicle_state
        connection_manager = request.app.state.connection_manager

        execution_result = await execute_vehicle_action(
            ml_result, vehicle_state, connection_manager
        )

        return VoiceResponse(
            success=True,
            action=ml_result.get("action", "unknown"),
            confidence=ml_result.get("confidence", 0.0),
            parameters=ml_result.get("parameters", {}),
            response_text=f"Executed: {command.text}",
            timestamp=time.time(),
            execution_result=execution_result
        )

    except Exception as e:
        logger.error(f"Error processing voice command: {e}")
        return VoiceResponse(
            success=False,
            action="error",
            confidence=0.0,
            parameters={},
            response_text=f"Failed to process: {command.text}",
            timestamp=time.time(),
            error=str(e)
        )


async def execute_vehicle_action(ml_result: Dict, vehicle_state, connection_manager) -> Dict:
    """Execute vehicle action based on ML parsing result"""
    action = ml_result.get("action", "")
    parameters = ml_result.get("parameters", {})

    logger.info(f"Executing action: {action} with parameters: {parameters}")

    try:
        # COMPREHENSIVE action mapping
        action_mapping = {
            # Climate actions
            "climate_set": "climate_set_temperature",
            "climate_set_temperature": "climate_set_temperature",
            "climate_turn_on": "climate_turn_on_ac",
            "climate_turn_off": "climate_turn_off_ac",
            "climate_increase": "climate_increase_temperature",
            "climate_decrease": "climate_decrease_temperature",

            # Lights actions
            "lights_turn_on": "lights_turn_on",
            "lights_turn_off": "lights_turn_off",
            "lights_brighten": "lights_brighten",
            "lights_dim": "lights_dim",

            # Seats actions
            "seats_heat_on": "seats_heat_on",
            "seats_heat_off": "seats_heat_off",
            "seats_adjust": "seats_adjust_position",

            # Infotainment actions - COMPLETE MAPPING
            "infotainment_play": "infotainment_play",
            "infotainment_pause": "infotainment_pause",
            "infotainment_stop": "infotainment_pause",
            "infotainment_turn_off": "infotainment_pause",
            "infotainment_turn_on": "infotainment_play",
            "infotainment_volume_up": "infotainment_volume_up",
            "infotainment_volume_down": "infotainment_volume_down",
            "infotainment_set_volume": "infotainment_set_volume",
            "infotainment_set": "infotainment_set_volume",
            "infotainment_adjust": "infotainment_set_volume",
            "infotainment_increase": "infotainment_volume_up",
            "infotainment_decrease": "infotainment_volume_down",
            "infotainment_mute": "infotainment_mute",
            "infotainment_unmute": "infotainment_unmute",
            "infotainment_next_track": "infotainment_next_track",
            "infotainment_previous_track": "infotainment_previous_track",
            "infotainment_set_source": "infotainment_set_source"
        }

        # Map the action
        mapped_action = action_mapping.get(action, action)
        logger.info(f"Mapped '{action}' to '{mapped_action}'")

        # Handle special parameter cases
        if mapped_action == "climate_set_temperature":
            if "temperature" not in parameters:
                temp = parameters.get("temp", parameters.get("value", 22))
                parameters = {"temperature": temp}

        elif mapped_action.startswith("seats_"):
            if "seat" not in parameters:
                parameters["seat"] = "driver"

        elif mapped_action == "infotainment_set_volume":
            if "volume" not in parameters:
                vol = None
                for key in ["volume", "value", "level"]:
                    if key in parameters:
                        vol = parameters[key]
                        break
                if vol is None:
                    vol = 50
                parameters = {"volume": vol}

        # ✅ FIX: Properly await the execute_command call
        result = await vehicle_state.execute_command(mapped_action, parameters)

        # Check if result is valid
        if not isinstance(result, dict):
            logger.error(f"execute_command returned non-dict result: {type(result)}")
            return {
                "success": False,
                "error": f"Invalid result type from execute_command: {type(result)}",
                "action_attempted": action,
                "mapped_action": mapped_action
            }

        # Broadcast state update via WebSocket if successful
        if result.get("success", False):
            try:
                # ✅ FIX: Use correct method name
                updated_state = vehicle_state.get_all_states()
                translated_state = translate_backend_to_frontend_state(updated_state)

                await connection_manager.broadcast(json.dumps({
                    "type": "state_update",
                    "data": translated_state,
                    "timestamp": time.time()
                }))
                logger.info("State update broadcasted via WebSocket")
            except Exception as broadcast_error:
                logger.warning(f"Failed to broadcast state update: {broadcast_error}")

        return {
            "success": result.get("success", False),
            "action_executed": mapped_action,
            "original_action": action,
            "parameters_used": parameters,
            "execution_result": result,
            "message": f"Successfully executed {mapped_action}" if result.get(
                "success") else f"Failed to execute {mapped_action}"
        }

    except Exception as e:
        logger.error(f"Error executing action {action}: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "action_attempted": action,
            "mapped_action": action_mapping.get(action, action)
        }


@router.get("/status")
async def get_nlp_status():
    """Get NLP service status"""
    try:
        ml_service = MLParserService()
        test_result = await ml_service.parse_command("test")

        return {
            "status": "healthy",
            "ml_service_available": True,
            "ml_service_url": ml_service.ml_service_url,
            "test_result": test_result,
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "status": "degraded",
            "ml_service_available": False,
            "error": str(e),
            "timestamp": time.time()
        }


# Health check for speech service
@router.get("/speech-status")
async def get_speech_status():
    """Get status of speech-to-text service"""
    try:
        speech_service = SpeechService()
        return {
            "available": speech_service.is_available(),
            "model": speech_service.model if speech_service.is_available() else None,
            "connection_test": speech_service.test_connection() if speech_service.is_available() else False
        }
    except Exception as e:
        return {
            "available": False,
            "error": str(e)
        }
