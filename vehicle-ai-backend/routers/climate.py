from fastapi import APIRouter, HTTPException, Request
from models.schemas import ClimateCommand, ClimateState, APIResponse
from typing import Optional

router = APIRouter()

@router.get("/", response_model=ClimateState)
async def get_climate_state(request: Request):
    """Get current climate control state"""
    vehicle_state = request.app.state.vehicle_state
    return vehicle_state.get_climate_state()

@router.post("/turn-on", response_model=APIResponse)
async def turn_on_climate(request: Request):
    """Turn on climate control"""
    try:
        vehicle_state = request.app.state.vehicle_state
        connection_manager = request.app.state.connection_manager
        
        updated_state = await vehicle_state.update_climate({"is_on": True})
        
        # Broadcast update to connected clients
        await connection_manager.broadcast_state_update({
            "climate": updated_state.dict()
        })
        
        return APIResponse(
            success=True,
            message="Climate control turned on",
            data=updated_state.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/turn-off", response_model=APIResponse)
async def turn_off_climate(request: Request):
    """Turn off climate control"""
    try:
        vehicle_state = request.app.state.vehicle_state
        connection_manager = request.app.state.connection_manager
        
        updated_state = await vehicle_state.update_climate({"is_on": False})
        
        await connection_manager.broadcast_state_update({
            "climate": updated_state.dict()
        })
        
        return APIResponse(
            success=True,
            message="Climate control turned off",
            data=updated_state.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/set-temperature/{temperature}", response_model=APIResponse)
async def set_temperature(temperature: int, request: Request):
    """Set climate control temperature"""
    if temperature < 16 or temperature > 32:
        raise HTTPException(status_code=400, detail="Temperature must be between 16 and 32 degrees")
    
    try:
        vehicle_state = request.app.state.vehicle_state
        connection_manager = request.app.state.connection_manager
        
        updated_state = await vehicle_state.update_climate({"temperature": temperature})
        
        await connection_manager.broadcast_state_update({
            "climate": updated_state.dict()
        })
        
        return APIResponse(
            success=True,
            message=f"Temperature set to {temperature}°C",
            data=updated_state.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/increase-temperature", response_model=APIResponse)
async def increase_temperature(request: Request, amount: Optional[int] = 1):
    """Increase climate control temperature"""
    try:
        vehicle_state = request.app.state.vehicle_state
        connection_manager = request.app.state.connection_manager
        
        current_temp = vehicle_state.get_climate_state().temperature
        new_temp = min(32, current_temp + amount)
        
        updated_state = await vehicle_state.update_climate({"temperature": new_temp})
        
        await connection_manager.broadcast_state_update({
            "climate": updated_state.dict()
        })
        
        return APIResponse(
            success=True,
            message=f"Temperature increased to {new_temp}°C",
            data=updated_state.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/decrease-temperature", response_model=APIResponse)
async def decrease_temperature(request: Request, amount: Optional[int] = 1):
    """Decrease climate control temperature"""
    try:
        vehicle_state = request.app.state.vehicle_state
        connection_manager = request.app.state.connection_manager
        
        current_temp = vehicle_state.get_climate_state().temperature
        new_temp = max(16, current_temp - amount)
        
        updated_state = await vehicle_state.update_climate({"temperature": new_temp})
        
        await connection_manager.broadcast_state_update({
            "climate": updated_state.dict()
        })
        
        return APIResponse(
            success=True,
            message=f"Temperature decreased to {new_temp}°C",
            data=updated_state.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/set-fan-speed/{speed}", response_model=APIResponse)
async def set_fan_speed(speed: int, request: Request):
    """Set climate control fan speed"""
    if speed < 1 or speed > 5:
        raise HTTPException(status_code=400, detail="Fan speed must be between 1 and 5")
    
    try:
        vehicle_state = request.app.state.vehicle_state
        connection_manager = request.app.state.connection_manager
        
        updated_state = await vehicle_state.update_climate({"fan_speed": speed})
        
        await connection_manager.broadcast_state_update({
            "climate": updated_state.dict()
        })
        
        return APIResponse(
            success=True,
            message=f"Fan speed set to {speed}",
            data=updated_state.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/set-mode/{mode}", response_model=APIResponse)
async def set_mode(mode: str, request: Request):
    """Set climate control mode"""
    valid_modes = ["auto", "heat", "cool", "fan"]
    if mode not in valid_modes:
        raise HTTPException(status_code=400, detail=f"Mode must be one of: {valid_modes}")
    
    try:
        vehicle_state = request.app.state.vehicle_state
        connection_manager = request.app.state.connection_manager
        
        updated_state = await vehicle_state.update_climate({"mode": mode})
        
        await connection_manager.broadcast_state_update({
            "climate": updated_state.dict()
        })
        
        return APIResponse(
            success=True,
            message=f"Climate mode set to {mode}",
            data=updated_state.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))