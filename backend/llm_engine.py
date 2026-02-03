"""
LLM Engine - Integrates with Google Gemini API
Uses Gemini for interview question generation and evaluation
"""

import google.generativeai as genai
import json
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


class LLMEngine:
    def __init__(self, model: str = "gemini-1.5-flash", api_key: str = None):
        """
        Initialize LLM Engine
        
        Args:
            model: Model name (gemini-1.5-flash, gemini-1.5-pro, etc.)
            api_key: Google Gemini API key (or set GEMINI_API_KEY env var)
        """
        self.model = model
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self._initialized = False
        
        if not self.api_key:
            logger.error("GEMINI_API_KEY not found. Set it as environment variable or pass it to __init__")
            raise ValueError("GEMINI_API_KEY is required")
        
        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(model)
    
    async def initialize(self):
        """Initialize Gemini API"""
        try:
            # Test the connection with a simple API call
            response = self.client.generate_content("Hello")
            self._initialized = True
            logger.info(f"LLM Engine initialized with model: {self.model}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini API: {e}")
            raise
    
    def is_initialized(self) -> bool:
        """Check if LLM is ready"""
        return self._initialized
    
    async def generate_question(
        self,
        job_description: str,
        candidate_profile: dict,
        previous_questions: list = None,
        difficulty: str = "intermediate"
    ) -> str:
        """
        Generate interview question based on job description and candidate profile
        
        Args:
            job_description: The job posting text
            candidate_profile: Dict with candidate info (name, experience, skills, answers)
            previous_questions: List of previously asked questions
            difficulty: beginner|intermediate|advanced
        
        Returns:
            Generated question string
        """
        previous_context = ""
        if previous_questions:
            previous_context = f"\n\nPrevious questions asked:\n" + "\n".join(
                [f"Q{i+1}: {q}" for i, q in enumerate(previous_questions)]
            )
        
        prompt = f"""You are a professional technical interviewer conducting an interview for the following position:

JOB DESCRIPTION:
{job_description}

CANDIDATE PROFILE:
- Name: {candidate_profile.get('name', 'Candidate')}
- Years of Experience: {candidate_profile.get('experience_years', 0)}
- Previous Answers: {json.dumps(candidate_profile.get('answers', []), indent=2)}

{previous_context}

INTERVIEW RULES:
1. Ask ONE clear, specific question
2. Difficulty level: {difficulty}
3. Focus on skills relevant to the job description
4. If candidate answers were weak, probe deeper
5. Keep questions professional and conversational
6. Vary between technical and behavioral questions

Generate the next interview question. Return ONLY the question, nothing else. Be concise but specific."""

        try:
            response = self.client.generate_content(prompt)
            question = response.text.strip()
            
            logger.info(f"Generated question: {question[:100]}...")
            return question
        
        except Exception as e:
            logger.error(f"Error generating question: {e}")
            raise
    
    async def evaluate_answer(
        self,
        question: str,
        answer: str,
        job_description: str,
        difficulty: str = "intermediate"
    ) -> dict:
        """
        Evaluate candidate's answer to interview question
        
        Returns:
            {
                "score": 0-10,
                "evaluation": "text feedback",
                "strengths": ["list"],
                "improvements": ["list"]
            }
        """
        prompt = f"""You are an expert technical interviewer evaluating a candidate's response.

JOB DESCRIPTION:
{job_description}

QUESTION ASKED:
{question}

CANDIDATE ANSWER:
{answer}

DIFFICULTY LEVEL: {difficulty}

Evaluate this answer and provide:
1. A score from 0-10
2. Brief evaluation (2-3 sentences)
3. 2-3 key strengths
4. 2-3 areas for improvement

Return response in JSON format only:
{{
    "score": <number>,
    "evaluation": "<text>",
    "strengths": ["<item>", "<item>"],
    "improvements": ["<item>", "<item>"]
}}"""

        try:
            response = self.client.generate_content(prompt)
            response_text = response.text.strip()
            
            # Extract JSON from response
            try:
                # Find JSON in response
                start = response_text.find("{")
                end = response_text.rfind("}") + 1
                if start >= 0 and end > start:
                    json_str = response_text[start:end]
                    evaluation = json.loads(json_str)
                else:
                    # Fallback if JSON not found
                    evaluation = {
                        "score": 7,
                        "evaluation": response_text,
                        "strengths": ["Good communication"],
                        "improvements": ["More detail needed"]
                    }
            except json.JSONDecodeError:
                evaluation = {
                    "score": 6,
                    "evaluation": response_text,
                    "strengths": ["Attempted answer"],
                    "improvements": ["Could be more detailed"]
                }
            
            return evaluation
        
        except Exception as e:
            logger.error(f"Error evaluating answer: {e}")
            raise
    
    async def generate_final_feedback(
        self,
        job_description: str,
        candidate_profile: dict,
        all_scores: list
    ) -> dict:
        """
        Generate comprehensive final interview feedback
        
        Args:
            job_description: The job posting
            candidate_profile: Candidate info and answers
            all_scores: List of scores from all questions
        
        Returns:
            {
                "overall_score": 0-10,
                "summary": "text",
                "strengths": ["list"],
                "weaknesses": ["list"],
                "recommendations": ["list"]
            }
        """
        average_score = sum(all_scores) / len(all_scores) if all_scores else 0
        
        prompt = f"""You are an expert technical interviewer preparing a final evaluation summary.

JOB DESCRIPTION:
{job_description}

CANDIDATE PROFILE:
- Name: {candidate_profile.get('name')}
- Experience: {candidate_profile.get('experience_years')} years
- Answers Summary: {json.dumps(candidate_profile.get('answers_summary', []), indent=2)}

INTERVIEW SCORES:
{all_scores}
Average: {average_score:.1f}/10

Generate a professional final interview evaluation in JSON format:
{{
    "overall_score": <rounded average>,
    "summary": "<2-3 sentence professional summary>",
    "strengths": ["<key strength>", "<key strength>"],
    "weaknesses": ["<area to improve>", "<area to improve>"],
    "recommendations": ["<actionable advice>", "<actionable advice>"],
    "hire_recommendation": "strong yes|yes|maybe|no"
}}"""

        try:
            response = self.client.generate_content(prompt)
            response_text = response.text.strip()
            
            # Extract and parse JSON
            try:
                start = response_text.find("{")
                end = response_text.rfind("}") + 1
                if start >= 0 and end > start:
                    json_str = response_text[start:end]
                    feedback = json.loads(json_str)
                else:
                    feedback = {
                        "overall_score": int(average_score),
                        "summary": response_text,
                        "strengths": [],
                        "weaknesses": [],
                        "recommendations": [],
                        "hire_recommendation": "maybe"
                    }
            except json.JSONDecodeError:
                feedback = {
                    "overall_score": int(average_score),
                    "summary": response_text,
                    "strengths": [],
                    "weaknesses": [],
                    "recommendations": [],
                    "hire_recommendation": "maybe"
                }
            
            return feedback
        
        except Exception as e:
            logger.error(f"Error generating final feedback: {e}")
            raise
    
    async def get_available_models(self) -> list:
        """Get list of available Gemini models"""
        return ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
