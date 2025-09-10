from fastapi import APIRouter, Request, HTTPException
from models.schemas import SeatsState
from typing import Dict, Any
import logging

logger = logging.getLogger("seats-router")
router = APIRouter()


@router.get("/status", response_model=SeatsState)
async def get_seats_status(request: Request):
    """Get current seat status"""
    try:
        vehicle_state = request.app.state.vehicle_state
        return vehicle_state.get_seats_state()
    except Exception as e:
        logger.error(f"Error getting seats status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get seats status")


@router.post("/heating")
async def toggle_seat_heating(seat: str, enabled: bool, request: Request):
    """Toggle seat heating"""
    try:
        valid_seats = ["driver", "passenger"]
        if seat not in valid_seats:
            raise HTTPException(status_code=400, detail=f"Seat must be one of: {valid_seats}")

        vehicle_state = request.app.state.vehicle_state
        action = "seats_heat_on" if enabled else "seats_heat_off"
        result = await vehicle_state.process_nlp_action(action, {"seat": seat})

        return {"success": True, "seat": seat, "heating": enabled, "result": result}
    except Exception as e:
        logger.error(f"Error toggling seat heating: {e}")
        raise HTTPException(status_code=500, detail="Failed to toggle seat heating")


@router.post("/massage")
async def toggle_seat_massage(seat: str, enabled: bool, request: Request):
    """Toggle seat massage"""
    try:
        valid_seats = ["driver", "passenger"]
        if seat not in valid_seats:
            raise HTTPException(status_code=400, detail=f"Seat must be one of: {valid_seats}")

        vehicle_state = request.app.state.vehicle_state
        action = "seats_massage_on" if enabled else "seats_massage_off"
        result = await vehicle_state.process_nlp_action(action, {"seat": seat})

        return {"success": True, "seat": seat, "massage": enabled, "result": result}
    except Exception as e:
        logger.error(f"Error toggling seat massage: {e}")
        raise HTTPException(status_code=500, detail="Failed to toggle seat massage")


@router.post("/position")
async def adjust_seat_position(seat: str, position_type: str, value: int, request: Request):
    """Adjust seat position"""
    try:
        valid_seats = ["driver", "passenger"]
        valid_positions = ["height", "tilt", "lumbar"]

        if seat not in valid_seats:
            raise HTTPException(status_code=400, detail=f"Seat must be one of: {valid_seats}")

        if position_type not in valid_positions:
            raise HTTPException(status_code=400, detail=f"Position type must be one of: {valid_positions}")

        if not 0 <= value <= 100:
            raise HTTPException(status_code=400, detail="Position value must be between 0-100")

        vehicle_state = request.app.state.vehicle_state
        result = await vehicle_state.process_nlp_action("seats_adjust_position", {
            "seat": seat,
            "position_type": position_type,
            "value": value
        })

        return {"success": True, "seat": seat, "position_type": position_type, "value": value, "result": result}
    except Exception as e:
        logger.error(f"Error adjusting seat position: {e}")
        raise HTTPException(status_code=500, detail="Failed to adjust seat position")