from fastapi import APIRouter, Request, HTTPException
from models.schemas import LightsState
from typing import Dict, Any
import logging

logger = logging.getLogger("lights-router")
router = APIRouter()


@router.get("/status", response_model=LightsState)
async def get_lights_status(request: Request):
    """Get current lighting status"""
    try:
        vehicle_state = request.app.state.vehicle_state
        return vehicle_state.get_lights_state()
    except Exception as e:
        logger.error(f"Error getting lights status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get lights status")


@router.post("/toggle")
async def toggle_lights(light_type: str, enabled: bool, request: Request):
    """Toggle specific lights"""
    try:
        valid_types = ["interior", "ambient", "reading", "all"]
        if light_type not in valid_types:
            raise HTTPException(status_code=400, detail=f"Light type must be one of: {valid_types}")

        vehicle_state = request.app.state.vehicle_state
        action = "lights_turn_on" if enabled else "lights_turn_off"
        result = await vehicle_state.process_nlp_action(action, {"location": light_type})

        return {"success": True, "light_type": light_type, "enabled": enabled, "result": result}
    except Exception as e:
        logger.error(f"Error toggling lights: {e}")
        raise HTTPException(status_code=500, detail="Failed to toggle lights")


@router.post("/brightness")
async def set_brightness(brightness: int, request: Request):
    """Set light brightness"""
    try:
        if not 0 <= brightness <= 100:
            raise HTTPException(status_code=400, detail="Brightness must be between 0-100")

        vehicle_state = request.app.state.vehicle_state
        result = await vehicle_state.process_nlp_action("lights_set_brightness", {"brightness": brightness})

        return {"success": True, "brightness": brightness, "result": result}
    except Exception as e:
        logger.error(f"Error setting brightness: {e}")
        raise HTTPException(status_code=500, detail="Failed to set brightness")


@router.post("/color")
async def set_ambient_color(color: str, request: Request):
    """Set ambient light color"""
    try:
        valid_colors = ["white", "red", "blue", "green", "purple", "orange", "yellow"]
        if color not in valid_colors:
            raise HTTPException(status_code=400, detail=f"Color must be one of: {valid_colors}")

        vehicle_state = request.app.state.vehicle_state
        result = await vehicle_state.process_nlp_action("lights_set_color", {"color": color})

        return {"success": True, "color": color, "result": result}
    except Exception as e:
        logger.error(f"Error setting ambient color: {e}")
        raise HTTPException(status_code=500, detail="Failed to set ambient color")