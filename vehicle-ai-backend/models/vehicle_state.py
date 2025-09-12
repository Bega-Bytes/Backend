# # models/vehicle_state.py - Complete file with execute_command integration
# import asyncio
# import logging
# import time
# from typing import Dict, Any, Optional, Union
# from models.schemas import (
#     VehicleState, ClimateState, LightsState,
#     SeatsState, InfotainmentState
# )
#
# logger = logging.getLogger("vehicle-state")
#
#
# class VehicleStateManager:
#     """Manages the complete vehicle state across all systems"""
#
#     def __init__(self):
#         # Initialize default states
#         self.state = VehicleState()
#         self._lock = asyncio.Lock()
#         self._update_callbacks = []
#
#         logger.info("Vehicle State Manager initialized")
#         logger.info(f"Initial state: {self.state.dict()}")
#
#     # NEW METHOD: Main integration point for ML service
#     async def execute_command(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         """Execute a parsed command on the vehicle state"""
#         async with self._lock:
#             try:
#                 logger.info(f"Executing command: {action} with parameters: {parameters}")
#                 result = {"action": action, "success": False, "changes": {}}
#
#                 # Route to appropriate handler based on action prefix
#                 if action.startswith("climate_"):
#                     result = await self._execute_climate_action(action, parameters)
#                 elif action.startswith("lights_"):
#                     result = await self._execute_lights_action(action, parameters)
#                 elif action.startswith("seats_"):
#                     result = await self._execute_seats_action(action, parameters)
#                 elif action.startswith("infotainment_"):
#                     result = await self._execute_infotainment_action(action, parameters)
#                 else:
#                     result["error"] = f"Unknown action category: {action}"
#                     logger.warning(f"Unknown action: {action}")
#
#                 # Update timestamp if successful
#                 if result.get("success"):
#                     self.state.last_updated = time.time()
#                     logger.info(f"Command executed successfully: {result}")
#
#                     # Notify callbacks
#                     await self._notify_update_callbacks(action, parameters, result)
#                 else:
#                     logger.warning(f"Command execution failed: {result}")
#
#                 return result
#
#             except Exception as e:
#                 logger.error(f"Error executing command {action}: {e}", exc_info=True)
#                 return {"action": action, "success": False, "error": str(e)}
#
#     async def _execute_climate_action(self, action: str, params: Dict) -> Dict:
#         """Execute climate-related actions"""
#         changes = {}
#
#         try:
#             if action == "climate_set_temperature":
#                 temp = float(params.get("temperature", self.state.climate.temperature))
#                 temp = max(16.0, min(30.0, temp))  # Clamp between 16-30°C
#                 self.state.climate.temperature = temp
#                 changes["temperature"] = temp
#
#             elif action == "climate_turn_on" or action == "climate_turn_on_ac":
#                 self.state.climate.ac_enabled = True
#                 changes["ac_enabled"] = True
#
#             elif action == "climate_turn_off" or action == "climate_turn_off_ac":
#                 self.state.climate.ac_enabled = False
#                 changes["ac_enabled"] = False
#
#             elif action == "climate_increase":
#                 new_temp = min(30.0, self.state.climate.temperature + 1.0)
#                 self.state.climate.temperature = new_temp
#                 changes["temperature"] = new_temp
#
#             elif action == "climate_decrease":
#                 new_temp = max(16.0, self.state.climate.temperature - 1.0)
#                 self.state.climate.temperature = new_temp
#                 changes["temperature"] = new_temp
#
#             elif action == "climate_set_fan_speed":
#                 speed = int(params.get("speed", self.state.climate.fan_speed))
#                 speed = max(0, min(5, speed))  # Clamp between 0-5
#                 self.state.climate.fan_speed = speed
#                 changes["fan_speed"] = speed
#
#             elif action == "climate_heating_on":
#                 self.state.climate.heating_enabled = True
#                 changes["heating_enabled"] = True
#
#             elif action == "climate_heating_off":
#                 self.state.climate.heating_enabled = False
#                 changes["heating_enabled"] = False
#
#             else:
#                 return {"success": False, "error": f"Unknown climate action: {action}"}
#
#             return {"success": True, "changes": changes}
#
#         except Exception as e:
#             return {"success": False, "error": f"Climate action error: {str(e)}"}
#
#     async def _execute_lights_action(self, action: str, params: Dict) -> Dict:
#         """Execute lighting-related actions"""
#         changes = {}
#
#         try:
#             location = params.get("location", "all")
#
#             if action == "lights_turn_on":
#                 if location in ["interior", "all"]:
#                     self.state.lights.interior_lights = True
#                     changes["interior_lights"] = True
#                 if location in ["ambient", "all"]:
#                     self.state.lights.ambient_lights = True
#                     changes["ambient_lights"] = True
#                 if location in ["reading", "all"]:
#                     self.state.lights.reading_lights = True
#                     changes["reading_lights"] = True
#
#             elif action == "lights_turn_off":
#                 if location in ["interior", "all"]:
#                     self.state.lights.interior_lights = False
#                     changes["interior_lights"] = False
#                 if location in ["ambient", "all"]:
#                     self.state.lights.ambient_lights = False
#                     changes["ambient_lights"] = False
#                 if location in ["reading", "all"]:
#                     self.state.lights.reading_lights = False
#                     changes["reading_lights"] = False
#
#             elif action == "lights_set_brightness":
#                 brightness = int(params.get("brightness", self.state.lights.brightness))
#                 brightness = max(0, min(100, brightness))
#                 self.state.lights.brightness = brightness
#                 changes["brightness"] = brightness
#
#             elif action == "lights_dim":
#                 new_brightness = max(0, self.state.lights.brightness - 20)
#                 self.state.lights.brightness = new_brightness
#                 changes["brightness"] = new_brightness
#
#             elif action == "lights_brighten":
#                 new_brightness = min(100, self.state.lights.brightness + 20)
#                 self.state.lights.brightness = new_brightness
#                 changes["brightness"] = new_brightness
#
#             elif action == "lights_set_color":
#                 color = params.get("color", "white")
#                 valid_colors = ["white", "red", "blue", "green", "purple", "orange", "yellow"]
#                 if color in valid_colors:
#                     self.state.lights.ambient_color = color
#                     changes["ambient_color"] = color
#                 else:
#                     return {"success": False, "error": f"Invalid color: {color}"}
#
#             else:
#                 return {"success": False, "error": f"Unknown lights action: {action}"}
#
#             return {"success": True, "changes": changes}
#
#         except Exception as e:
#             return {"success": False, "error": f"Lights action error: {str(e)}"}
#
#     async def _execute_seats_action(self, action: str, params: Dict) -> Dict:
#         """Execute seat-related actions"""
#         changes = {}
#
#         try:
#             seat = params.get("seat", "driver")
#
#             if action == "seats_heat_on":
#                 if seat == "driver":
#                     self.state.seats.driver_heating = True
#                     changes["driver_heating"] = True
#                 elif seat == "passenger":
#                     self.state.seats.passenger_heating = True
#                     changes["passenger_heating"] = True
#
#             elif action == "seats_heat_off":
#                 if seat == "driver":
#                     self.state.seats.driver_heating = False
#                     changes["driver_heating"] = False
#                 elif seat == "passenger":
#                     self.state.seats.passenger_heating = False
#                     changes["passenger_heating"] = False
#
#             elif action == "seats_massage_on":
#                 if seat == "driver":
#                     self.state.seats.driver_massage = True
#                     changes["driver_massage"] = True
#                 elif seat == "passenger":
#                     self.state.seats.passenger_massage = True
#                     changes["passenger_massage"] = True
#
#             elif action == "seats_massage_off":
#                 if seat == "driver":
#                     self.state.seats.driver_massage = False
#                     changes["driver_massage"] = False
#                 elif seat == "passenger":
#                     self.state.seats.passenger_massage = False
#                     changes["passenger_massage"] = False
#
#             elif action == "seats_adjust":
#                 # Handle position adjustments
#                 position_type = params.get("position_type", "height")
#                 value = params.get("value", 50)
#                 value = max(0, min(100, int(value)))
#
#                 if seat == "driver":
#                     if hasattr(self.state.seats.driver_position, position_type):
#                         setattr(self.state.seats.driver_position, position_type, value)
#                         changes[f"driver_{position_type}"] = value
#                 elif seat == "passenger":
#                     if hasattr(self.state.seats.passenger_position, position_type):
#                         setattr(self.state.seats.passenger_position, position_type, value)
#                         changes[f"passenger_{position_type}"] = value
#
#             else:
#                 return {"success": False, "error": f"Unknown seats action: {action}"}
#
#             return {"success": True, "changes": changes}
#
#         except Exception as e:
#             return {"success": False, "error": f"Seats action error: {str(e)}"}
#
#     async def _execute_infotainment_action(self, action: str, params: Dict) -> Dict:
#         """Execute infotainment-related actions"""
#         changes = {}
#
#         try:
#             if action == "infotainment_set_volume":
#                 volume = int(params.get("volume", self.state.infotainment.volume))
#                 volume = max(0, min(100, volume))
#                 self.state.infotainment.volume = volume
#                 changes["volume"] = volume
#
#             elif action == "infotainment_volume_up":
#                 new_volume = min(100, self.state.infotainment.volume + 10)
#                 self.state.infotainment.volume = new_volume
#                 changes["volume"] = new_volume
#
#             elif action == "infotainment_volume_down":
#                 new_volume = max(0, self.state.infotainment.volume - 10)
#                 self.state.infotainment.volume = new_volume
#                 changes["volume"] = new_volume
#
#             elif action == "infotainment_mute":
#                 self.state.infotainment.muted = True
#                 changes["muted"] = True
#
#             elif action == "infotainment_unmute":
#                 self.state.infotainment.muted = False
#                 changes["muted"] = False
#
#             elif action == "infotainment_play" or action == "infotainment_play_music":
#                 self.state.infotainment.playing = True
#                 changes["playing"] = True
#
#             elif action == "infotainment_pause" or action == "infotainment_pause_music":
#                 self.state.infotainment.playing = False
#                 changes["playing"] = False
#
#             elif action == "infotainment_next_track":
#                 # Simulate track change
#                 changes["track_changed"] = "next"
#
#             elif action == "infotainment_previous_track":
#                 # Simulate track change
#                 changes["track_changed"] = "previous"
#
#             else:
#                 return {"success": False, "error": f"Unknown infotainment action: {action}"}
#
#             return {"success": True, "changes": changes}
#
#         except Exception as e:
#             return {"success": False, "error": f"Infotainment action error: {str(e)}"}
#
#     # EXISTING METHODS (kept for backward compatibility)
#     async def process_nlp_action(self, action: str, parameters: Dict[str, Any]) -> Union[
#         ClimateState, LightsState, SeatsState, InfotainmentState, Dict[str, Any]]:
#         """Process an NLP action and update vehicle state"""
#         async with self._lock:
#             logger.info(f"Processing action: {action} with parameters: {parameters}")
#
#             try:
#                 if action.startswith("climate_"):
#                     result = await self._process_climate_action(action, parameters)
#                 elif action.startswith("lights_"):
#                     result = await self._process_lights_action(action, parameters)
#                 elif action.startswith("seats_"):
#                     result = await self._process_seats_action(action, parameters)
#                 elif action.startswith("infotainment_"):
#                     result = await self._process_infotainment_action(action, parameters)
#                 else:
#                     logger.warning(f"Unknown action category: {action}")
#                     result = {"error": f"Unknown action: {action}"}
#
#                 # Update timestamp
#                 self.state.last_updated = time.time()
#
#                 # Notify callbacks
#                 await self._notify_update_callbacks(action, parameters, result)
#
#                 logger.info(f"Action processed successfully: {result}")
#                 return result
#
#             except Exception as e:
#                 logger.error(f"Error processing action {action}: {e}", exc_info=True)
#                 raise
#
#     async def _process_climate_action(self, action: str, parameters: Dict[str, Any]) -> ClimateState:
#         """Process climate-related actions"""
#         logger.debug(f"Processing climate action: {action}")
#
#         if action == "climate_set_temperature":
#             temp = parameters.get("temperature", 22.0)
#             self.state.climate.temperature = max(16.0, min(30.0, temp))
#             logger.info(f"Temperature set to {self.state.climate.temperature}°C")
#
#         elif action == "climate_turn_on_ac":
#             self.state.climate.ac_enabled = True
#             logger.info("Air conditioning turned on")
#
#         elif action == "climate_turn_off_ac":
#             self.state.climate.ac_enabled = False
#             logger.info("Air conditioning turned off")
#
#         elif action == "climate_set_fan_speed":
#             speed = parameters.get("speed", 3)
#             self.state.climate.fan_speed = max(0, min(5, speed))
#             logger.info(f"Fan speed set to {self.state.climate.fan_speed}")
#
#         elif action == "climate_increase_temperature":
#             self.state.climate.temperature = min(30.0, self.state.climate.temperature + 1)
#             logger.info(f"Temperature increased to {self.state.climate.temperature}°C")
#
#         elif action == "climate_decrease_temperature":
#             self.state.climate.temperature = max(16.0, self.state.climate.temperature - 1)
#             logger.info(f"Temperature decreased to {self.state.climate.temperature}°C")
#
#         else:
#             logger.warning(f"Unknown climate action: {action}")
#
#         return self.state.climate
#
#     async def _process_lights_action(self, action: str, parameters: Dict[str, Any]) -> LightsState:
#         """Process lighting-related actions"""
#         logger.debug(f"Processing lights action: {action}")
#
#         location = parameters.get("location", "all")
#
#         if action == "lights_turn_on":
#             if location in ["interior", "all"]:
#                 self.state.lights.interior_lights = True
#             if location in ["ambient", "all"]:
#                 self.state.lights.ambient_lights = True
#             if location in ["reading", "all"]:
#                 self.state.lights.reading_lights = True
#             logger.info(f"Lights turned on: {location}")
#
#         elif action == "lights_turn_off":
#             if location in ["interior", "all"]:
#                 self.state.lights.interior_lights = False
#             if location in ["ambient", "all"]:
#                 self.state.lights.ambient_lights = False
#             if location in ["reading", "all"]:
#                 self.state.lights.reading_lights = False
#             logger.info(f"Lights turned off: {location}")
#
#         elif action == "lights_set_brightness":
#             brightness = parameters.get("brightness", 50)
#             self.state.lights.brightness = max(0, min(100, brightness))
#             logger.info(f"Brightness set to {self.state.lights.brightness}%")
#
#         elif action == "lights_set_color":
#             color = parameters.get("color", "white")
#             self.state.lights.ambient_color = color
#             logger.info(f"Ambient color set to {color}")
#
#         else:
#             logger.warning(f"Unknown lights action: {action}")
#
#         return self.state.lights
#
#     async def _process_seats_action(self, action: str, parameters: Dict[str, Any]) -> SeatsState:
#         """Process seat-related actions"""
#         logger.debug(f"Processing seats action: {action}")
#
#         seat = parameters.get("seat", "driver")
#
#         if action == "seats_heat_on":
#             if seat == "driver":
#                 self.state.seats.driver_heating = True
#             elif seat == "passenger":
#                 self.state.seats.passenger_heating = True
#             logger.info(f"{seat} seat heating turned on")
#
#         elif action == "seats_heat_off":
#             if seat == "driver":
#                 self.state.seats.driver_heating = False
#             elif seat == "passenger":
#                 self.state.seats.passenger_heating = False
#             logger.info(f"{seat} seat heating turned off")
#
#         elif action == "seats_massage_on":
#             if seat == "driver":
#                 self.state.seats.driver_massage = True
#             elif seat == "passenger":
#                 self.state.seats.passenger_massage = True
#             logger.info(f"{seat} seat massage turned on")
#
#         elif action == "seats_massage_off":
#             if seat == "driver":
#                 self.state.seats.driver_massage = False
#             elif seat == "passenger":
#                 self.state.seats.passenger_massage = False
#             logger.info(f"{seat} seat massage turned off")
#
#         elif action == "seats_adjust_position":
#             position_type = parameters.get("position_type", "height")
#             value = parameters.get("value", 50)
#             value = max(0, min(100, int(value)))
#
#             if seat == "driver":
#                 if position_type in self.state.seats.driver_position:
#                     self.state.seats.driver_position[position_type] = value
#             elif seat == "passenger":
#                 if position_type in self.state.seats.passenger_position:
#                     self.state.seats.passenger_position[position_type] = value
#
#             logger.info(f"{seat} seat {position_type} adjusted to {value}")
#
#         else:
#             logger.warning(f"Unknown seats action: {action}")
#
#         return self.state.seats
#
#     async def _process_infotainment_action(self, action: str, parameters: Dict[str, Any]) -> InfotainmentState:
#         """Process infotainment-related actions"""
#         logger.debug(f"Processing infotainment action: {action}")
#
#         if action == "infotainment_set_volume":
#             volume = parameters.get("volume", 50)
#             self.state.infotainment.volume = max(0, min(100, volume))
#             logger.info(f"Volume set to {self.state.infotainment.volume}%")
#
#         elif action == "infotainment_volume_up":
#             self.state.infotainment.volume = min(100, self.state.infotainment.volume + 10)
#             logger.info(f"Volume increased to {self.state.infotainment.volume}%")
#
#         elif action == "infotainment_volume_down":
#             self.state.infotainment.volume = max(0, self.state.infotainment.volume - 10)
#             logger.info(f"Volume decreased to {self.state.infotainment.volume}%")
#
#         elif action == "infotainment_mute":
#             self.state.infotainment.muted = True
#             logger.info("Audio muted")
#
#         elif action == "infotainment_unmute":
#             self.state.infotainment.muted = False
#             logger.info("Audio unmuted")
#
#         elif action == "infotainment_play_music":
#             self.state.infotainment.playing = True
#             logger.info("Music playback started")
#
#         elif action == "infotainment_pause_music":
#             self.state.infotainment.playing = False
#             logger.info("Music playback paused")
#
#         elif action == "infotainment_next_track":
#             # Simulate track change
#             self.state.infotainment.track = "Next Track"
#             logger.info("Skipped to next track")
#
#         elif action == "infotainment_previous_track":
#             # Simulate track change
#             self.state.infotainment.track = "Previous Track"
#             logger.info("Skipped to previous track")
#
#         elif action == "infotainment_radio_tune":
#             station = parameters.get("station", "FM 101.5")
#             self.state.infotainment.station = station
#             self.state.infotainment.source = "radio"
#             self.state.infotainment.playing = True
#             logger.info(f"Tuned to {station}")
#
#         elif action == "infotainment_set_source":
#             source = parameters.get("source", "radio")
#             self.state.infotainment.source = source
#             logger.info(f"Audio source set to {source}")
#
#         else:
#             logger.warning(f"Unknown infotainment action: {action}")
#
#         return self.state.infotainment
#
#     async def _notify_update_callbacks(self, action: str, parameters: Dict[str, Any], result: Any):
#         """Notify all registered update callbacks"""
#         for callback in self._update_callbacks:
#             try:
#                 await callback(action, parameters, result)
#             except Exception as e:
#                 logger.error(f"Error in update callback: {e}")
#
#     def register_update_callback(self, callback):
#         """Register a callback to be called when state updates"""
#         self._update_callbacks.append(callback)
#         logger.info(f"Registered update callback: {callback.__name__}")
#
#     def unregister_update_callback(self, callback):
#         """Unregister an update callback"""
#         if callback in self._update_callbacks:
#             self._update_callbacks.remove(callback)
#             logger.info(f"Unregistered update callback: {callback.__name__}")
#
#     def get_all_states(self) -> Dict[str, Any]:
#         """Get all current vehicle states"""
#         return self.state.dict()
#
#     def get_climate_state(self) -> ClimateState:
#         """Get current climate state"""
#         return self.state.climate
#
#     def get_lights_state(self) -> LightsState:
#         """Get current lights state"""
#         return self.state.lights
#
#     def get_seats_state(self) -> SeatsState:
#         """Get current seats state"""
#         return self.state.seats
#
#     def get_infotainment_state(self) -> InfotainmentState:
#         """Get current infotainment state"""
#         return self.state.infotainment
#
#     async def reset_to_defaults(self):
#         """Reset all systems to default state"""
#         async with self._lock:
#             self.state = VehicleState()
#             logger.info("Vehicle state reset to defaults")
#
#     async def set_custom_state(self, system: str, new_state: Dict[str, Any]):
#         """Set custom state for a specific system"""
#         async with self._lock:
#             try:
#                 if system == "climate":
#                     self.state.climate = ClimateState(**new_state)
#                 elif system == "lights":
#                     self.state.lights = LightsState(**new_state)
#                 elif system == "seats":
#                     self.state.seats = SeatsState(**new_state)
#                 elif system == "infotainment":
#                     self.state.infotainment = InfotainmentState(**new_state)
#                 else:
#                     raise ValueError(f"Unknown system: {system}")
#
#                 self.state.last_updated = time.time()
#                 logger.info(f"Custom state set for {system}: {new_state}")
#
#             except Exception as e:
#                 logger.error(f"Error setting custom state for {system}: {e}")
#                 raise
#
#     def get_state_summary(self) -> Dict[str, str]:
#         """Get a human-readable summary of current state"""
#         return {
#             "climate": f"Temp: {self.state.climate.temperature}°C, AC: {'On' if self.state.climate.ac_enabled else 'Off'}, Fan: {self.state.climate.fan_speed}",
#             "lights": f"Interior: {'On' if self.state.lights.interior_lights else 'Off'}, Brightness: {self.state.lights.brightness}%",
#             "seats": f"Driver Heat: {'On' if self.state.seats.driver_heating else 'Off'}, Passenger Heat: {'On' if self.state.seats.passenger_heating else 'Off'}",
#             "infotainment": f"Volume: {self.state.infotainment.volume}%, Source: {self.state.infotainment.source}, Playing: {'Yes' if self.state.infotainment.playing else 'No'}"
#         }



