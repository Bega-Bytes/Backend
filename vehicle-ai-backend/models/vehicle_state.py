import asyncio
import time
from typing import Dict, Any
from .schemas import VehicleState, ClimateState, InfotainmentState, LightsState, SeatsState

class VehicleStateManager:
    """Manages the current state of all vehicle systems"""
    
    def __init__(self):
        self.state = VehicleState()
        self._lock = asyncio.Lock()
        
    async def update_climate(self, updates: Dict[str, Any]) -> ClimateState:
        """Update climate system state"""
        async with self._lock:
            current = self.state.climate.dict()
            current.update(updates)
            self.state.climate = ClimateState(**current)
            self.state.last_updated = time.time()
            return self.state.climate
    
    async def update_infotainment(self, updates: Dict[str, Any]) -> InfotainmentState:
        """Update infotainment system state"""
        async with self._lock:
            current = self.state.infotainment.dict()
            current.update(updates)
            self.state.infotainment = InfotainmentState(**current)
            self.state.last_updated = time.time()
            return self.state.infotainment
    
    async def update_lights(self, updates: Dict[str, Any]) -> LightsState:
        """Update lights system state"""
        async with self._lock:
            current = self.state.lights.dict()
            current.update(updates)
            self.state.lights = LightsState(**current)
            self.state.last_updated = time.time()
            return self.state.lights
    
    async def update_seats(self, updates: Dict[str, Any]) -> SeatsState:
        """Update seats system state"""
        async with self._lock:
            current = self.state.seats.dict()
            current.update(updates)
            self.state.seats = SeatsState(**current)
            self.state.last_updated = time.time()
            return self.state.seats
    
    def get_climate_state(self) -> ClimateState:
        """Get current climate state"""
        return self.state.climate
    
    def get_infotainment_state(self) -> InfotainmentState:
        """Get current infotainment state"""
        return self.state.infotainment
    
    def get_lights_state(self) -> LightsState:
        """Get current lights state"""
        return self.state.lights
    
    def get_seats_state(self) -> SeatsState:
        """Get current seats state"""
        return self.state.seats
    
    def get_all_states(self) -> Dict[str, Any]:
        """Get all system states"""
        return self.state.dict()
    
    async def reset_all(self):
        """Reset all systems to default state"""
        async with self._lock:
            self.state = VehicleState()
            self.state.last_updated = time.time()
    
    async def process_nlp_action(self, action: str, parameters: Dict[str, Any] = None):
        """Process an action from NLP and update appropriate system"""
        if parameters is None:
            parameters = {}
            
        # Climate actions
        if action.startswith("climate_"):
            return await self._process_climate_action(action, parameters)
        
        # Infotainment actions
        elif action.startswith("infotainment_"):
            return await self._process_infotainment_action(action, parameters)
        
        # Lights actions
        elif action.startswith("lights_"):
            return await self._process_lights_action(action, parameters)
        
        # Seats actions
        elif action.startswith("seats_"):
            return await self._process_seats_action(action, parameters)
        
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _process_climate_action(self, action: str, parameters: Dict[str, Any]):
        """Process climate-specific actions"""
        updates = {}
        
        if action == "climate_turn_on":
            updates["is_on"] = True
        elif action == "climate_turn_off":
            updates["is_on"] = False
        elif action == "climate_set_temperature":
            updates["temperature"] = parameters.get("temperature", 22)
        elif action == "climate_increase":
            current_temp = self.state.climate.temperature
            updates["temperature"] = min(32, current_temp + parameters.get("amount", 1))
        elif action == "climate_decrease":
            current_temp = self.state.climate.temperature
            updates["temperature"] = max(16, current_temp - parameters.get("amount", 1))
        
        return await self.update_climate(updates)
    
    async def _process_infotainment_action(self, action: str, parameters: Dict[str, Any]):
        """Process infotainment-specific actions"""
        updates = {}
        
        if action == "infotainment_play":
            updates["is_playing"] = True
        elif action == "infotainment_stop":
            updates["is_playing"] = False
        elif action == "infotainment_volume_up":
            current_volume = self.state.infotainment.volume
            updates["volume"] = min(100, current_volume + parameters.get("amount", 5))
        elif action == "infotainment_volume_down":
            current_volume = self.state.infotainment.volume
            updates["volume"] = max(0, current_volume - parameters.get("amount", 5))
        elif action == "infotainment_set_volume":
            updates["volume"] = parameters.get("volume", 50)
        
        return await self.update_infotainment(updates)
    
    async def _process_lights_action(self, action: str, parameters: Dict[str, Any]):
        """Process lights-specific actions"""
        updates = {}
        
        if action == "lights_turn_on":
            updates["interior_on"] = True
        elif action == "lights_turn_off":
            updates["interior_on"] = False
        elif action == "lights_dim":
            current_brightness = self.state.lights.brightness
            updates["brightness"] = max(0, current_brightness - parameters.get("amount", 10))
        elif action == "lights_brighten":
            current_brightness = self.state.lights.brightness
            updates["brightness"] = min(100, current_brightness + parameters.get("amount", 10))
        
        return await self.update_lights(updates)
    
    async def _process_seats_action(self, action: str, parameters: Dict[str, Any]):
        """Process seats-specific actions"""
        updates = {}
        
        if action == "seats_heat_on":
            updates["heating_on"] = True
        elif action == "seats_heat_off":
            updates["heating_on"] = False
        elif action == "seats_adjust":
            if "position" in parameters:
                updates["position"] = parameters["position"]
        
        return await self.update_seats(updates)