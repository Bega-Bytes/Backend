from fastapi import APIRouter, HTTPException, Request
from models.schemas import LightsCommand, LightsState, APIResponse
from typing import Optional

router = APIRouter()

@router.get("/", response_model=LightsState)
async def get_lights_state(request: Request):
    """Get current lights system state"""
    vehicle_state = request.app.state.vehicle_state
    return vehicle_state.get_lights_state()

@router.post("/turn-on", response_model=APIResponse)
async def turn_on_lights(request: Request):
    """Turn on interior lights"""
    try:
        vehicle_state = request.app.state.vehicle_state
        connection_manager = request.app.state.connection_manager
        
        updated_state = await vehicle_state.update_lights({"interior_on": True})
        
        await connection_manager.broadcast_state_update({
            "lights": updated_state.dict()
        })
        
        return APIResponse(
            success=True,
            message="Interior lights turned on",
            data=updated_state.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/turn-off", response_model=APIResponse)
async def turn_off_lights(request: Request):
    """Turn off interior lights"""
    try:
        vehicle_state = request.app.state.vehicle_state
        connection_manager = request.app.state.connection_manager
        
        updated_state = await vehicle_state.update_lights({"interior_on": False})
        
        await connection_manager.broadcast_state_update({
            "lights": updated_state.dict()
        })
        
        return APIResponse(
            success=True,
            message="Interior lights turned off",
            data=updated_state.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/dim", response_model=APIResponse)
async def dim_lights(request: Request, amount: Optional[int] = 10):
    """Dim the interior lights"""
    try:
        vehicle_state = request.app.state.vehicle_state
        connection_manager = request.app.state.connection_manager
        
        current_brightness = vehicle_state.get_lights_state().brightness
        new_brightness = max(0, current_brightness - amount)
        
        updated_state = await vehicle_state.update_lights({"brightness": new_brightness})
        
        await connection_manager.broadcast_state_update({
            "lights": updated_state.dict()
        })
        
        return APIResponse(
            success=True,
            message=f"Lights dimmed to {new_brightness}%",
            data=updated_state.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/brighten", response_model=APIResponse)
async def brighten_lights(request: Request, amount: Optional[int] = 10):
    """Brighten the interior lights"""
    try:
        vehicle_state = request.app.state.vehicle_state
        connection_manager = request.app.state.connection_manager
        
        current_brightness = vehicle_state.get_lights_state().brightness
        new_brightness = min(100, current_brightness + amount)
        
        updated_state = await vehicle_state.update_lights({"brightness": new_brightness})
        
        await connection_manager.broadcast_state_update({
            "lights": updated_state.dict()
        })
        
        return APIResponse(
            success=True,
            message=f"Lights brightened to {new_brightness}%",
            data=updated_state.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/set-brightness/{brightness}", response_model=APIResponse)
async def set_brightness(brightness: int, request: Request):
    """Set specific brightness level"""
    if brightness < 0 or brightness > 100:
        raise HTTPException(status_code=400, detail="Brightness must be between 0 and 100")
    
    try:
        vehicle_state = request.app.state.vehicle_state
        connection_manager = request.app.state.connection_manager
        
        updated_state = await vehicle_state.update_lights({"brightness": brightness})
        
        await connection_manager.broadcast_state_update({
            "lights": updated_state.dict()
        })
        
        return APIResponse(
            success=True,
            message=f"Lights brightness set to {brightness}%",
            data=updated_state.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/set-color/{color}", response_model=APIResponse)
async def set_ambient_color(color: str, request: Request):
    """Set ambient lighting color"""
    valid_colors = ["white", "red", "blue", "green", "yellow", "purple", "orange"]
    if color not in valid_colors:
        raise HTTPException(status_code=400, detail=f"Color must be one of: {valid_colors}")
    
    try:
        vehicle_state = request.app.state.vehicle_state
        connection_manager = request.app.state.connection_manager
        
        updated_state = await vehicle_state.update_lights({"ambient_color": color})
        
        await connection_manager.broadcast_state_update({
            "lights": updated_state.dict()
        })
        
        return APIResponse(
            success=True,
            message=f"Ambient lighting color set to {color}",
            data=updated_state.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))