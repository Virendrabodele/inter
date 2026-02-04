 """
 FastAPI Backend for AI Voice Interviewer
 - Handles interview orchestration
 - Integrates with local LLM (Ollama)
 - Manages interview state and scoring
 """
 
 from fastapi import FastAPI, WebSocket, HTTPException
 from fastapi.middleware.cors import CORSMiddleware
 import json
 import asyncio
 from typing import Optional
 import logging
+import os
 
 from interview_manager import InterviewManager
 from llm_engine import LLMEngine
 from audio_processor import AudioProcessor
 from data_storage import DataStorage, GoogleSheetsStorage
 
 # Configure logging
 logging.basicConfig(level=logging.INFO)
 logger = logging.getLogger(__name__)
 
 app = FastAPI(title="AI Voice Interviewer", version="1.0.0")
 
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
 interview_manager = None
 audio_processor = AudioProcessor()
 
 # Initialize data storage
-data_storage = DataStorage(storage_dir="interview_data")
+storage_mode = os.getenv("STORAGE_MODE", "local").lower()
+data_storage = None
+if storage_mode in {"local", "both"}:
+    data_storage = DataStorage(storage_dir="interview_data")
 
 # Initialize Google Sheets (optional - requires credentials)
 google_sheets = None
+google_sheet_name = os.getenv("GOOGLE_SHEETS_NAME", "Interview Data")
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
 async def start_interview(payload: dict):
@@ -75,51 +80,52 @@ async def start_interview(payload: dict):
         "job_description": "string",
         "candidate_name": "string",
         "experience_years": int,
         "difficulty": "beginner|intermediate|advanced"
     }
     """
     global interview_manager
     
     try:
         job_description = payload.get("job_description")
         candidate_name = payload.get("candidate_name", "Candidate")
         experience_years = payload.get("experience_years", 0)
         difficulty = payload.get("difficulty", "intermediate")
         
         if not job_description:
             raise HTTPException(status_code=400, detail="Job description required")
         
         # Create new interview manager
         interview_manager = InterviewManager(
             llm_engine=llm_engine,
             job_description=job_description,
             candidate_name=candidate_name,
             experience_years=experience_years,
             difficulty=difficulty,
             data_storage=data_storage,
-            google_sheets=google_sheets
+            google_sheets=google_sheets,
+            google_sheet_name=google_sheet_name
         )
         
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
 async def submit_answer(payload: dict):
     """
     Submit candidate answer and get next question
     
     Expected payload:
     {
@@ -214,64 +220,79 @@ async def websocket_interview(websocket: WebSocket, session_id: str):
 
 @app.get("/api/health")
 async def health_check():
     """Health check endpoint"""
     return {
         "status": "healthy",
         "llm_ready": llm_engine.is_initialized()
     }
 
 
 @app.get("/api/models")
 async def available_models():
     """Get available LLM models from Ollama"""
     try:
         models = await llm_engine.get_available_models()
         return {"models": models}
     except Exception as e:
         logger.error(f"Error fetching models: {e}")
         raise HTTPException(status_code=500, detail=str(e))
 
 
 @app.get("/api/data/interviews")
 async def get_all_interviews():
     """Get all stored interview sessions"""
     try:
+        if not data_storage:
+            raise HTTPException(
+                status_code=400,
+                detail="Local storage disabled. Set STORAGE_MODE=local or STORAGE_MODE=both to enable."
+            )
         interviews = data_storage.get_all_interviews()
         return {
             "total": len(interviews),
             "interviews": interviews
         }
     except Exception as e:
         logger.error(f"Error fetching interviews: {e}")
         raise HTTPException(status_code=500, detail=str(e))
 
 
 @app.get("/api/data/statistics")
 async def get_statistics():
     """Get statistics about stored interviews"""
     try:
+        if not data_storage:
+            raise HTTPException(
+                status_code=400,
+                detail="Local storage disabled. Set STORAGE_MODE=local or STORAGE_MODE=both to enable."
+            )
         stats = data_storage.get_statistics()
         return stats
     except Exception as e:
         logger.error(f"Error fetching statistics: {e}")
         raise HTTPException(status_code=500, detail=str(e))
 
 
 @app.get("/api/data/interview/{session_id}")
 async def get_interview(session_id: str):
     """Get a specific interview by session ID"""
     try:
+        if not data_storage:
+            raise HTTPException(
+                status_code=400,
+                detail="Local storage disabled. Set STORAGE_MODE=local or STORAGE_MODE=both to enable."
+            )
         interview = data_storage.get_interview_by_id(session_id)
         if not interview:
             raise HTTPException(status_code=404, detail="Interview not found")
         return interview
     except HTTPException:
         raise
     except Exception as e:
         logger.error(f"Error fetching interview: {e}")
         raise HTTPException(status_code=500, detail=str(e))
 
 
 if __name__ == "__main__":
     import uvicorn
     uvicorn.run(app, host="0.0.0.0", port=8000)
 
EOF
)
