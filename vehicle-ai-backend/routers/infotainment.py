from fastapi import APIRouter, HTTPException, Request
from models.schemas import InfotainmentCommand, InfotainmentState, APIResponse
from typing import Optional

router = APIRouter()

@router.get("/", response_model=InfotainmentState)
async def get_infotainment_state(request: Request):
    """Get current infotainment system state"""
    vehicle_state = request.app.state.vehicle_state
    return vehicle_state.get_infotainment_state()

@router.post("/play", response_model=APIResponse)
async def play_media(request: Request):
    """Start playing media"""
    try:
        vehicle_state = request.app.state.vehicle_state
        connection_manager = request.app.state.connection_manager
        
        updated_state = await vehicle_state.update_infotainment({"is_playing": True})
        
        await connection_manager.broadcast_state_update({
            "infotainment": updated_state.dict()
        })
        
        return APIResponse(
            success=True,
            message="Media playback started",
            data=updated_state.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop", response_model=APIResponse)
async def stop_media(request: Request):
    """Stop playing media"""
    try:
        vehicle_state = request.app.state.vehicle_state
        connection_manager = request.app.state.connection_manager
        
        updated_state = await vehicle_state.update_infotainment({"is_playing": False})
        
        await connection_manager.broadcast_state_update({
            "infotainment": updated_state.dict()
        })
        
        return APIResponse(
            success=True,
            message="Media playback stopped",
            data=updated_state.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/volume-up", response_model=APIResponse)
async def volume_up(request: Request, amount: Optional[int] = 5):
    """Increase volume"""
    try:
        vehicle_state = request.app.state.vehicle_state
        connection_manager = request.app.state.connection_manager
        
        current_volume = vehicle_state.get_infotainment_state().volume
        new_volume = min(100, current_volume + amount)
        
        updated_state = await vehicle_state.update_infotainment({"volume": new_volume})
        
        await connection_manager.broadcast_state_update({
            "infotainment": updated_state.dict()
        })
        
        return APIResponse(
            success=True,
            message=f"Volume increased to {new_volume}%",
            data=updated_state.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/volume-down", response_model=APIResponse)
async def volume_down(request: Request, amount: Optional[int] = 5):
    """Decrease volume"""
    try:
        vehicle_state = request.app.state.vehicle_state
        connection_manager = request.app.state.connection_manager
        
        current_volume = vehicle_state.get_infotainment_state().volume
        new_volume = max(0, current_volume - amount)
        
        updated_state = await vehicle_state.update_infotainment({"volume": new_volume})
        
        await connection_manager.broadcast_state_update({
            "infotainment": updated_state.dict()
        })
        
        return APIResponse(
            success=True,
            message=f"Volume decreased to {new_volume}%",
            data=updated_state.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/set-volume/{volume}", response_model=APIResponse)
async def set_volume(volume: int, request: Request):
    """Set specific volume level"""
    if volume < 0 or volume > 100:
        raise HTTPException(status_code=400, detail="Volume must be between 0 and 100")
    
    try:
        vehicle_state = request.app.state.vehicle_state
        connection_manager = request.app.state.connection_manager
        
        updated_state = await vehicle_state.update_infotainment({"volume": volume})
        
        await connection_manager.broadcast_state_update({
            "infotainment": updated_state.dict()
        })
        
        return APIResponse(
            success=True,
            message=f"Volume set to {volume}%",
            data=updated_state.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/set-source/{source}", response_model=APIResponse)
async def set_source(source: str, request: Request):
    """Set media source"""
    valid_sources = ["radio", "bluetooth", "usb", "streaming"]
    if source not in valid_sources:
        raise HTTPException(status_code=400, detail=f"Source must be one of: {valid_sources}")
    
    try:
        vehicle_state = request.app.state.vehicle_state
        connection_manager = request.app.state.connection_manager
        
        updated_state = await vehicle_state.update_infotainment({"source": source})
        
        await connection_manager.broadcast_state_update({
            "infotainment": updated_state.dict()
        })
        
        return APIResponse(
            success=True,
            message=f"Media source set to {source}",
            data=updated_state.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/set-track", response_model=APIResponse)
async def set_current_track(track_name: str, request: Request):
    """Set current track information"""
    try:
        vehicle_state = request.app.state.vehicle_state
        connection_manager = request.app.state.connection_manager
        
        updated_state = await vehicle_state.update_infotainment({"current_track": track_name})
        
        await connection_manager.broadcast_state_update({
            "infotainment": updated_state.dict()
        })
        
        return APIResponse(
            success=True,
            message=f"Now playing: {track_name}",
            data=updated_state.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))