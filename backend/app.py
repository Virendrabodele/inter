"""
FastAPI Backend for AI Voice Interviewer
Handles interview orchestration
Integrates with local LLM (Ollama)
Manages interview state and scoring
"""

from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import json
import asyncio
from typing import Optional
import logging
import os

from interview_manager import InterviewManager
from llm_engine import LLMEngine
from audio_processor import AudioProcessor
from data_storage import DataStorage, GoogleSheetsStorage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Voice Interviewer", version="1.0.0")


class StartInterviewPayload(BaseModel):
    job_description: str = Field(..., min_length=1)
    candidate_name: str = "Candidate"
    experience_years: int = Field(0, ge=0)
    difficulty: str = "intermediate"


class SubmitAnswerPayload(BaseModel):
    session_id: str = Field(..., min_length=1)
    answer: str = Field(..., min_length=1)


class EndInterviewPayload(BaseModel):
    session_id: str = Field(..., min_length=1)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
llm_engine = LLMEngine(model="gemini-1.5-flash")  # Using Google Gemini
interview_sessions = {}
audio_processor = AudioProcessor()

# Initialize data storage
storage_mode = os.getenv("STORAGE_MODE", "local").lower()
data_storage = None
if storage_mode in {"local", "both"}:
    data_storage = DataStorage(storage_dir="interview_data")

# Initialize Google Sheets (optional - requires credentials)
google_sheets = None
google_sheet_name = os.getenv("GOOGLE_SHEETS_NAME", "Interview Data")
try:
    google_sheets = GoogleSheetsStorage()
    if google_sheets.is_initialized():
        logger.info("Google Sheets integration enabled")
    else:
        logger.info("Google Sheets integration disabled (credentials not found)")
except Exception as e:
    logger.warning(f"Google Sheets initialization failed: {e}")
    google_sheets = None


@app.on_event("startup")
async def startup_event():
    """Initialize LLM on startup"""
    logger.info("Starting AI Voice Interviewer Backend...")
    try:
        await llm_engine.initialize()
        logger.info("LLM Engine initialized successfully")
    except Exception as e:
        logger.warning(f"LLM initialization failed (will retry on first use): {e}")
    # Don't raise - let the app start and try again when needed


@app.post("/api/start-interview")
async def start_interview(payload: StartInterviewPayload):
    """
    Start a new interview session

    Expected payload:
    {
        "job_description": "string",
        "candidate_name": "string",
        "experience_years": int,
        "difficulty": "beginner|intermediate|advanced"
    }
    """
    try:
        job_description = payload.job_description
        candidate_name = payload.candidate_name
        experience_years = payload.experience_years
        difficulty = payload.difficulty

        # Create new interview manager
        interview_manager = InterviewManager(
            llm_engine=llm_engine,
            job_description=job_description,
            candidate_name=candidate_name,
            experience_years=experience_years,
            difficulty=difficulty,
            data_storage=data_storage,
            google_sheets=google_sheets,
            google_sheet_name=google_sheet_name
        )
        interview_sessions[interview_manager.session_id] = interview_manager

        # Generate first question
        first_question = await interview_manager.generate_first_question()

        return {
            "status": "started",
            "session_id": interview_manager.session_id,
            "question": first_question,
            "question_number": 1,
            "total_questions": 5
        }

    except Exception as e:
        logger.error(f"Error starting interview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/submit-answer")
async def submit_answer(payload: SubmitAnswerPayload):
    """
    Submit candidate answer and get next question

    Expected payload:
    {
        "session_id": "string",
        "answer": "string (transcribed from audio)"
    }
    """
    try:
        interview_manager = interview_sessions.get(payload.session_id)
        if not interview_manager:
            raise HTTPException(status_code=400, detail="No active interview session")

        answer = payload.answer

        # Process answer and generate next question
        result = await interview_manager.process_answer(answer)

        return result

    except Exception as e:
        logger.error(f"Error submitting answer: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/end-interview")
async def end_interview(payload: EndInterviewPayload):
    """
    End interview and get final score/feedback

    Expected payload:
    {
        "session_id": "string"
    }
    """
    try:
        interview_manager = interview_sessions.get(payload.session_id)
        if not interview_manager:
            raise HTTPException(status_code=400, detail="No active interview session")

        # Generate final report
        report = await interview_manager.generate_final_report()

        interview_sessions.pop(payload.session_id, None)

        return {
            "status": "completed",
            "report": report
        }

    except Exception as e:
        logger.error(f"Error ending interview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/interview/{session_id}")
async def websocket_interview(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time interview interaction
    Allows bidirectional communication for audio streaming
    """
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            # Handle different message types
            if message.get("type") == "audio":
                # Process audio stream
                audio_data = message.get("audio")
                # Convert audio to text using speech-to-text
                # For now, just echo back
                pass

            elif message.get("type") == "answer":
                # Handle text answer
                answer = message.get("answer")
                interview_manager = interview_sessions.get(session_id)
                if interview_manager:
                    result = await interview_manager.process_answer(answer)
                    await websocket.send_text(json.dumps(result))

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close(code=1000)


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    # Determine storage status
    storage_status = "local"
    if google_sheets and google_sheets.is_initialized():
        if storage_mode == "both":
            storage_status = "local + sheets"
        elif storage_mode == "sheets":
            storage_status = "sheets only"
    
    return {
        "status": "healthy",
        "llm_ready": llm_engine.is_initialized(),
        "storage_mode": storage_status,
        "sheet_name": google_sheet_name if google_sheets and google_sheets.is_initialized() else None
    }


@app.post("/api/export/{session_id}")
async def export_to_sheets(session_id: str):
    """
    Manually export an interview session to Google Sheets
    
    Args:
        session_id: The session ID to export
    """
    try:
        if not google_sheets or not google_sheets.is_initialized():
            raise HTTPException(
                status_code=503, 
                detail="Google Sheets integration is not enabled"
            )
        
        # Try to get the interview data from active sessions
        interview_manager = interview_sessions.get(session_id)
        if interview_manager:
            # Get current state and export
            state = interview_manager.get_state()
            google_sheets.export_interview(state, google_sheet_name)
            return {
                "status": "success",
                "message": f"Interview exported to '{google_sheet_name}'",
                "session_id": session_id
            }
        
        # If not in active sessions, try to get from data storage
        if data_storage:
            interview_data = data_storage.get_interview_by_id(session_id)
            if interview_data:
                google_sheets.export_interview(interview_data, google_sheet_name)
                return {
                    "status": "success",
                    "message": f"Interview exported to '{google_sheet_name}'",
                    "session_id": session_id
                }
        
        raise HTTPException(status_code=404, detail="Interview session not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting to sheets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/models")
async def available_models():
    """Get available LLM models from Ollama"""
    try:
        models = await llm_engine.get_available_models()
        return {"models": models}
    except Exception as e:
        logger.error(f"Error getting models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

