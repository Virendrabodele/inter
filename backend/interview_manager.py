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
        google_sheets: Optional[GoogleSheetsStorage] = None
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
                "experience_years": self.experience_years,
                "answers": []
            }
            
            question = await self.llm_engine.generate_question(
                job_description=self.job_description,
                candidate_profile=candidate_profile,
                previous_questions=[],
                difficulty=self.difficulty
            )
            
            self.current_question_number = 1
            self.questions_asked.append(question)
            self.interview_started = True
            self.started_at = datetime.now()
            
            logger.info(f"Interview {self.session_id} started. Question 1: {question[:80]}...")
            
            return question
        
        except Exception as e:
            logger.error(f"Error generating first question: {e}")
            raise
    
    async def process_answer(self, answer: str) -> dict:
        """
        Process candidate's answer and generate next question or end interview
        
        Args:
            answer: Candidate's answer text
        
        Returns:
            {
                "status": "next_question|interview_complete",
                "evaluation": {...},  # if status is next_question
                "question": "next question text",
                "question_number": int,
                "report": {...}  # if status is interview_complete
            }
        """
        try:
            if not self.interview_started:
                raise ValueError("Interview not started")
            
            if self.interview_ended:
                raise ValueError("Interview already ended")
            
            # Store answer
            self.answers_given.append(answer)
            
            # Evaluate answer
            current_question = self.questions_asked[self.current_question_number - 1]
            
            evaluation = await self.llm_engine.evaluate_answer(
                question=current_question,
                answer=answer,
                job_description=self.job_description,
                difficulty=self.difficulty
            )
            
            self.evaluations.append(evaluation)
            score = evaluation.get("score", 5)
            self.scores.append(score)
            
            logger.info(
                f"Answer {self.current_question_number} evaluated. "
                f"Score: {score}/10"
            )
            
            # Save answer to storage
            if self.data_storage:
                try:
                    self.data_storage.save_answer(
                        self.session_id,
                        current_question,
                        answer,
                        score
                    )
                except Exception as e:
                    logger.error(f"Error saving answer: {e}")
            
            # Check if interview should continue
            if self.current_question_number >= self.total_questions:
                # Interview ends
                self.interview_ended = True
                self.ended_at = datetime.now()
                
                # Generate final report
                final_report = await self._generate_final_report()
                
                return {
                    "status": "interview_complete",
                    "evaluation": evaluation,
                    "report": final_report
                }
            
            else:
                # Generate next question
                self.current_question_number += 1
                
                candidate_profile = {
                    "name": self.candidate_name,
                    "experience_years": self.experience_years,
                    "answers": self.answers_given,
                    "scores": self.scores
                }
                
                next_question = await self.llm_engine.generate_question(
                    job_description=self.job_description,
                    candidate_profile=candidate_profile,
                    previous_questions=self.questions_asked,
                    difficulty=self.difficulty
                )
                
                self.questions_asked.append(next_question)
                
                logger.info(
                    f"Question {self.current_question_number} generated. "
                    f"Progress: {self.current_question_number}/{self.total_questions}"
                )
                
                return {
                    "status": "next_question",
                    "evaluation": evaluation,
                    "question": next_question,
                    "question_number": self.current_question_number,
                    "total_questions": self.total_questions,
                    "progress": self.current_question_number / self.total_questions
                }
        
        except Exception as e:
            logger.error(f"Error processing answer: {e}")
            raise
    
    async def _generate_final_report(self) -> dict:
        """Generate comprehensive final interview report"""
        try:
            # Prepare candidate profile summary
            answers_summary = [
                {
                    "question": self.questions_asked[i],
                    "answer": self.answers_given[i],
                    "score": self.scores[i]
                }
                for i in range(len(self.questions_asked))
            ]
            
            candidate_profile = {
                "name": self.candidate_name,
                "experience_years": self.experience_years,
                "answers_summary": answers_summary
            }
            
            # Get final feedback from LLM
            final_feedback = await self.llm_engine.generate_final_feedback(
                job_description=self.job_description,
                candidate_profile=candidate_profile,
                all_scores=self.scores
            )
            
            # Build comprehensive report
            report = {
                "session_id": self.session_id,
                "candidate_name": self.candidate_name,
                "candidate_experience": self.experience_years,
                "job_description": self.job_description,
                "difficulty": self.difficulty,
                "started_at": self.started_at.isoformat() if self.started_at else None,
                "ended_at": self.ended_at.isoformat() if self.ended_at else None,
                "total_questions": len(self.questions_asked),
                "average_score": sum(self.scores) / len(self.scores) if self.scores else 0,
                "individual_scores": self.scores,
                "questions_and_answers": [
                    {
                        "question_number": i + 1,
                        "question": self.questions_asked[i],
                        "answer": self.answers_given[i],
                        "score": self.scores[i],
                        "feedback": {
                            "strengths": self.evaluations[i].get("strengths", []),
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
                    self.google_sheets.export_interview(report)
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
            "questions_asked": len(self.questions_asked),
            "answers_given": len(self.answers_given),
            "average_score": sum(self.scores) / len(self.scores) if self.scores else 0,
            "progress": self.current_question_number / self.total_questions
        }
