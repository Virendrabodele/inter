
 """
 Interview Manager - Orchestrates the interview flow
 Manages questions, answers, scoring, and state
 """
 import uuid
 import json
 import logging
 from typing import List, Dict, Optional
 from datetime import datetime
 from data_storage import DataStorage, GoogleSheetsStorage
 
 logger = logging.getLogger(__name__)
 
 
 class InterviewManager:
     def __init__(
         self,
         llm_engine,
         job_description: str,
         candidate_name: str = "Candidate",
         experience_years: int = 0,
         difficulty: str = "intermediate",
         data_storage: Optional[DataStorage] = None,
-        google_sheets: Optional[GoogleSheetsStorage] = None
+        google_sheets: Optional[GoogleSheetsStorage] = None,
+        google_sheet_name: str = "Interview Data"
     ):
         """
         Initialize interview manager
         
         Args:
             llm_engine: LLMEngine instance
             job_description: Job description text
             candidate_name: Name of candidate
             experience_years: Years of experience
             difficulty: Difficulty level (beginner|intermediate|advanced)
             data_storage: DataStorage instance for persisting interview data
             google_sheets: GoogleSheetsStorage instance for exporting to Google Sheets
         """
         self.llm_engine = llm_engine
         self.session_id = str(uuid.uuid4())[:8]
         self.job_description = job_description
         self.candidate_name = candidate_name
         self.experience_years = experience_years
         self.difficulty = difficulty
         
         # Data persistence
         self.data_storage = data_storage
         self.google_sheets = google_sheets
+        self.google_sheet_name = google_sheet_name
         
         # Interview state
         self.current_question_number = 0
         self.total_questions = 5
         self.questions_asked: List[str] = []
         self.answers_given: List[str] = []
         self.scores: List[float] = []
         self.evaluations: List[Dict] = []
         self.interview_started = False
         self.interview_ended = False
         self.started_at = None
         self.ended_at = None
         
         # Save job description to storage
         if self.data_storage:
             try:
                 self.data_storage.save_job_description(job_description, self.session_id)
             except Exception as e:
                 logger.error(f"Error saving job description: {e}")
     
     async def generate_first_question(self) -> str:
         """Generate the first interview question"""
         try:
             candidate_profile = {
                 "name": self.candidate_name,
@@ -254,51 +256,54 @@ class InterviewManager:
                             "improvements": self.evaluations[i].get("improvements", [])
                         }
                     }
                     for i in range(len(self.questions_asked))
                 ],
                 "timestamp": datetime.now().isoformat(),
                 **final_feedback
             }
             
             logger.info(
                 f"Interview {self.session_id} completed. "
                 f"Final Score: {report['average_score']:.1f}/10, "
                 f"Recommendation: {report.get('hire_recommendation', 'N/A')}"
             )
             
             # Save complete interview session to storage
             if self.data_storage:
                 try:
                     self.data_storage.save_interview_session(report)
                 except Exception as e:
                     logger.error(f"Error saving interview session: {e}")
             
             # Export to Google Sheets if available
             if self.google_sheets and self.google_sheets.is_initialized():
                 try:
-                    self.google_sheets.export_interview(report)
+                    self.google_sheets.export_interview(
+                        report,
+                        sheet_name=self.google_sheet_name
+                    )
                 except Exception as e:
                     logger.error(f"Error exporting to Google Sheets: {e}")
             
             return report
         
         except Exception as e:
             logger.error(f"Error generating final report: {e}")
             raise
     
     async def generate_final_report(self) -> dict:
         """Public method to generate final report"""
         if not self.interview_ended:
             self.interview_ended = True
             self.ended_at = datetime.now()
         
         return await self._generate_final_report()
     
     def get_state(self) -> dict:
         """Get current interview state"""
         return {
             "session_id": self.session_id,
             "interview_started": self.interview_started,
             "interview_ended": self.interview_ended,
             "current_question_number": self.current_question_number,
             "total_questions": self.total_questions,
