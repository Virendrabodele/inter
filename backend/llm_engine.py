"""
LLM Engine - Integrates with Google Gemini API
Uses Gemini for interview question generation and evaluation
"""

import google.generativeai as genai
import json
import logging
import os
import asyncio
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class LLMEngine:
    def __init__(self, model: str = "gemini-1.5-flash", api_key: Optional[str] = None):
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
            logger.error("GEMINI_API_KEY not found.")
            raise ValueError("GEMINI_API_KEY is required")

        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(model)

    async def initialize(self):
        """Initialize Gemini API"""
        try:
            response = await asyncio.to_thread(self.client.generate_content, "Hello")
            self._initialized = True
            logger.info(f"LLM Engine initialized with model: {self.model}")
            return response.text
        except Exception as e:
            logger.error(f"Failed to initialize Gemini API: {e}")
            raise

    def is_initialized(self) -> bool:
        return self._initialized

    async def generate_question(
        self,
        job_description: str,
        candidate_profile: Dict,
        previous_questions: List[str] = None,
        difficulty: str = "intermediate"
    ) -> str:
        """Generate interview question"""

        previous_context = ""
        if previous_questions:
            previous_context = "PREVIOUS QUESTIONS:\n" + "\n".join(previous_questions)

        prompt = f"""You are a professional technical interviewer conducting an interview for the following position:

JOB DESCRIPTION:
{job_description}

CANDIDATE PROFILE:
 Name: {candidate_profile.get('name', 'Candidate')}
 Years of Experience: {candidate_profile.get('experience_years', 0)}
 Previous Answers: {json.dumps(candidate_profile.get('answers', []), indent=2)}

{previous_context}

INTERVIEW RULES:
1. Ask ONE clear, specific question
2. Difficulty level: {difficulty}
3. Focus on skills relevant to the job description
4. If candidate answers were weak, probe deeper
5. Keep questions professional and conversational
6. Vary between technical and behavioral questions

Generate the next interview question. Return ONLY the question, nothing else.
"""

        try:
            response = await asyncio.to_thread(self.client.generate_content, prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error generating question: {e}")
            raise

    async def evaluate_answer(
        self,
        question: str,
        answer: str,
        job_description: str,
        difficulty: str = "intermediate"
    ) -> Dict:
        """Evaluate candidate's answer"""

        prompt = f"""You are a technical interviewer evaluating a candidate's answer.

JOB DESCRIPTION:
{job_description}

QUESTION ASKED:
{question}

CANDIDATE ANSWER:
{answer}

DIFFICULTY LEVEL: {difficulty}

Evaluate this answer using the following structured rubric:

1. **Communication** (0-10): Clarity, structure, and articulation
2. **Technical Accuracy** (0-10): Correctness and depth of technical knowledge
3. **Completeness** (0-10): How thoroughly the question was addressed

Provide:
1. An overall score from 0-10 (average of rubric scores)
2. Individual rubric scores for communication, technical_accuracy, and completeness
3. Brief evaluation (2-3 sentences)
4. 2-3 key strengths
5. 2-3 areas for improvement
6. The difficulty level of the question

Return response in JSON format only:
{{
  "score": 0,
  "rubric": {{
    "communication": 0,
    "technical_accuracy": 0,
    "completeness": 0
  }},
  "evaluation": "",
  "strengths": [],
  "improvements": [],
  "question_difficulty": "{difficulty}"
}}
"""

        try:
            response = await asyncio.to_thread(self.client.generate_content, prompt)
            response_text = response.text.strip()

            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            if start >= 0 and end > start:
                result = json.loads(response_text[start:end])
                # Ensure question_difficulty is present
                if "question_difficulty" not in result:
                    result["question_difficulty"] = difficulty
                # Ensure rubric is present
                if "rubric" not in result:
                    result["rubric"] = {
                        "communication": result.get("score", 6),
                        "technical_accuracy": result.get("score", 6),
                        "completeness": result.get("score", 6)
                    }
                return result
            else:
                return {
                    "score": 6,
                    "rubric": {
                        "communication": 6,
                        "technical_accuracy": 6,
                        "completeness": 6
                    },
                    "evaluation": response_text,
                    "strengths": ["Attempted answer"],
                    "improvements": ["Needs more clarity"],
                    "question_difficulty": difficulty
                }

        except Exception as e:
            logger.error(f"Error evaluating answer: {e}")
            raise

    async def final_feedback(
        self,
        job_description: str,
        candidate_profile: Dict,
        all_scores: List[int]
    ) -> Dict:
        """Generate final interview feedback"""

        average_score = sum(all_scores) / max(len(all_scores), 1)

        prompt = f"""You are an expert technical interviewer preparing a final evaluation summary.

JOB DESCRIPTION:
{job_description}

CANDIDATE PROFILE:
 Name: {candidate_profile.get('name')}
 Experience: {candidate_profile.get('experience_years')} years
 Answers Summary: {json.dumps(candidate_profile.get('answers_summary', []), indent=2)}

INTERVIEW SCORES:
{all_scores}
Average: {average_score:.1f}/10

Generate a professional final interview evaluation in JSON format:
{{
  "overall_score": 0,
  "summary": "",
  "strengths": [],
  "weaknesses": [],
  "recommendations": [],
  "hire_recommendation": "strong yes|yes|maybe|no"
}}
"""

        try:
            response = await asyncio.to_thread(self.client.generate_content, prompt)
            response_text = response.text.strip()

            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(response_text[start:end])
            else:
                return {
                    "overall_score": round(average_score),
                    "summary": response_text,
                    "strengths": [],
                    "weaknesses": [],
                    "recommendations": [],
                    "hire_recommendation": "maybe"
                }

        except Exception as e:
            logger.error(f"Error generating final feedback: {e}")
            raise
