# services/speech_service.py
import logging
import tempfile
import os
from typing import Optional, Dict, Any
from openai import OpenAI
from config import settings

logger = logging.getLogger("speech-service")


class SpeechService:
    """Service for handling speech-to-text conversion using OpenAI Whisper"""

    def __init__(self):
        self.client = None
        self.model = "whisper-1"

        if settings.OPENAI_API_KEY:
            try:
                self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("✅ OpenAI Speech client initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize OpenAI client: {e}")
                self.client = None
        else:
            logger.warning("⚠️ No OpenAI API key found, speech-to-text disabled")

    def is_available(self) -> bool:
        """Check if speech-to-text service is available"""
        return self.client is not None

    async def transcribe_audio(self, audio_data: bytes, file_format: str = "webm") -> Dict[str, Any]:
        """
        Transcribe audio data to text using OpenAI Whisper

        Args:
            audio_data: Raw audio bytes
            file_format: Audio format (webm, mp3, wav, etc.)

        Returns:
            Dict with transcription result and metadata
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "Speech-to-text service not available",
                "text": ""
            }

        try:
            logger.info(f"🎤 Transcribing audio ({len(audio_data)} bytes, format: {file_format})")

            # Create temporary file for audio data
            with tempfile.NamedTemporaryFile(suffix=f".{file_format}", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name

            try:
                # Transcribe using OpenAI Whisper
                with open(temp_file_path, "rb") as audio_file:
                    transcript = self.client.audio.transcriptions.create(
                        model=self.model,
                        file=audio_file,
                        response_format="verbose_json",  # Get confidence and timing info
                        language="en"  # Specify English for better accuracy
                    )

                # Extract transcription text
                transcribed_text = transcript.text.strip()

                logger.info(f"🎯 Transcription successful: '{transcribed_text}'")

                return {
                    "success": True,
                    "text": transcribed_text,
                    "duration": getattr(transcript, 'duration', None),
                    "language": getattr(transcript, 'language', 'en'),
                    "confidence": self._estimate_confidence(transcribed_text),
                    "word_count": len(transcribed_text.split()) if transcribed_text else 0
                }

            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except Exception as e:
                    logger.warning(f"Failed to delete temp file: {e}")

        except Exception as e:
            logger.error(f"❌ Transcription failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": ""
            }

    def _estimate_confidence(self, text: str) -> float:
        """
        Estimate confidence based on text characteristics
        (Whisper doesn't provide confidence scores in the current API)
        """
        if not text:
            return 0.0

        # Simple heuristics for confidence estimation
        confidence = 0.8  # Base confidence

        # Reduce confidence for very short transcriptions
        if len(text) < 10:
            confidence -= 0.2

        # Reduce confidence if text contains many numbers or special chars
        special_char_ratio = sum(1 for c in text if not c.isalnum() and not c.isspace()) / len(text)
        if special_char_ratio > 0.3:
            confidence -= 0.1

        # Reduce confidence for very long transcriptions (might be hallucination)
        if len(text) > 200:
            confidence -= 0.1

        return max(0.0, min(1.0, confidence))

    def test_connection(self) -> bool:
        """Test if the OpenAI API connection is working"""
        try:
            if not self.client:
                return False

            # Try to list available models to test connection
            models = self.client.models.list()
            return True

        except Exception as e:
            logger.error(f"❌ Connection test failed: {e}")
            return False