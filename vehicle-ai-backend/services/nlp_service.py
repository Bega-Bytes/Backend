# Add these methods to your existing services/nlp_service.py

def intent_to_action(self, intent: str) -> str:
    """Map intent to vehicle action"""
    intent_action_map = {
        "climate_turn_on": "climate_turn_on",
        "climate_turn_off": "climate_turn_off",
        "climate_set_temperature": "climate_set_temperature",
        "climate_increase": "climate_increase",
        "climate_decrease": "climate_decrease",
        "infotainment_play": "infotainment_play",
        "infotainment_stop": "infotainment_stop",
        "infotainment_volume_up": "infotainment_volume_up",
        "infotainment_volume_down": "infotainment_volume_down",
        "infotainment_set_volume": "infotainment_set_volume",
        "lights_turn_on": "lights_turn_on",
        "lights_turn_off": "lights_turn_off",
        "lights_dim": "lights_dim",
        "lights_brighten": "lights_brighten",
        "seats_heat_on": "seats_heat_on",
        "seats_heat_off": "seats_heat_off",
        "seats_adjust": "seats_adjust",
        "unknown": "unknown"
    }

    return intent_action_map.get(intent, "unknown")


def extract_parameters_from_entities(self, entities: Dict) -> Dict:
    """Extract parameters from entities dictionary"""
    parameters = {}

    # Look for temperature values
    if "temperature" in entities:
        try:
            temp = int(entities["temperature"])
            parameters["temperature"] = max(16, min(32, temp))
        except (ValueError, TypeError):
            pass

    # Look for volume values
    if "volume" in entities:
        try:
            vol = int(entities["volume"])
            parameters["volume"] = max(0, min(100, vol))
        except (ValueError, TypeError):
            pass

    # Look for brightness values
    if "brightness" in entities:
        try:
            bright = int(entities["brightness"])
            parameters["brightness"] = max(0, min(100, bright))
        except (ValueError, TypeError):
            pass

    return parameters


async def process_command(self, text: str) -> Tuple[str, float, Dict]:
    """Process command and return intent, confidence, entities"""
    text_lower = text.lower().strip()

    # Try to match patterns
    for intent, patterns in self.intent_patterns.items():
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                confidence = self._calculate_confidence(text_lower, pattern)
                entities = self._extract_entities(match, intent)
                return intent, confidence, entities

    # No match found
    return "unknown", 0.0, {}


def _extract_entities(self, match, intent: str) -> Dict:
    """Extract entities from regex match"""
    entities = {}

    if match.groups():
        if intent == "climate_set_temperature":
            try:
                entities["temperature"] = int(match.group(1))
            except (ValueError, IndexError):
                pass

        elif intent == "infotainment_set_volume":
            try:
                entities["volume"] = int(match.group(1))
            except (ValueError, IndexError):
                pass

    return entities


def get_test_commands(self) -> List[str]:
    """Get list of test commands for development"""
    return [
        # Climate commands
        "Turn on climate control",
        "Set temperature to 24 degrees",
        "Make it cooler",
        "Turn off the heat",

        # Audio commands
        "Play music",
        "Set volume to 75",
        "Turn up the volume",
        "Stop the music",

        # Lighting commands
        "Turn on the lights",
        "Dim the lights",
        "Brighten the interior",
        "Turn off lights",

        # Seat commands
        "Heat the seats",
        "Turn off seat heating",
        "Adjust my seat",

        # Complex commands
        "Set temperature to 22 and turn on music",
        "Turn on lights and heat seats",
        "Make it warmer and turn up volume"
    ]