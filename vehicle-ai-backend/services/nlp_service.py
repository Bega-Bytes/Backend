import re
from typing import Dict, List, Optional, Tuple
from models.schemas import NLPResponse

class NLPService:
    """Natural Language Processing service for vehicle commands"""
    
    def __init__(self):
        # Define the available actions
        self.actions = [
            "climate_turn_on", "climate_turn_off", "climate_set_temperature", 
            "climate_increase", "climate_decrease",
            "infotainment_play", "infotainment_stop", "infotainment_volume_up", 
            "infotainment_volume_down", "infotainment_set_volume",
            "lights_turn_on", "lights_turn_off", "lights_dim", "lights_brighten",
            "seats_heat_on", "seats_heat_off", "seats_adjust"
        ]
        
        # Define intent patterns for each category
        self.intent_patterns = {
            # Climate patterns
            "climate_turn_on": [
                r"turn on (the )?climate", r"start (the )?air conditioning", r"turn on (the )?ac",
                r"start (the )?heating", r"turn on (the )?heat"
            ],
            "climate_turn_off": [
                r"turn off (the )?climate", r"stop (the )?air conditioning", r"turn off (the )?ac",
                r"stop (the )?heating", r"turn off (the )?heat"
            ],
            "climate_set_temperature": [
                r"set temperature to (\d+)", r"set temp to (\d+)", r"make it (\d+) degrees"
            ],
            "climate_increase": [
                r"increase temperature", r"turn up (the )?heat", r"make it warmer", r"hotter"
            ],
            "climate_decrease": [
                r"decrease temperature", r"turn down (the )?heat", r"make it cooler", r"colder"
            ],
            
            # Infotainment patterns
            "infotainment_play": [
                r"play music", r"start music", r"resume", r"play", r"start playing"
            ],
            "infotainment_stop": [
                r"stop music", r"pause", r"stop playing", r"stop"
            ],
            "infotainment_volume_up": [
                r"volume up", r"turn up volume", r"louder", r"increase volume"
            ],
            "infotainment_volume_down": [
                r"volume down", r"turn down volume", r"quieter", r"decrease volume"
            ],
            "infotainment_set_volume": [
                r"set volume to (\d+)", r"volume (\d+)"
            ],
            
            # Lights patterns
            "lights_turn_on": [
                r"turn on (the )?lights", r"lights on", r"interior lights on"
            ],
            "lights_turn_off": [
                r"turn off (the )?lights", r"lights off", r"interior lights off"
            ],
            "lights_dim": [
                r"dim (the )?lights", r"make lights dimmer", r"darker lights"
            ],
            "lights_brighten": [
                r"brighten (the )?lights", r"make lights brighter", r"brighter lights"
            ],
            
            # Seats patterns
            "seats_heat_on": [
                r"turn on seat heating", r"heat (the )?seats", r"heated seats on"
            ],
            "seats_heat_off": [
                r"turn off seat heating", r"stop heating seats", r"heated seats off"
            ],
            "seats_adjust": [
                r"adjust (the )?seat", r"move (the )?seat", r"seat position"
            ]
        }
    
    async def process_command(self, text: str) -> NLPResponse:
        """Process a natural language command and return structured response"""
        text = text.lower().strip()
        
        # Find matching intent and extract parameters
        intent, confidence, parameters = self._classify_intent(text)
        
        if intent:
            return NLPResponse(
                intent=intent,
                confidence=confidence,
                entities=parameters,
                action=intent,
                parameters=parameters
            )
        else:
            return NLPResponse(
                intent="unknown",
                confidence=0.0,
                entities={},
                action="unknown",
                parameters={}
            )
    
    def _classify_intent(self, text: str) -> Tuple[Optional[str], float, Dict]:
        """Classify the intent from the input text"""
        best_match = None
        best_confidence = 0.0
        best_parameters = {}
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    confidence = self._calculate_confidence(text, pattern)
                    if confidence > best_confidence:
                        best_match = intent
                        best_confidence = confidence
                        best_parameters = self._extract_parameters(match, intent)
        
        return best_match, best_confidence, best_parameters
    
    def _calculate_confidence(self, text: str, pattern: str) -> float:
        """Calculate confidence score for a pattern match"""
        # Simple confidence calculation based on pattern coverage
        pattern_words = len(pattern.split())
        text_words = len(text.split())
        
        # Base confidence for exact matches
        confidence = 0.8
        
        # Adjust confidence based on text length vs pattern length
        if text_words <= pattern_words + 2:
            confidence += 0.2
        
        return min(confidence, 1.0)
    
    def _extract_parameters(self, match, intent: str) -> Dict:
        """Extract parameters from regex match groups"""
        parameters = {}
        
        if match.groups():
            if intent == "climate_set_temperature":
                try:
                    temperature = int(match.group(1))
                    parameters["temperature"] = max(16, min(32, temperature))
                except (ValueError, IndexError):
                    pass
            
            elif intent == "infotainment_set_volume":
                try:
                    volume = int(match.group(1))
                    parameters["volume"] = max(0, min(100, volume))
                except (ValueError, IndexError):
                    pass
        
        return parameters
    
    async def get_response_text(self, intent: str, parameters: Dict = None) -> str:
        """Generate a natural language response for the processed command"""
        if parameters is None:
            parameters = {}
        
        responses = {
            "climate_turn_on": "Climate control turned on.",
            "climate_turn_off": "Climate control turned off.",
            "climate_set_temperature": f"Temperature set to {parameters.get('temperature', 'default')} degrees.",
            "climate_increase": "Temperature increased.",
            "climate_decrease": "Temperature decreased.",
            
            "infotainment_play": "Music playing.",
            "infotainment_stop": "Music stopped.",
            "infotainment_volume_up": "Volume increased.",
            "infotainment_volume_down": "Volume decreased.",
            "infotainment_set_volume": f"Volume set to {parameters.get('volume', 'default')}%.",
            
            "lights_turn_on": "Interior lights turned on.",
            "lights_turn_off": "Interior lights turned off.",
            "lights_dim": "Lights dimmed.",
            "lights_brighten": "Lights brightened.",
            
            "seats_heat_on": "Seat heating turned on.",
            "seats_heat_off": "Seat heating turned off.",
            "seats_adjust": "Seat position adjusted.",
            
            "unknown": "I didn't understand that command. Please try again."
        }
        
        return responses.get(intent, "Command processed.")
    
    def get_available_commands(self) -> List[str]:
        """Return list of available voice commands"""
        return [
            "Turn on climate control",
            "Set temperature to 24 degrees",
            "Play music",
            "Volume up",
            "Turn on lights",
            "Heat the seats",
            "And many more..."
        ]