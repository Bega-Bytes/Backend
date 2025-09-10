from fastapi import APIRouter, Request, HTTPException
from models.schemas import InfotainmentState
from typing import Dict, Any
import logging

logger = logging.getLogger("infotainment-router")
router = APIRouter()


@router.get("/status", response_model=InfotainmentState)
async def get_infotainment_status(request: Request):
    """Get current infotainment status"""
    try:
        vehicle_state = request.app.state.vehicle_state
        return vehicle_state.get_infotainment_state()
    except Exception as e:
        logger.error(f"Error getting infotainment status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get infotainment status")


@router.post("/volume")
async def set_volume(volume: int, request: Request):
    """Set audio volume"""
    try:
        if not 0 <= volume <= 100:
            raise HTTPException(status_code=400, detail="Volume must be between 0-100")

        vehicle_state = request.app.state.vehicle_state
        result = await vehicle_state.process_nlp_action("infotainment_set_volume", {"volume": volume})

        return {"success": True, "volume": volume, "result": result}
    except Exception as e:
        logger.error(f"Error setting volume: {e}")
        raise HTTPException(status_code=500, detail="Failed to set volume")


@router.post("/mute")
async def toggle_mute(muted: bool, request: Request):
    """Toggle audio mute"""
    try:
        vehicle_state = request.app.state.vehicle_state
        action = "infotainment_mute" if muted else "infotainment_unmute"
        result = await vehicle_state.process_nlp_action(action, {})

        return {"success": True, "muted": muted, "result": result}
    except Exception as e:
        logger.error(f"Error toggling mute: {e}")
        raise HTTPException(status_code=500, detail="Failed to toggle mute")


@router.post("/play")
async def toggle_playback(playing: bool, request: Request):
    """Toggle music playback"""
    try:
        vehicle_state = request.app.state.vehicle_state
        action = "infotainment_play_music" if playing else "infotainment_pause_music"
        result = await vehicle_state.process_nlp_action(action, {})

        return {"success": True, "playing": playing, "result": result}
    except Exception as e:
        logger.error(f"Error toggling playback: {e}")
        raise HTTPException(status_code=500, detail="Failed to toggle playback")


@router.post("/track")
async def change_track(direction: str, request: Request):
    """Change to next or previous track"""
    try:
        valid_directions = ["next", "previous"]
        if direction not in valid_directions:
            raise HTTPException(status_code=400, detail=f"Direction must be one of: {valid_directions}")

        vehicle_state = request.app.state.vehicle_state
        action = f"infotainment_{direction}_track"
        result = await vehicle_state.process_nlp_action(action, {})

        return {"success": True, "direction": direction, "result": result}
    except Exception as e:
        logger.error(f"Error changing track: {e}")
        raise HTTPException(status_code=500, detail="Failed to change track")


@router.post("/radio")
async def tune_radio(station: str, request: Request):
    """Tune to radio station"""
    try:
        vehicle_state = request.app.state.vehicle_state
        result = await vehicle_state.process_nlp_action("infotainment_radio_tune", {"station": station})

        return {"success": True, "station": station, "result": result}
    except Exception as e:
        logger.error(f"Error tuning radio: {e}")
        raise HTTPException(status_code=500, detail="Failed to tune radio")


@router.post("/source")
async def set_audio_source(source: str, request: Request):
    """Set audio source"""
    try:
        valid_sources = ["radio", "bluetooth", "usb", "aux", "music"]
        if source not in valid_sources:
            raise HTTPException(status_code=400, detail=f"Source must be one of: {valid_sources}")

        vehicle_state = request.app.state.vehicle_state
        result = await vehicle_state.process_nlp_action("infotainment_set_source", {"source": source})

        return {"success": True, "source": source, "result": result}
    except Exception as e:
        logger.error(f"Error setting audio source: {e}")
        raise HTTPException(status_code=500, detail="Failed to set audio source")