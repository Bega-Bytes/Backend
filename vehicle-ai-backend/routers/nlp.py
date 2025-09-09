from fastapi import APIRouter, HTTPException, Request
from models.schemas import VoiceCommand, NLPResponse, APIResponse
from services.nlp_service import NLPService
import asyncio

router = APIRouter()
nlp_service = NLPService()

@router.post("/process-command", response_model=NLPResponse)
async def process_voice_command(command: VoiceCommand, request: Request):
    """Process a natural language voice command"""
    try:
        # Process the command through NLP
        nlp_response = await nlp_service.process_command(command.text)
        
        # If we have a valid action, execute it
        if nlp_response.action != "unknown":
            await execute_vehicle_action(nlp_response, request)
        
        return nlp_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute-action", response_model=APIResponse)
async def execute_action_endpoint(action: str, parameters: dict, request: Request):
    """Execute a specific vehicle action with parameters"""
    try:
        vehicle_state = request.app.state.vehicle_state
        connection_manager = request.app.state.connection_manager
        
        # Execute the action through vehicle state manager
        result = await vehicle_state.process_nlp_action(action, parameters)
        
        # Generate response text
        response_text = await nlp_service.get_response_text(action, parameters)
        
        # Broadcast the result to connected clients
        await connection_manager.broadcast_command_result(action, result.dict(), True)
        
        # Send chat response
        await connection_manager.send_chat_message(response_text, "assistant")
        
        return APIResponse(
            success=True,
            message=response_text,
            data=result.dict()
        )
    except Exception as e:
        await request.app.state.connection_manager.send_chat_message(
            f"Sorry, I couldn't execute that command: {str(e)}", 
            "assistant"
        )
        raise HTTPException(status_code=500, detail=str(e))

async def execute_vehicle_action(nlp_response: NLPResponse, request: Request):
    """Execute the vehicle action based on NLP response"""
    try:
        vehicle_state = request.app.state.vehicle_state
        connection_manager = request.app.state.connection_manager
        
        # Execute the action
        result = await vehicle_state.process_nlp_action(
            nlp_response.action, 
            nlp_response.parameters
        )
        
        # Generate response text
        response_text = await nlp_service.get_response_text(
            nlp_response.action, 
            nlp_response.parameters
        )
        
        # Broadcast updates
        await connection_manager.broadcast_command_result(
            nlp_response.action, 
            result.dict(), 
            True
        )
        
        # Send chat response
        await connection_manager.send_chat_message(response_text, "assistant")
        
    except Exception as e:
        error_message = f"Failed to execute command: {str(e)}"
        await request.app.state.connection_manager.send_chat_message(error_message, "assistant")
        raise e

@router.get("/available-commands")
async def get_available_commands():
    """Get list of available voice commands"""
    return {
        "commands": nlp_service.get_available_commands(),
        "actions": nlp_service.actions,
        "examples": [
            "Turn on the air conditioning",
            "Set temperature to 24 degrees",
            "Play some music",
            "Turn up the volume",
            "Turn on the lights",
            "Heat the seats",
            "Dim the lights a bit"
        ]
    }

@router.post("/chat", response_model=APIResponse)
async def chat_with_assistant(message: str, request: Request):
    """Send a chat message to the voice assistant"""
    try:
        connection_manager = request.app.state.connection_manager
        
        # Broadcast user message
        await connection_manager.send_chat_message(message, "user")
        
        # Process as voice command
        nlp_response = await nlp_service.process_command(message)
        
        if nlp_response.action != "unknown":
            # Execute the command
            await execute_vehicle_action(nlp_response, request)
        else:
            # Send a helpful response for unknown commands
            help_message = "I didn't understand that command. Try saying something like 'turn on climate' or 'play music'."
            await connection_manager.send_chat_message(help_message, "assistant")
        
        return APIResponse(
            success=True,
            message="Message processed",
            data={
                "nlp_response": nlp_response.dict(),
                "executed": nlp_response.action != "unknown"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-nlp")
async def test_nlp_processing(test_phrases: list[str]):
    """Test NLP processing with multiple phrases"""
    results = []
    
    for phrase in test_phrases:
        try:
            response = await nlp_service.process_command(phrase)
            results.append({
                "input": phrase,
                "intent": response.intent,
                "confidence": response.confidence,
                "action": response.action,
                "parameters": response.parameters
            })
        except Exception as e:
            results.append({
                "input": phrase,
                "error": str(e)
            })
    
    return {"test_results": results}