# routers/nlp.py - Complete file with ML integration
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from services.ml_parser_service import MLParserService
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


@router.post("/process-voice", response_model=VoiceResponse)
async def process_voice_command(command: VoiceCommand, request: Request):
    """Process voice command using ML service"""
    if not command.timestamp:
        command.timestamp = time.time()

    logger.info(f"Processing voice command: '{command.text}'")

    try:
        # Initialize ML parser service
        ml_service = MLParserService()

        # Parse command using ML service
        ml_result = await ml_service.parse_command(command.text)

        # Get vehicle state and connection manager from app state
        vehicle_state = request.app.state.vehicle_state
        connection_manager = request.app.state.connection_manager

        # Execute the action based on ML result
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
        # Map ML actions to VehicleStateManager actions
        action_mapping = {
            # Climate actions
            "climate_set": "climate_set_temperature",
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

            # Infotainment actions
            "infotainment_play": "infotainment_play",
            "infotainment_pause": "infotainment_pause",
            "infotainment_volume_up": "infotainment_volume_up",
            "infotainment_volume_down": "infotainment_volume_down",
            "infotainment_set_volume": "infotainment_set_volume"
        }

        # Map the action
        mapped_action = action_mapping.get(action, action)

        # For climate_set, ensure we have temperature parameter
        if mapped_action == "climate_set_temperature":
            if "temperature" not in parameters:
                # Try to extract from other possible keys
                temp = parameters.get("temp", parameters.get("value", 22))
                parameters = {"temperature": temp}

        # For seats actions, add seat parameter if missing
        if mapped_action.startswith("seats_"):
            if "seat" not in parameters:
                parameters["seat"] = "driver"  # Default to driver

        # Execute the command using VehicleStateManager's execute_command method
        result = await vehicle_state.execute_command(mapped_action, parameters)

        # Broadcast state update via WebSocket if successful
        if result.get("success", True):  # Some results might not have success field
            try:
                updated_state = vehicle_state.get_all_states()
                await connection_manager.broadcast(json.dumps({
                    "type": "state_update",
                    "data": updated_state,
                    "timestamp": time.time()
                }))
                logger.info("State update broadcasted via WebSocket")
            except Exception as broadcast_error:
                logger.warning(f"Failed to broadcast state update: {broadcast_error}")

        return {
            "success": True,
            "action_executed": mapped_action,
            "original_action": action,
            "parameters_used": parameters,
            "execution_result": result,
            "message": f"Successfully executed {mapped_action}"
        }

    except Exception as e:
        logger.error(f"Error executing action {action}: {e}")
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
        # Test ML service connection
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