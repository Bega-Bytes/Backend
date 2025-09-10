from fastapi import APIRouter, Request, HTTPException
from models.schemas import ClimateState
from typing import Dict, Any
import logging

logger = logging.getLogger("climate-router")
router = APIRouter()


@router.get("/status", response_model=ClimateState)
async def get_climate_status(request: Request):
    """Get current climate control status"""
    try:
        vehicle_state = request.app.state.vehicle_state
        return vehicle_state.get_climate_state()
    except Exception as e:
        logger.error(f"Error getting climate status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get climate status")


@router.post("/temperature")
async def set_temperature(temperature: float, request: Request):
    """Set climate temperature"""
    try:
        if not 16.0 <= temperature <= 30.0:
            raise HTTPException(status_code=400, detail="Temperature must be between 16-30°C")

        vehicle_state = request.app.state.vehicle_state
        result = await vehicle_state.process_nlp_action("climate_set_temperature", {"temperature": temperature})

        return {"success": True, "temperature": temperature, "result": result}
    except Exception as e:
        logger.error(f"Error setting temperature: {e}")
        raise HTTPException(status_code=500, detail="Failed to set temperature")


@router.post("/ac")
async def toggle_ac(enabled: bool, request: Request):
    """Toggle air conditioning"""
    try:
        vehicle_state = request.app.state.vehicle_state
        action = "climate_turn_on_ac" if enabled else "climate_turn_off_ac"
        result = await vehicle_state.process_nlp_action(action, {})

        return {"success": True, "ac_enabled": enabled, "result": result}
    except Exception as e:
        logger.error(f"Error toggling AC: {e}")
        raise HTTPException(status_code=500, detail="Failed to toggle AC")


@router.post("/fan-speed")
async def set_fan_speed(speed: int, request: Request):
    """Set fan speed"""
    try:
        if not 0 <= speed <= 5:
            raise HTTPException(status_code=400, detail="Fan speed must be between 0-5")

        vehicle_state = request.app.state.vehicle_state
        result = await vehicle_state.process_nlp_action("climate_set_fan_speed", {"speed": speed})

        return {"success": True, "fan_speed": speed, "result": result}
    except Exception as e:
        logger.error(f"Error setting fan speed: {e}")
        raise HTTPException(status_code=500, detail="Failed to set fan speed")