# api_server.py (Enhanced version)
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import logging
import time
import uvicorn
import sys
import os

# Add src to path to import your modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from main import EnsembleCommandParser
    from utils.text_processing import preprocess_text

    PARSER_AVAILABLE = True
except ImportError as e:
    logging.error(f"❌ Failed to import parser modules: {e}")
    PARSER_AVAILABLE = False

app = FastAPI(
    title="ML Command Parser API",
    description="Advanced Vehicle Command Parser with ML/LLM Ensemble",
    version="1.0.0"
)

# Initialize parser if available
if PARSER_AVAILABLE:
    try:
        parser = EnsembleCommandParser()
        logging.info("✅ ML Parser initialized successfully")
    except Exception as e:
        logging.error(f"❌ Failed to initialize ML Parser: {e}")
        parser = None
        PARSER_AVAILABLE = False
else:
    parser = None


class CommandRequest(BaseModel):
    text: str
    test_mode: Optional[bool] = False
    simulate_corruption: Optional[bool] = False


class CommandResponse(BaseModel):
    intent: str
    confidence: float
    action: str
    parameters: dict
    processing_time: float
    source: str
    original_text: str
    processed_text: Optional[str] = None


class TestResult(BaseModel):
    success: bool
    message: str
    data: dict


@app.post("/parse", response_model=CommandResponse)
async def parse_command(request: CommandRequest):
    """Parse voice command using ML/LLM ensemble"""
    if not PARSER_AVAILABLE or not parser:
        raise HTTPException(
            status_code=503,
            detail="ML Parser not available. Check logs for initialization errors."
        )

    start_time = time.time()

    try:
        original_text = request.text
        processed_text = original_text

        # Apply text preprocessing if available
        if hasattr(parser, 'preprocess_text'):
            processed_text = parser.preprocess_text(original_text)

        # Parse the command
        result = parser.parse_command(processed_text)

        processing_time = time.time() - start_time

        # Ensure result has all required fields
        response = CommandResponse(
            intent=result.get("intent", "unknown"),
            confidence=result.get("confidence", 0.0),
            action=result.get("action", "unknown"),
            parameters=result.get("parameters", {}),
            processing_time=processing_time,
            source=result.get("source", "ml_ensemble"),
            original_text=original_text,
            processed_text=processed_text if processed_text != original_text else None
        )

        logging.info(f"✅ Parsed '{original_text}' -> {result.get('action')} ({result.get('confidence'):.2f})")

        return response

    except Exception as e:
        logging.error(f"❌ Parsing error: {e}")
        raise HTTPException(status_code=500, detail=f"Parsing failed: {str(e)}")


@app.post("/test-parse", response_model=TestResult)
async def test_parse_command(request: CommandRequest):
    """Test parsing without execution - useful for development"""
    if not PARSER_AVAILABLE or not parser:
        return TestResult(
            success=False,
            message="ML Parser not available",
            data={"error": "Parser not initialized"}
        )

    try:
        start_time = time.time()

        # Parse the command
        result = parser.parse_command(request.text)
        processing_time = time.time() - start_time

        # Add debugging information
        debug_info = {
            "original_text": request.text,
            "parsed_result": result,
            "processing_time": processing_time,
            "confidence_breakdown": getattr(parser, 'get_confidence_breakdown', lambda x: {})(request.text),
            "parser_method": result.get("source", "unknown")
        }

        return TestResult(
            success=True,
            message="Command parsed successfully (test mode)",
            data=debug_info
        )

    except Exception as e:
        logging.error(f"❌ Test parsing error: {e}")
        return TestResult(
            success=False,
            message=f"Test parsing failed: {str(e)}",
            data={"error": str(e)}
        )


@app.get("/test-commands")
async def get_test_commands():
    """Get list of test commands for development"""
    test_commands = [
        # Clean commands
        "Set temperature to 24 degrees",
        "Turn up the volume",
        "Turn on the lights",
        "Heat the seats",
        "Play some music",

        # Corrupted commands (what your ML model is trained for)
        "sit temprature too 24",  # set temperature to 24
        "tern up thee valium",  # turn up the volume
        "tern on thee lights",  # turn on the lights
        "heat thee sits",  # heat the seats
        "play sum musik",  # play some music

        # Complex commands
        "make it cooler and turn up music",
        "dim lights and heat seats to level 2",
    ]

    return TestResult(
        success=True,
        message="Available test commands",
        data={
            "commands": test_commands,
            "total_count": len(test_commands),
            "description": "Mix of clean and corrupted commands for testing ML model robustness"
        }
    )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy" if PARSER_AVAILABLE else "degraded",
        "parser_available": PARSER_AVAILABLE,
        "timestamp": time.time()
    }


@app.get("/status")
async def get_status():
    """Get detailed status information"""
    status = {
        "parser_available": PARSER_AVAILABLE,
        "timestamp": time.time(),
        "version": "1.0.0"
    }

    if PARSER_AVAILABLE and parser:
        try:
            # Get parser-specific status
            status.update({
                "ml_model_loaded": hasattr(parser, 'ml_parser') and parser.ml_parser is not None,
                "llm_fallback_available": hasattr(parser, 'llm_fallback') and parser.llm_fallback is not None,
                "confidence_threshold": getattr(parser, 'confidence_threshold', 0.1)
            })
        except Exception as e:
            status["parser_error"] = str(e)

    return status


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "ML Command Parser API",
        "status": "running",
        "parser_available": PARSER_AVAILABLE,
        "endpoints": {
            "parse": "/parse - Parse voice commands",
            "test": "/test-parse - Test parsing without execution",
            "commands": "/test-commands - Get test commands",
            "health": "/health - Health check",
            "status": "/status - Detailed status",
            "docs": "/docs - API documentation"
        }
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("🧠 Starting ML Command Parser API...")
    print(f"🌐 Server: http://localhost:8001")
    print(f"📚 API Docs: http://localhost:8001/docs")
    print("=" * 50)

    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )