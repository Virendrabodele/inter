# Data Persistence Usage Examples

This document provides examples of how the data persistence features work in the AI Voice Interviewer.

## Overview

The application now automatically saves:
1. **Job Descriptions** - All job postings submitted
2. **Interview Sessions** - Complete interview data including questions, answers, and scores
3. **Individual Answers** - Each answer with its score (saved incrementally)

## Automatic Data Saving

### During Interview Start

When a candidate starts an interview, the system automatically:
1. Saves the job description to `backend/interview_data/job_descriptions.json`
2. Creates a unique session ID

```python
# This happens automatically when you POST to /api/start-interview
{
  "job_description": "Senior Python Developer with 5+ years experience...",
  "candidate_name": "John Doe",
  "experience_years": 5,
  "difficulty": "intermediate"
}
```

### During Each Answer

After each answer is evaluated, the system automatically:
1. Saves the answer to `backend/interview_data/answers.json`
2. Includes the question, answer, score, and timestamp

```python
# This happens automatically when you POST to /api/submit-answer
{
  "session_id": "a1b2c3d4",
  "answer": "I have extensive experience with Python..."
}
```

### After Interview Completion

When the interview ends, the system automatically:
1. Generates a complete report
2. Saves the full interview session to `backend/interview_data/interviews.json`
3. Exports to Google Sheets (if configured)

## Accessing Stored Data

### 1. Via API Endpoints

#### Get All Interviews
```bash
curl http://localhost:8000/api/data/interviews
```

Response:
```json
{
  "total": 5,
  "interviews": [
    {
      "session_id": "a1b2c3d4",
      "candidate_name": "John Doe",
      "average_score": 7.8,
      "timestamp": "2024-01-15T10:30:00",
      ...
    }
  ]
}
```

#### Get Statistics
```bash
curl http://localhost:8000/api/data/statistics
```

Response:
```json
{
  "total_interviews": 5,
  "average_score": 7.4,
  "total_questions": 25,
  "total_answers": 25
}
```

#### Get Specific Interview
```bash
curl http://localhost:8000/api/data/interview/a1b2c3d4
```

Response:
```json
{
  "session_id": "a1b2c3d4",
  "candidate_name": "John Doe",
  "candidate_experience": 5,
  "job_description": "Senior Python Developer...",
  "average_score": 7.8,
  "questions_and_answers": [
    {
      "question_number": 1,
      "question": "Describe your experience with Python",
      "answer": "I have 5 years of experience...",
      "score": 8,
      "feedback": {
        "strengths": ["Clear communication", "Relevant examples"],
        "improvements": ["Could mention specific projects"]
      }
    }
  ],
  "summary": "Strong candidate with good technical skills...",
  "strengths": ["Python expertise", "Problem-solving"],
  "weaknesses": ["Limited experience with cloud platforms"],
  "recommendations": ["Study AWS/Azure", "Practice system design"],
  "hire_recommendation": "yes"
}
```

### 2. Via Direct File Access

All data is stored in JSON format in `backend/interview_data/`:

```python
import json

# Load all interviews
with open('backend/interview_data/interviews.json', 'r') as f:
    interviews = json.load(f)
    
# Process the data
for interview in interviews:
    print(f"Candidate: {interview['candidate_name']}")
    print(f"Score: {interview['average_score']}")
    print(f"Recommendation: {interview['hire_recommendation']}")
    print("---")
```

## Data Analysis Examples

### Example 1: Find Top Performers

```python
import json

with open('backend/interview_data/interviews.json', 'r') as f:
    interviews = json.load(f)

# Sort by score
top_candidates = sorted(
    interviews, 
    key=lambda x: x['average_score'], 
    reverse=True
)[:5]

print("Top 5 Candidates:")
for candidate in top_candidates:
    print(f"{candidate['candidate_name']}: {candidate['average_score']}/10")
```

### Example 2: Analyze by Experience Level

```python
import json
from collections import defaultdict

with open('backend/interview_data/interviews.json', 'r') as f:
    interviews = json.load(f)

# Group by experience
by_experience = defaultdict(list)
for interview in interviews:
    exp = interview['candidate_experience']
    by_experience[exp].append(interview['average_score'])

# Calculate averages
for exp_years, scores in sorted(by_experience.items()):
    avg = sum(scores) / len(scores)
    print(f"{exp_years} years exp: {avg:.2f} avg score ({len(scores)} candidates)")
```

### Example 3: Most Common Weaknesses

