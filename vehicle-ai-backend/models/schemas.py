from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
import time


# Input Models
class VoiceCommand(BaseModel):
    """Voice command input model"""
    text: str = Field(..., min_length=1, max_length=500, description="The voice command text")
    timestamp: Optional[float] = Field(default_factory=time.time,
                                       description="Unix timestamp when command was recorded")
    user_id: Optional[str] = Field(None, description="Optional user identifier")
    session_id: Optional[str] = Field(None, description="Optional session identifier")

    class Config:
        schema_extra = {
            "example": {
                "text": "turn on the air conditioning",
                "timestamp": 1234567890.123,
                "user_id": "user123",
                "session_id": "session456"
            }
        }


# Response Models
class NLPResponse(BaseModel):
    """NLP processing response model"""
    action: str = Field(..., description="The identified action")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0 and 1")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Action parameters")
    response_text: str = Field(..., description="Human-readable response text")
    timestamp: float = Field(..., description="Timestamp when command was processed")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    success: bool = Field(True, description="Whether the command was successfully processed")
    intent: Optional[str] = Field(None, description="The identified intent/domain")
    source: Optional[str] = Field("backend", description="Source of the response")

    class Config:
        schema_extra = {
            "example": {
                "action": "climate_set_temperature",
                "confidence": 0.95,
                "parameters": {"temperature": 22, "unit": "celsius"},
                "response_text": "Setting temperature to 22°C",
                "timestamp": 1234567890.123,
                "processing_time": 0.156,
                "success": True,
                "intent": "climate",
                "source": "ml_parser"
            }
        }


# Vehicle State Models
class ClimateState(BaseModel):
    """Climate control state"""
    temperature: float = Field(22.0, ge=16.0, le=30.0, description="Temperature in Celsius")
    fan_speed: int = Field(3, ge=0, le=5, description="Fan speed level")
    ac_enabled: bool = Field(True, description="Air conditioning enabled")
    heating_enabled: bool = Field(False, description="Heating enabled")
    auto_mode: bool = Field(True, description="Auto climate mode")
    recirculation: bool = Field(False, description="Air recirculation enabled")

    class Config:
        schema_extra = {
            "example": {
                "temperature": 22.0,
                "fan_speed": 3,
                "ac_enabled": True,
                "heating_enabled": False,
                "auto_mode": True,
                "recirculation": False
            }
        }


class LightsState(BaseModel):
    """Lighting system state"""
    interior_lights: bool = Field(True, description="Interior lights on/off")
    ambient_lights: bool = Field(True, description="Ambient lights on/off")
    reading_lights: bool = Field(False, description="Reading lights on/off")
    brightness: int = Field(80, ge=0, le=100, description="Overall brightness percentage")
    ambient_color: str = Field("white", description="Ambient light color")

    class Config:
        schema_extra = {
            "example": {
                "interior_lights": True,
                "ambient_lights": True,
                "reading_lights": False,
                "brightness": 80,
                "ambient_color": "blue"
            }
        }


class SeatsState(BaseModel):
    """Seat control state"""
    driver_heating: bool = Field(False, description="Driver seat heating")
    passenger_heating: bool = Field(False, description="Passenger seat heating")
    driver_massage: bool = Field(False, description="Driver seat massage")
    passenger_massage: bool = Field(False, description="Passenger seat massage")
    driver_position: Dict[str, int] = Field(
        default_factory=lambda: {"height": 50, "tilt": 50, "lumbar": 50},
        description="Driver seat position settings"
    )
    passenger_position: Dict[str, int] = Field(
        default_factory=lambda: {"height": 50, "tilt": 50, "lumbar": 50},
        description="Passenger seat position settings"
    )

    class Config:
        schema_extra = {
            "example": {
                "driver_heating": True,
                "passenger_heating": False,
                "driver_massage": False,
                "passenger_massage": False,
                "driver_position": {"height": 60, "tilt": 45, "lumbar": 55},
                "passenger_position": {"height": 50, "tilt": 50, "lumbar": 50}
            }
        }


