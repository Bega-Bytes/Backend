from pydantic import BaseModel, Field
from typing import Optional, Union
from enum import Enum

# Climate Control Models
class ClimateState(BaseModel):
    is_on: bool = False
    temperature: int = Field(default=22, ge=16, le=32)  # Celsius
    fan_speed: int = Field(default=3, ge=1, le=5)
    mode: str = Field(default="auto")  # auto, heat, cool, fan
    
class ClimateCommand(BaseModel):
    action: str
    value: Optional[Union[int, str]] = None

# Infotainment Models
class InfotainmentState(BaseModel):
    is_playing: bool = False
    volume: int = Field(default=50, ge=0, le=100)
    current_track: Optional[str] = None
    source: str = Field(default="radio")  # radio, bluetooth, usb
    
class InfotainmentCommand(BaseModel):
    action: str
    value: Optional[Union[int, str]] = None

# Lights Models
class LightsState(BaseModel):
    interior_on: bool = False
    brightness: int = Field(default=50, ge=0, le=100)
    ambient_color: str = Field(default="white")
    
class LightsCommand(BaseModel):
    action: str
    value: Optional[Union[int, str]] = None

# Seats Models
class SeatsState(BaseModel):
    heating_on: bool = False
    heating_level: int = Field(default=1, ge=1, le=3)
    position: dict = Field(default_factory=lambda: {
        "recline": 50,
        "height": 50,
        "lumbar": 50
    })
    
class SeatsCommand(BaseModel):
    action: str
    value: Optional[Union[int, str, dict]] = None

# NLP Models
class VoiceCommand(BaseModel):
    text: str
    timestamp: Optional[float] = None
    
class NLPResponse(BaseModel):
    intent: str
    confidence: float
    entities: dict
    action: str
    parameters: Optional[dict] = None

# Overall Vehicle State
class VehicleState(BaseModel):
    climate: ClimateState = Field(default_factory=ClimateState)
    infotainment: InfotainmentState = Field(default_factory=InfotainmentState)
    lights: LightsState = Field(default_factory=LightsState)
    seats: SeatsState = Field(default_factory=SeatsState)
    last_updated: Optional[float] = None

# WebSocket Message Models
class WebSocketMessage(BaseModel):
    type: str
    data: Optional[dict] = None
    timestamp: Optional[float] = None

# Response Models
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None