```python
import json
from collections import Counter

with open('backend/interview_data/interviews.json', 'r') as f:
    interviews = json.load(f)

# Collect all weaknesses
all_weaknesses = []
for interview in interviews:
    all_weaknesses.extend(interview.get('weaknesses', []))

# Count occurrences
weakness_counts = Counter(all_weaknesses)
print("Top 5 Common Weaknesses:")
for weakness, count in weakness_counts.most_common(5):
    print(f"- {weakness}: {count} times")
```

### Example 4: Question Effectiveness

```python
import json
from collections import defaultdict

with open('backend/interview_data/answers.json', 'r') as f:
    answers = json.load(f)

# Group scores by question
question_scores = defaultdict(list)
for answer in answers:
    question_scores[answer['question']].append(answer['score'])

# Calculate average score per question
print("Question Effectiveness (sorted by avg score):")
for question, scores in sorted(
    question_scores.items(),
    key=lambda x: sum(x[1])/len(x[1]),
    reverse=True
):
    avg = sum(scores) / len(scores)
    print(f"{avg:.1f}: {question[:60]}...")
```

## Google Sheets Export

### Automatic Export

If Google Sheets is configured, every completed interview is automatically exported.

### Manual Export

You can also manually export all stored interviews:

```python
from data_storage import DataStorage, GoogleSheetsStorage

# Initialize storage
storage = DataStorage()
sheets = GoogleSheetsStorage(credentials_file='google_sheets_credentials.json')

# Get all interviews
interviews = storage.get_all_interviews()

# Export to Google Sheets
sheets.export_all_interviews(interviews, sheet_name="Interview Data")
```

## Data Structure Reference

### Interview Session Object

```json
{
  "session_id": "string (8 chars)",
  "timestamp": "ISO 8601 datetime",
  "candidate_name": "string",
  "candidate_experience": "number (years)",
  "job_description": "string (full text)",
  "difficulty": "beginner|intermediate|advanced",
  "started_at": "ISO 8601 datetime",
  "ended_at": "ISO 8601 datetime",
  "total_questions": "number",
  "average_score": "number (0-10)",
  "individual_scores": ["array of numbers"],
  "questions_and_answers": [
    {
      "question_number": "number",
      "question": "string",
      "answer": "string",
      "score": "number (0-10)",
      "feedback": {
        "strengths": ["array of strings"],
        "improvements": ["array of strings"]
      }
    }
  ],
  "overall_score": "number (0-10)",
  "summary": "string (overall summary)",
  "strengths": ["array of strings"],
  "weaknesses": ["array of strings"],
  "recommendations": ["array of strings"],
  "hire_recommendation": "strong yes|yes|maybe|no"
}
```

## Benefits for Bot Improvement

### 1. Question Quality Analysis
- Identify which questions get high-quality answers
- Remove questions that confuse candidates
- Add questions that reveal important skills

### 2. Scoring Calibration
- Compare AI scores with human evaluations
- Adjust scoring prompts for better accuracy
- Identify patterns in over/under-scoring

### 3. Job Description Patterns
- Analyze which job descriptions lead to better interviews
- Identify key skills that matter most
- Generate better questions based on successful patterns

### 4. Candidate Insights
- Understand common strengths and gaps
- Adjust difficulty levels appropriately
- Create targeted improvement recommendations

### 5. Training Data
- Build a dataset for fine-tuning LLMs
- Improve question generation algorithms
- Create a knowledge base of interview best practices

## Best Practices

1. **Regular Backups**: Periodically backup the `interview_data` directory
2. **Privacy**: Don't commit interview data to public repositories
3. **Analysis**: Review data monthly to identify improvement opportunities
4. **Feedback Loop**: Use insights to update prompts and questions
5. **Documentation**: Keep notes on changes made based on data analysis

## Troubleshooting

### Data Not Saving

Check:
1. Directory permissions - ensure `backend/interview_data/` is writable
2. Disk space - ensure sufficient storage available
3. Backend logs - look for error messages

### Google Sheets Not Working

Check:
1. Credentials file exists and is valid
2. Service account has access to the sheet
3. Google Sheets API is enabled
4. Backend logs for specific error messages

### Data Format Issues

If JSON files are corrupted:
1. Check for syntax errors using a JSON validator
2. Restore from backup if available
3. The application will create fresh files if they're missing

## Next Steps

- Set up monitoring for interview statistics
- Create dashboards using the stored data
- Build automated reports
- Use data to continuously improve the bot
- Share insights with your team via Google Sheets
