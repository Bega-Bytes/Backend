import httpx
import json
from typing import Dict, Any, Optional
import logging
import asyncio
from config import settings

logger = logging.getLogger("ml-parser-service")


class MLParserService:
    """Service to communicate with the ML command parser"""

    def __init__(self, ml_service_url: str = None):
        self.ml_service_url = ml_service_url or settings.ML_SERVICE_URL
        self.timeout = httpx.Timeout(settings.ML_SERVICE_TIMEOUT)
        self.client = httpx.AsyncClient(timeout=self.timeout)
        self._service_available = None  # Cache service availability
        self._last_health_check = 0
        self.health_check_interval = 60  # Check health every 60 seconds

        logger.info(f"🔗 ML Parser Service initialized with URL: {self.ml_service_url}")

    async def parse_command(self, text: str) -> Dict[str, Any]:
        """Send voice command to ML parser service"""
        if not text or not text.strip():
            logger.warning("⚠️ Empty text provided to parse_command")
            return await self._create_fallback_result(text, "Empty command")

        text = text.strip()
        logger.info(f"📤 Sending to ML service: '{text}'")

        try:
            # Check service health periodically
            if not await self._is_service_healthy():
                logger.warning("⚠️ ML service unhealthy, using fallback")
                return await self._create_fallback_result(text, "Service unavailable")

            # Send parsing request
            logger.info(f"📡 Posting to {self.ml_service_url}/parse")

            request_data = {"text": text}
            logger.debug(f"📤 Request data: {request_data}")

            response = await self.client.post(
                f"{self.ml_service_url}/parse",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )

            logger.info(f"📥 ML service response status: {response.status_code}")

            if response.status_code == 200:
                try:
                    result = response.json()
                    logger.info(f"✅ ML parsing successful: {result}")

                    # Validate and normalize the result
                    normalized_result = self._normalize_ml_result(result)
                    logger.debug(f"🔄 Normalized result: {normalized_result}")

                    return normalized_result

                except json.JSONDecodeError as e:
                    logger.error(f"❌ Failed to parse ML service JSON response: {e}")
                    logger.error(f"Raw response: {response.text[:500]}")
                    return await self._create_fallback_result(text, "Invalid JSON response")

            else:
                logger.error(f"❌ ML service error: {response.status_code}")
                try:
                    error_detail = response.text[:500]
                    logger.error(f"Error details: {error_detail}")
                except:
                    pass
                return await self._create_fallback_result(text, f"HTTP {response.status_code}")

        except httpx.TimeoutException:
            logger.error("⏰ ML service timeout")
            self._service_available = False
            return await self._create_fallback_result(text, "Service timeout")

        except httpx.ConnectError as e:
            logger.error(f"🔌 Cannot connect to ML service: {e}")
            self._service_available = False
            return await self._create_fallback_result(text, "Connection failed")

        except Exception as e:
            logger.error(f"❌ ML Parser service unexpected error: {e}", exc_info=True)
            return await self._create_fallback_result(text, f"Unexpected error: {str(e)}")

    async def _is_service_healthy(self) -> bool:
        """Check if ML service is available and healthy"""
        import time
        current_time = time.time()

        # Use cached result if recent
        if (self._service_available is not None and
                current_time - self._last_health_check < self.health_check_interval):
            return self._service_available

        try:
            logger.debug("🏥 Checking ML service health...")
            health_response = await self.client.get(
                f"{self.ml_service_url}/healthz",
                timeout=5.0  # Shorter timeout for health checks
            )

            is_healthy = health_response.status_code == 200
            logger.debug(f"🏥 Health check result: {is_healthy} (status: {health_response.status_code})")

            self._service_available = is_healthy
            self._last_health_check = current_time

            return is_healthy

        except Exception as e:
            logger.warning(f"🏥 Health check failed: {e}")
            self._service_available = False
            self._last_health_check = current_time
            return False

    def _normalize_ml_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize ML service result to expected format"""
        # Handle different possible response formats from ML service
        normalized = {
            "action": "unknown",
            "confidence": 0.0,
            "parameters": {},
            "intent": "unknown",
            "source": "ml_parser"
        }

        try:
            # Extract action
            if "action" in result:
                normalized["action"] = str(result["action"])
            elif "intent" in result:
                # Some models might return intent instead of action
                normalized["action"] = str(result["intent"])

            # Extract confidence
            if "confidence" in result:
                confidence = result["confidence"]
                if isinstance(confidence, (int, float)):
                    normalized["confidence"] = float(confidence)
                    # Ensure confidence is between 0 and 1
                    if normalized["confidence"] > 1.0:
                        normalized["confidence"] = normalized["confidence"] / 100.0

            # Extract parameters/entities
            if "parameters" in result:
                normalized["parameters"] = result["parameters"] if isinstance(result["parameters"], dict) else {}
            elif "entities" in result:
                normalized["parameters"] = result["entities"] if isinstance(result["entities"], dict) else {}

            # Extract intent
            if "intent" in result:
                normalized["intent"] = str(result["intent"])
            elif "domain" in result:
                normalized["intent"] = str(result["domain"])

            # Add original result for debugging
            normalized["original_result"] = result

        except Exception as e:
            logger.error(f"❌ Error normalizing ML result: {e}")
            logger.error(f"Original result: {result}")

        return normalized

    async def _create_fallback_result(self, text: str, reason: str) -> Dict[str, Any]:
        """Create a fallback result when ML service is unavailable"""
        logger.info(f"🔄 Creating fallback result for '{text}' (reason: {reason})")

        # Simple keyword-based fallback
        fallback_result = {
            "action": "unknown",
            "confidence": 0.1,
            "parameters": {},
            "intent": "unknown",
            "source": "fallback",
            "fallback_reason": reason
        }

        # Basic keyword detection for common commands
        text_lower = text.lower()

        # Climate keywords
        if any(word in text_lower for word in ["temperature", "temp", "hot", "cold", "ac", "air", "climate"]):
            fallback_result.update({
                "action": "climate_unknown",
                "intent": "climate",
                "confidence": 0.3
            })

        # Lights keywords
        elif any(word in text_lower for word in ["light", "lights", "bright", "dim", "lamp"]):
            fallback_result.update({
                "action": "lights_unknown",
                "intent": "lights",
                "confidence": 0.3
            })

        # Music/infotainment keywords
        elif any(word in text_lower for word in ["music", "song", "play", "volume", "radio"]):
            fallback_result.update({
                "action": "infotainment_unknown",
                "intent": "infotainment",
                "confidence": 0.3
            })

        # Seat keywords
        elif any(word in text_lower for word in ["seat", "heating", "massage", "position"]):
            fallback_result.update({
                "action": "seats_unknown",
                "intent": "seats",
                "confidence": 0.3
            })

        logger.info(f"🔄 Fallback result: {fallback_result}")
        return fallback_result

    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to ML service"""
        try:
            # Test health endpoint
            health_response = await self.client.get(f"{self.ml_service_url}/healthz")
            health_status = health_response.status_code == 200

            # Test parse endpoint with simple command
            test_command = "turn on lights"
            parse_response = await self.client.post(
                f"{self.ml_service_url}/parse",
                json={"text": test_command}
            )
            parse_status = parse_response.status_code == 200

            return {
                "service_url": self.ml_service_url,
                "health_check": health_status,
                "parse_test": parse_status,
                "overall_status": health_status and parse_status,
                "timestamp": asyncio.get_event_loop().time()
            }

        except Exception as e:
            return {
                "service_url": self.ml_service_url,
                "health_check": False,
                "parse_test": False,
                "overall_status": False,
                "error": str(e),
                "timestamp": asyncio.get_event_loop().time()
            }

    async def close(self):
        """Close the HTTP client"""
        try:
            await self.client.aclose()
            logger.info("🔌 ML Parser Service HTTP client closed")
        except Exception as e:
            logger.error(f"❌ Error closing ML Parser Service client: {e}")

    def __del__(self):
        """Cleanup when object is destroyed"""
        try:
            if hasattr(self, 'client') and self.client:
                # Note: We can't call async close() in __del__
                # This is just for cleanup notification
                logger.debug("🗑️ ML Parser Service object destroyed")
        except:
            pass