class InfotainmentState(BaseModel):
    """Infotainment system state"""
    volume: int = Field(50, ge=0, le=100, description="Volume level")
    source: str = Field("radio", description="Audio source")
    station: Optional[str] = Field("FM 101.5", description="Current radio station")
    track: Optional[str] = Field(None, description="Current track name")
    artist: Optional[str] = Field(None, description="Current artist")
    playing: bool = Field(False, description="Audio currently playing")
    muted: bool = Field(False, description="Audio muted")

    class Config:
        schema_extra = {
            "example": {
                "volume": 65,
                "source": "bluetooth",
                "station": None,
                "track": "Bohemian Rhapsody",
                "artist": "Queen",
                "playing": True,
                "muted": False
            }
        }


class VehicleState(BaseModel):
    """Complete vehicle state"""
    climate: ClimateState = Field(default_factory=ClimateState)
    lights: LightsState = Field(default_factory=LightsState)
    seats: SeatsState = Field(default_factory=SeatsState)
    infotainment: InfotainmentState = Field(default_factory=InfotainmentState)
    last_updated: float = Field(default_factory=time.time, description="Last update timestamp")

    class Config:
        schema_extra = {
            "example": {
                "climate": {
                    "temperature": 22.0,
                    "fan_speed": 3,
                    "ac_enabled": True,
                    "heating_enabled": False,
                    "auto_mode": True,
                    "recirculation": False
                },
                "lights": {
                    "interior_lights": True,
                    "ambient_lights": True,
                    "reading_lights": False,
                    "brightness": 80,
                    "ambient_color": "blue"
                },
                "seats": {
                    "driver_heating": True,
                    "passenger_heating": False,
                    "driver_massage": False,
                    "passenger_massage": False,
                    "driver_position": {"height": 60, "tilt": 45, "lumbar": 55},
                    "passenger_position": {"height": 50, "tilt": 50, "lumbar": 50}
                },
                "infotainment": {
                    "volume": 65,
                    "source": "bluetooth",
                    "station": None,
                    "track": "Bohemian Rhapsody",
                    "artist": "Queen",
                    "playing": True,
                    "muted": False
                },
                "last_updated": 1234567890.123
            }
        }


# WebSocket Message Models
class WebSocketMessage(BaseModel):
    """WebSocket message model"""
    type: str = Field(..., description="Message type")
    data: Dict[str, Any] = Field(default_factory=dict, description="Message data")
    timestamp: float = Field(default_factory=time.time, description="Message timestamp")

    class Config:
        schema_extra = {
            "example": {
                "type": "voice_command",
                "data": {"text": "turn on lights"},
                "timestamp": 1234567890.123
            }
        }


class StateUpdateMessage(BaseModel):
    """State update WebSocket message"""
    type: str = Field("state_update", description="Message type")
    system: str = Field(..., description="System that was updated")
    action: str = Field(..., description="Action that was performed")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Action parameters")
    state: Dict[str, Any] = Field(..., description="New state")
    timestamp: float = Field(default_factory=time.time, description="Update timestamp")

    class Config:
        schema_extra = {
            "example": {
                "type": "state_update",
                "system": "climate",
                "action": "set_temperature",
                "parameters": {"temperature": 24},
                "state": {"temperature": 24.0, "fan_speed": 3},
                "timestamp": 1234567890.123
            }
        }


# Error Models
class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: float = Field(default_factory=time.time, description="Error timestamp")

    class Config:
        schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Invalid temperature value",
                "details": {"field": "temperature", "value": -50},
                "timestamp": 1234567890.123
            }
        }


# Test Models
class TestCommand(BaseModel):
    """Test command model"""
    text: str = Field(..., description="Command to test")
    expected_action: Optional[str] = Field(None, description="Expected action result")
    expected_confidence: Optional[float] = Field(None, description="Expected confidence threshold")

    class Config:
        schema_extra = {
            "example": {
                "text": "set temperature to 25 degrees",
                "expected_action": "climate_set_temperature",
                "expected_confidence": 0.8
            }
        }


class TestResult(BaseModel):
    """Test result model"""
    success: bool = Field(..., description="Test passed")
    command: str = Field(..., description="Test command")
    actual_result: Dict[str, Any] = Field(..., description="Actual parsing result")
    expected_result: Optional[Dict[str, Any]] = Field(None, description="Expected result")
    message: str = Field(..., description="Test result message")
    timestamp: float = Field(default_factory=time.time, description="Test timestamp")

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "command": "turn on lights",
                "actual_result": {"action": "lights_turn_on", "confidence": 0.95},
                "expected_result": {"action": "lights_turn_on"},
                "message": "Test passed successfully",
                "timestamp": 1234567890.123
            }
        }