# models/vehicle_state.py - Complete fixed version with all actions
import asyncio
import logging
import time
from typing import Dict, Any, Optional, Union
from models.schemas import (
    VehicleState, ClimateState, LightsState,
    SeatsState, InfotainmentState
)

logger = logging.getLogger("vehicle-state")


class VehicleStateManager:
    """Manages the complete vehicle state across all systems"""

    def __init__(self):
        # Initialize default states
        self.state = VehicleState()
        self._lock = asyncio.Lock()
        self._update_callbacks = []

        logger.info("Vehicle State Manager initialized")
        logger.info(f"Initial state: {self.state.dict()}")

    async def execute_command(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a parsed command on the vehicle state"""
        async with self._lock:
            try:
                logger.info(f"Executing command: {action} with parameters: {parameters}")
                result = {"action": action, "success": False, "changes": {}}

                # Route to appropriate handler based on action prefix
                if action.startswith("climate_"):
                    result = await self._execute_climate_action(action, parameters)
                elif action.startswith("lights_"):
                    result = await self._execute_lights_action(action, parameters)
                elif action.startswith("seats_"):
                    result = await self._execute_seats_action(action, parameters)
                elif action.startswith("infotainment_"):
                    result = await self._execute_infotainment_action(action, parameters)
                else:
                    result["error"] = f"Unknown action category: {action}"
                    logger.warning(f"Unknown action: {action}")

                # Update timestamp if successful
                if result.get("success"):
                    self.state.last_updated = time.time()
                    logger.info(f"Command executed successfully: {result}")
                    await self._notify_update_callbacks(action, parameters, result)
                else:
                    logger.warning(f"Command execution failed: {result}")

                return result

            except Exception as e:
                logger.error(f"Error executing command {action}: {e}", exc_info=True)
                return {"action": action, "success": False, "error": str(e)}

    async def _execute_climate_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute climate-related actions"""
        result = {"action": action, "success": False, "changes": {}}

        if action == "climate_set_temperature":
            temp = parameters.get("temperature", 22)
            if isinstance(temp, (int, float)):
                self.state.climate.temperature = float(max(16, min(32, temp)))
                result["success"] = True
                result["changes"]["temperature"] = self.state.climate.temperature
            else:
                result["error"] = "Invalid temperature value"

        elif action == "climate_turn_on_ac":
            self.state.climate.ac_enabled = True
            result["success"] = True
            result["changes"]["ac_enabled"] = True

        elif action == "climate_turn_off_ac":
            self.state.climate.ac_enabled = False
            result["success"] = True
            result["changes"]["ac_enabled"] = False

        elif action == "climate_increase_temperature" or action == "climate_increase":
            current_temp = self.state.climate.temperature
            new_temp = min(32, current_temp + 1)
            self.state.climate.temperature = new_temp
            result["success"] = True
            result["changes"]["temperature"] = new_temp

        elif action == "climate_decrease_temperature" or action == "climate_decrease":
            current_temp = self.state.climate.temperature
            new_temp = max(16, current_temp - 1)
            self.state.climate.temperature = new_temp
            result["success"] = True
            result["changes"]["temperature"] = new_temp

        elif action == "climate_set_fan_speed":
            speed = parameters.get("speed", 3)
            if isinstance(speed, int) and 1 <= speed <= 5:
                self.state.climate.fan_speed = speed
                result["success"] = True
                result["changes"]["fan_speed"] = speed
            else:
                result["error"] = "Invalid fan speed"

        elif action == "climate_toggle_auto":
            self.state.climate.auto_mode = not self.state.climate.auto_mode
            result["success"] = True
            result["changes"]["auto_mode"] = self.state.climate.auto_mode

        elif action == "climate_toggle_recirculation":
            self.state.climate.recirculation = not self.state.climate.recirculation
            result["success"] = True
            result["changes"]["recirculation"] = self.state.climate.recirculation

        else:
            result["error"] = f"Unknown climate action: {action}"

        return result

    async def _execute_lights_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute lights-related actions"""
        result = {"action": action, "success": False, "changes": {}}

        if action == "lights_turn_on":
            self.state.lights.interior_lights = True
            self.state.lights.ambient_lights = True
            result["success"] = True
            result["changes"]["interior_lights"] = True
            result["changes"]["ambient_lights"] = True

        elif action == "lights_turn_off":
            self.state.lights.interior_lights = False
            self.state.lights.ambient_lights = False
            self.state.lights.reading_lights = False
            result["success"] = True
            result["changes"]["interior_lights"] = False
            result["changes"]["ambient_lights"] = False
            result["changes"]["reading_lights"] = False

        elif action == "lights_set_brightness" or action == "lights_set":
            brightness = parameters.get("brightness", 80)
            if isinstance(brightness, (int, float)):
                self.state.lights.brightness = int(max(0, min(100, brightness)))
                result["success"] = True
                result["changes"]["brightness"] = self.state.lights.brightness
            else:
                result["error"] = "Invalid brightness value"

        elif action == "lights_brighten":
            current = self.state.lights.brightness
            new_brightness = min(100, current + 10)
            self.state.lights.brightness = new_brightness
            result["success"] = True
            result["changes"]["brightness"] = new_brightness

        elif action == "lights_dim":
            current = self.state.lights.brightness
            new_brightness = max(0, current - 10)
            self.state.lights.brightness = new_brightness
            result["success"] = True
            result["changes"]["brightness"] = new_brightness

        elif action == "lights_toggle_interior":
            self.state.lights.interior_lights = not self.state.lights.interior_lights
            result["success"] = True
            result["changes"]["interior_lights"] = self.state.lights.interior_lights

        elif action == "lights_toggle_ambient":
            self.state.lights.ambient_lights = not self.state.lights.ambient_lights
            result["success"] = True
            result["changes"]["ambient_lights"] = self.state.lights.ambient_lights

        elif action == "lights_toggle_reading":
            self.state.lights.reading_lights = not self.state.lights.reading_lights
            result["success"] = True
            result["changes"]["reading_lights"] = self.state.lights.reading_lights

        elif action == "lights_set_color":
            color = parameters.get("color", "white")
            if color in ["white", "blue", "red", "green", "purple", "orange"]:
                self.state.lights.ambient_color = color
                result["success"] = True
                result["changes"]["ambient_color"] = color
            else:
                result["error"] = "Invalid color"

        else:
            result["error"] = f"Unknown lights action: {action}"

        return result

    async def _execute_seats_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute seats-related actions"""
        result = {"action": action, "success": False, "changes": {}}
        seat = parameters.get("seat", "driver")

        if action == "seats_heat_on":
            if seat == "driver":
                self.state.seats.driver_heating = True
                result["changes"]["driver_heating"] = True
            else:
                self.state.seats.passenger_heating = True
                result["changes"]["passenger_heating"] = True
            result["success"] = True

        elif action == "seats_heat_off":
            if seat == "driver":
                self.state.seats.driver_heating = False
                result["changes"]["driver_heating"] = False
            else:
                self.state.seats.passenger_heating = False
                result["changes"]["passenger_heating"] = False
            result["success"] = True

        elif action == "seats_massage_on":
            if seat == "driver":
                self.state.seats.driver_massage = True
                result["changes"]["driver_massage"] = True
            else:
                self.state.seats.passenger_massage = True
                result["changes"]["passenger_massage"] = True
            result["success"] = True

        elif action == "seats_massage_off":
            if seat == "driver":
                self.state.seats.driver_massage = False
                result["changes"]["driver_massage"] = False
            else:
                self.state.seats.passenger_massage = False
                result["changes"]["passenger_massage"] = False
            result["success"] = True

        elif action == "seats_adjust_position" or action == "seats_adjust":
            position = parameters.get("position", {})
            if isinstance(position, dict):
                if seat == "driver":
                    if "height" in position:
                        self.state.seats.driver_position["height"] = max(0, min(100, position["height"]))
                    if "tilt" in position:
                        self.state.seats.driver_position["tilt"] = max(0, min(100, position["tilt"]))
                    if "lumbar" in position:
                        self.state.seats.driver_position["lumbar"] = max(0, min(100, position["lumbar"]))
                    result["changes"]["driver_position"] = self.state.seats.driver_position
                else:
                    if "height" in position:
                        self.state.seats.passenger_position["height"] = max(0, min(100, position["height"]))
                    if "tilt" in position:
                        self.state.seats.passenger_position["tilt"] = max(0, min(100, position["tilt"]))
                    if "lumbar" in position:
                        self.state.seats.passenger_position["lumbar"] = max(0, min(100, position["lumbar"]))
                    result["changes"]["passenger_position"] = self.state.seats.passenger_position
                result["success"] = True
            else:
                result["error"] = "Invalid position format"

        else:
            result["error"] = f"Unknown seats action: {action}"

        return result

    async def _execute_infotainment_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute infotainment-related actions"""
        result = {"action": action, "success": False, "changes": {}}

        if action == "infotainment_set_volume" or action == "infotainment_set":
            volume = parameters.get("volume", 50)
            if isinstance(volume, (int, float)):
                self.state.infotainment.volume = int(max(0, min(100, volume)))
                result["success"] = True
                result["changes"]["volume"] = self.state.infotainment.volume
            else:
                result["error"] = "Invalid volume value"

        elif action == "infotainment_volume_up" or action == "infotainment_increase":
            current_volume = self.state.infotainment.volume
            new_volume = min(100, current_volume + 5)
            self.state.infotainment.volume = new_volume
            result["success"] = True
            result["changes"]["volume"] = new_volume

        elif action == "infotainment_volume_down" or action == "infotainment_decrease":
            current_volume = self.state.infotainment.volume
            new_volume = max(0, current_volume - 5)
            self.state.infotainment.volume = new_volume
            result["success"] = True
            result["changes"]["volume"] = new_volume

        elif action == "infotainment_play":
            self.state.infotainment.playing = True
            result["success"] = True
            result["changes"]["playing"] = True

        elif action == "infotainment_pause" or action == "infotainment_stop":
            self.state.infotainment.playing = False
            result["success"] = True
            result["changes"]["playing"] = False

        elif action == "infotainment_mute":
            self.state.infotainment.muted = True
            result["success"] = True
            result["changes"]["muted"] = True

        elif action == "infotainment_unmute":
            self.state.infotainment.muted = False
            result["success"] = True
            result["changes"]["muted"] = False

        elif action == "infotainment_next_track":
            self.state.infotainment.track = "Next Track"
            result["success"] = True
            result["changes"]["track"] = "Next Track"

        elif action == "infotainment_previous_track":
            self.state.infotainment.track = "Previous Track"
            result["success"] = True
            result["changes"]["track"] = "Previous Track"

        elif action == "infotainment_set_source":
            source = parameters.get("source", "radio")
            if source in ["radio", "bluetooth", "usb", "aux", "music"]:
                self.state.infotainment.source = source
                result["success"] = True
                result["changes"]["source"] = source
            else:
                result["error"] = "Invalid source"

        elif action == "infotainment_radio_tune":
            station = parameters.get("station", "FM 101.5")
            self.state.infotainment.station = station
            self.state.infotainment.source = "radio"
            self.state.infotainment.playing = True
            result["success"] = True
            result["changes"]["station"] = station
            result["changes"]["source"] = "radio"
            result["changes"]["playing"] = True

        else:
            result["error"] = f"Unknown infotainment action: {action}"

        return result

    async def _notify_update_callbacks(self, action: str, parameters: Dict[str, Any], result: Any):
        """Notify all registered update callbacks"""
        for callback in self._update_callbacks:
            try:
                await callback(action, parameters, result)
            except Exception as e:
                logger.error(f"Error in update callback: {e}")

    def register_update_callback(self, callback):
        """Register a callback to be called when state updates"""
        self._update_callbacks.append(callback)
        logger.info(f"Registered update callback: {callback.__name__}")

    def unregister_update_callback(self, callback):
        """Unregister an update callback"""
        if callback in self._update_callbacks:
            self._update_callbacks.remove(callback)
            logger.info(f"Unregistered update callback: {callback.__name__}")

    def get_all_states(self) -> Dict[str, Any]:
        """Get all vehicle states as a dictionary"""
        return self.state.dict()

    def get_climate_state(self) -> ClimateState:
        """Get current climate state"""
        return self.state.climate

    def get_lights_state(self) -> LightsState:
        """Get current lights state"""
        return self.state.lights

    def get_seats_state(self) -> SeatsState:
        """Get current seats state"""
        return self.state.seats

    def get_infotainment_state(self) -> InfotainmentState:
        """Get current infotainment state"""
        return self.state.infotainment

    async def reset_all_states(self):
        """Reset all vehicle states to defaults"""
        async with self._lock:
            self.state = VehicleState()
            self.state.last_updated = time.time()
            logger.info("All vehicle states reset to defaults")
            await self._notify_update_callbacks("reset_all", {}, {"success": True})

    # Legacy method for backward compatibility
    async def process_nlp_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Process NLP action - redirects to execute_command"""
        return await self.execute_command(action, parameters)