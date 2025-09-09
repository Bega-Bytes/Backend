from fastapi import APIRouter, HTTPException, Request
from models.schemas import SeatsCommand, SeatsState, APIResponse
from typing import Optional, Dict

router = APIRouter()

@router.get("/", response_model=SeatsState)
async def get_seats_state(request: Request):
    """Get current seats system state"""
    vehicle_state = request.app.state.vehicle_state
    return vehicle_state.get_seats_state()

@router.post("/heat-on", response_model=APIResponse)
async def turn_on_seat_heating(request: Request):
    """Turn on seat heating"""
    try:
        vehicle_state = request.app.state.vehicle_state
        connection_manager = request.app.state.connection_manager
        
        updated_state = await vehicle_state.update_seats({"heating_on": True})
        
        await connection_manager.broadcast_state_update({
            "seats": updated_state.dict()
        })
        
        return APIResponse(
            success=True,
            message="Seat heating turned on",
            data=updated_state.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/heat-off", response_model=APIResponse)
async def turn_off_seat_heating(request: Request):
    """Turn off seat heating"""
    try:
        vehicle_state = request.app.state.vehicle_state
        connection_manager = request.app.state.connection_manager
        
        updated_state = await vehicle_state.update_seats({"heating_on": False})
        
        await connection_manager.broadcast_state_update({
            "seats": updated_state.dict()
        })
        
        return APIResponse(
            success=True,
            message="Seat heating turned off",
            data=updated_state.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/set-heating-level/{level}", response_model=APIResponse)
async def set_heating_level(level: int, request: Request):
    """Set seat heating level"""
    if level < 1 or level > 3:
        raise HTTPException(status_code=400, detail="Heating level must be between 1 and 3")
    
    try:
        vehicle_state = request.app.state.vehicle_state
        connection_manager = request.app.state.connection_manager
        
        updated_state = await vehicle_state.update_seats({
            "heating_level": level,
            "heating_on": True  # Turn on heating when setting level
        })
        
        await connection_manager.broadcast_state_update({
            "seats": updated_state.dict()
        })
        
        return APIResponse(
            success=True,
            message=f"Seat heating level set to {level}",
            data=updated_state.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/adjust-position", response_model=APIResponse)
async def adjust_seat_position(request: Request, position: Dict[str, int]):
    """Adjust seat position"""
    # Validate position parameters
    valid_params = ["recline", "height", "lumbar"]
    for param, value in position.items():
        if param not in valid_params:
            raise HTTPException(status_code=400, detail=f"Invalid position parameter: {param}")
        if not (0 <= value <= 100):
            raise HTTPException(status_code=400, detail=f"{param} must be between 0 and 100")
    
    try:
        vehicle_state = request.app.state.vehicle_state
        connection_manager = request.app.state.connection_manager
        
        # Get current position and update with new values
        current_position = vehicle_state.get_seats_state().position.copy()
        current_position.update(position)
        
        updated_state = await vehicle_state.update_seats({"position": current_position})
        
        await connection_manager.broadcast_state_update({
            "seats": updated_state.dict()
        })
        
        return APIResponse(
            success=True,
            message="Seat position adjusted",
            data=updated_state.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/preset/{preset_name}", response_model=APIResponse)
async def apply_seat_preset(preset_name: str, request: Request):
    """Apply a predefined seat preset"""
    presets = {
        "comfort": {
            "recline": 30,
            "height": 60,
            "lumbar": 70
        },
        "sport": {
            "recline": 80,
            "height": 40,
            "lumbar": 50
        },
        "relax": {
            "recline": 10,
            "height": 80,
            "lumbar": 90
        }
    }
    
    if preset_name not in presets:
        raise HTTPException(status_code=400, detail=f"Preset must be one of: {list(presets.keys())}")
    
    try:
        vehicle_state = request.app.state.vehicle_state
        connection_manager = request.app.state.connection_manager
        
        updated_state = await vehicle_state.update_seats({"position": presets[preset_name]})
        
        await connection_manager.broadcast_state_update({
            "seats": updated_state.dict()
        })
        
        return APIResponse(
            success=True,
            message=f"Applied {preset_name} seat preset",
            data=updated_state.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/presets")
async def get_available_presets():
    """Get list of available seat presets"""
    return {
        "presets": ["comfort", "sport", "relax"],
        "positions": ["recline", "height", "lumbar"]
    }