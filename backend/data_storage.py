"""
Data Storage Module - Persists interview data to JSON and Google Sheets
Stores all job descriptions and candidate responses for future improvements
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class DataStorage:
    def __init__(self, storage_dir: str = "interview_data"):
        """
        Initialize data storage
        
        Args:
            storage_dir: Directory to store interview data files
        """
        self.storage_dir = storage_dir
        self.data_file = os.path.join(storage_dir, "interviews.json")
        self._ensure_storage_dir()
    
    def _ensure_storage_dir(self):
        """Create storage directory if it doesn't exist"""
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
            logger.info(f"Created storage directory: {self.storage_dir}")
    
    def _load_all_interviews(self) -> List[Dict]:
        """Load all stored interviews from JSON file"""
        if not os.path.exists(self.data_file):
            return []
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading interviews: {e}")
            return []
    
    def _save_all_interviews(self, interviews: List[Dict]):
        """Save all interviews to JSON file"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(interviews, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(interviews)} interviews to {self.data_file}")
        except Exception as e:
            logger.error(f"Error saving interviews: {e}")
            raise
    
    def save_interview_session(self, session_data: Dict):
        """
        Save a complete interview session
        
        Args:
            session_data: Dictionary containing all interview data
                - session_id
                - candidate_name
                - job_description
                - questions_asked
                - answers_given
                - scores
                - timestamp
        """
        try:
            # Load existing interviews
            interviews = self._load_all_interviews()
            
            # Add timestamp if not present
            if 'timestamp' not in session_data:
                session_data['timestamp'] = datetime.now().isoformat()
            
            # Append new session
            interviews.append(session_data)
            
            # Save back to file
            self._save_all_interviews(interviews)
            
            logger.info(f"Saved interview session: {session_data.get('session_id')}")
            
        except Exception as e:
            logger.error(f"Error saving interview session: {e}")
            raise
    
    def save_job_description(self, job_description: str, session_id: str):
        """
        Save job description separately for analysis
        
        Args:
            job_description: The job posting text
            session_id: Interview session ID
        """
        try:
            job_data = {
                "session_id": session_id,
                "job_description": job_description,
                "timestamp": datetime.now().isoformat()
            }
            
            job_file = os.path.join(self.storage_dir, "job_descriptions.json")
            
            # Load existing jobs
            if os.path.exists(job_file):
                with open(job_file, 'r', encoding='utf-8') as f:
                    jobs = json.load(f)
            else:
                jobs = []
            
            # Append new job
            jobs.append(job_data)
            
            # Save back
            with open(job_file, 'w', encoding='utf-8') as f:
                json.dump(jobs, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved job description for session: {session_id}")
            
        except Exception as e:
            logger.error(f"Error saving job description: {e}")
    
    def save_answer(self, session_id: str, question: str, answer: str, score: float):
        """
        Save individual answer (called incrementally during interview)
        
        Args:
            session_id: Interview session ID
            question: The question asked
            answer: Candidate's answer
            score: Score for the answer
        """
        try:
            answer_data = {
                "session_id": session_id,
                "question": question,
                "answer": answer,
                "score": score,
                "timestamp": datetime.now().isoformat()
            }
            
            answers_file = os.path.join(self.storage_dir, "answers.json")
            
            # Load existing answers
            if os.path.exists(answers_file):
                with open(answers_file, 'r', encoding='utf-8') as f:
                    answers = json.load(f)
            else:
                answers = []
            
            # Append new answer
            answers.append(answer_data)
            
            # Save back
            with open(answers_file, 'w', encoding='utf-8') as f:
                json.dump(answers, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved answer for session: {session_id}")
            
        except Exception as e:
            logger.error(f"Error saving answer: {e}")
    
    def get_all_interviews(self) -> List[Dict]:
        """Get all stored interviews"""
        return self._load_all_interviews()
    
    def get_interview_by_id(self, session_id: str) -> Optional[Dict]:
        """Get a specific interview by session ID"""
        interviews = self._load_all_interviews()
        for interview in interviews:
            if interview.get('session_id') == session_id:
                return interview
        return None
    
    def get_statistics(self) -> Dict:
        """Get statistics about stored interviews"""
        interviews = self._load_all_interviews()
        
        if not interviews:
            return {
                "total_interviews": 0,
                "average_score": 0,
                "total_questions": 0,
                "total_answers": 0
            }
        
        total_scores = []
        total_questions = 0
        
        for interview in interviews:
            if 'average_score' in interview:
                total_scores.append(interview['average_score'])
            total_questions += len(interview.get('questions_and_answers', []))
        
        return {
            "total_interviews": len(interviews),
            "average_score": sum(total_scores) / len(total_scores) if total_scores else 0,
            "total_questions": total_questions,
            "total_answers": total_questions
        }


class GoogleSheetsStorage:
    """
    Google Sheets integration for exporting interview data
    Requires Google Sheets API credentials
    """
    
    def __init__(self, credentials_file: Optional[str] = None):
        """
        Initialize Google Sheets storage
        
        Args:
            credentials_file: Path to Google service account JSON credentials
        """
        self.credentials_file = credentials_file or os.getenv("GOOGLE_SHEETS_CREDENTIALS")
        self.sheet = None
        self._initialized = False
        
        # Try to initialize if credentials are available
        if self.credentials_file and os.path.exists(self.credentials_file):
            try:
                self._initialize()
            except Exception as e:
                logger.warning(f"Could not initialize Google Sheets: {e}")
    
    def _initialize(self):
        """Initialize Google Sheets API connection"""
        try:
            import gspread
            from google.oauth2.service_account import Credentials
            
            # Define the scope
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Load credentials
            creds = Credentials.from_service_account_file(
                self.credentials_file,
                scopes=scope
            )
            
            # Authorize and connect
            self.client = gspread.authorize(creds)
            self._initialized = True
            
            logger.info("Google Sheets initialized successfully")
            
        except ImportError:
            logger.warning("gspread not installed. Run: pip install gspread google-auth")
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets: {e}")
            raise
    
    def is_initialized(self) -> bool:
        """Check if Google Sheets is ready"""
        return self._initialized
    
    def export_interview(self, interview_data: Dict, sheet_name: str = "Interview Data"):
        """
        Export interview data to Google Sheets
        
        Args:
            interview_data: Complete interview data dictionary
            sheet_name: Name of the Google Sheet to create/update
        """
        if not self._initialized:
            logger.warning("Google Sheets not initialized. Skipping export.")
            return
        
        try:
            import gspread
            
            # Try to open existing sheet or create new one
            try:
                sheet = self.client.open(sheet_name)
            except gspread.exceptions.SpreadsheetNotFound:
                sheet = self.client.create(sheet_name)
                logger.info(f"Created new Google Sheet: {sheet_name}")
            
            # Get or create worksheet
            try:
                worksheet = sheet.worksheet("Interviews")
            except gspread.exceptions.WorksheetNotFound:
                worksheet = sheet.add_worksheet(title="Interviews", rows=1000, cols=20)
            
            # Prepare data for export
            headers = [
                "Session ID", "Timestamp", "Candidate Name", "Experience Years",
                "Average Score", "Job Description", "Questions", "Answers", "Scores"
            ]
            
            # Check if headers exist, if not add them
            if worksheet.row_count == 0 or not worksheet.row_values(1):
                worksheet.append_row(headers)
            
            # Prepare row data
            # Note: Job descriptions are truncated to 500 chars for Google Sheets
            # to avoid cell size limits and improve readability. Full descriptions
            # are still available in the local JSON storage.
            row = [
                interview_data.get('session_id', ''),
                interview_data.get('timestamp', datetime.now().isoformat()),
                interview_data.get('candidate_name', ''),
                str(interview_data.get('candidate_experience', 0)),
                str(interview_data.get('average_score', 0)),
                interview_data.get('job_description', '')[:500],  # Truncate long descriptions
                json.dumps([qa['question'] for qa in interview_data.get('questions_and_answers', [])]),
                json.dumps([qa['answer'] for qa in interview_data.get('questions_and_answers', [])]),
                json.dumps(interview_data.get('individual_scores', []))
            ]
            
            # Append row
            worksheet.append_row(row)
            
            logger.info(f"Exported interview {interview_data.get('session_id')} to Google Sheets")
            
        except Exception as e:
            logger.error(f"Error exporting to Google Sheets: {e}")
    
    def export_all_interviews(self, interviews: List[Dict], sheet_name: str = "Interview Data"):
        """
        Export all interviews to Google Sheets
        
        Args:
            interviews: List of interview data dictionaries
            sheet_name: Name of the Google Sheet
        """
        for interview in interviews:
            self.export_interview(interview, sheet_name)
