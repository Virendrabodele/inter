# Google Sheets Integration Setup Guide

This guide explains how to set up Google Sheets integration to automatically export interview data.

## Overview

The AI Voice Interviewer now includes data persistence features:
- **Local JSON Storage**: All interview data is automatically saved to JSON files in `backend/interview_data/`
- **Google Sheets Export** (Optional): Export interview data to Google Sheets for easy analysis and sharing

## Local Storage (Automatic)

No setup required! Interview data is automatically saved to:
- `backend/interview_data/interviews.json` - Complete interview sessions
- `backend/interview_data/job_descriptions.json` - All job descriptions
- `backend/interview_data/answers.json` - Individual answers and scores

### Data Stored:
- Candidate name, age, and experience
- Complete job descriptions
- All interview questions asked
- All candidate responses
- Individual question scores
- Final interview scores and evaluations
- Timestamps for each interview

## Google Sheets Integration (Optional)

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **Google Sheets API** and **Google Drive API**:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Sheets API" and click "Enable"
   - Search for "Google Drive API" and click "Enable"

### Step 2: Create Service Account

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Fill in the service account details:
   - Name: `interview-bot` (or any name)
   - Description: `Service account for AI Interview Bot`
4. Click "Create and Continue"
5. Skip granting permissions (click "Continue")
6. Click "Done"

### Step 3: Generate Service Account Key

1. Click on the newly created service account
2. Go to the "Keys" tab
3. Click "Add Key" > "Create new key"
4. Select "JSON" format
5. Click "Create"
6. A JSON file will be downloaded - **keep this file secure!**

### Step 4: Configure the Application

1. Rename the downloaded JSON file to `google_sheets_credentials.json`
2. Move it to the `backend/` directory
3. Set the environment variable:

```bash
# Linux/Mac
export GOOGLE_SHEETS_CREDENTIALS=/path/to/backend/google_sheets_credentials.json

# Windows
set GOOGLE_SHEETS_CREDENTIALS=C:\path\to\backend\google_sheets_credentials.json
```

Or add to your `.env` file in the backend directory:
```
GOOGLE_SHEETS_CREDENTIALS=./google_sheets_credentials.json
```

### Step 5: Share Google Sheet with Service Account

1. Open the downloaded JSON credentials file
2. Copy the `client_email` value (e.g., `interview-bot@project.iam.gserviceaccount.com`)
3. Create a new Google Sheet or open an existing one
4. Click "Share" and paste the service account email
5. Grant "Editor" permissions
6. Click "Done"

### Step 6: Test the Integration

1. Restart the backend server:
```bash
cd backend
python app.py
```

2. Check the logs for: `Google Sheets integration enabled`
3. Complete an interview
4. Check your Google Sheet - the data should appear automatically!

## Data Format in Google Sheets

The exported data includes:
- Session ID
- Timestamp
- Candidate Name
- Experience Years
- Average Score
- Job Description (truncated to 500 chars)
- Questions (JSON array)
- Answers (JSON array)
- Scores (JSON array)

## Viewing Stored Data

### Via API Endpoints

The application provides several endpoints to view stored data:

1. **Get all interviews:**
```bash
GET http://localhost:8000/api/data/interviews
```

2. **Get statistics:**
```bash
GET http://localhost:8000/api/data/statistics
```

3. **Get specific interview:**
```bash
GET http://localhost:8000/api/data/interview/{session_id}
```

### Via Files

You can directly open the JSON files in the `backend/interview_data/` directory:
- Use any text editor or JSON viewer
- Import into Excel or Google Sheets
- Process with Python scripts for analysis

## Privacy & Security

⚠️ **Important Security Notes:**

1. **Never commit credentials to Git**
   - The `.gitignore` file excludes `*_key.json`, `*-key.json`, and `service_account.json`
   - Always keep credentials secure and private

2. **Interview data privacy**
   - Interview data is stored locally by default
   - The `backend/interview_data/` directory is gitignored by default
   - Remove the gitignore entry if you want to commit interview data

3. **Google Sheets sharing**
   - Only share your Google Sheet with people who should access interview data
   - Consider using separate sheets for different purposes

## Troubleshooting

### "Google Sheets not initialized" message

**Cause**: Credentials file not found or invalid

**Solution**:
1. Verify the credentials file exists in the correct location
2. Check the `GOOGLE_SHEETS_CREDENTIALS` environment variable
3. Ensure the JSON file is valid and not corrupted
4. Restart the backend server after adding credentials

### "Permission denied" error

**Cause**: Service account doesn't have access to the Google Sheet

**Solution**:
1. Share the Google Sheet with the service account email
2. Grant "Editor" permissions
3. Try the export again

### Data not appearing in Google Sheets

**Cause**: Various reasons

**Solution**:
1. Check backend logs for error messages
2. Verify the service account has Editor permissions on the sheet
3. Ensure both Google Sheets API and Google Drive API are enabled
4. Try creating a new sheet and sharing it with the service account

### Import errors (gspread not found)

**Cause**: Dependencies not installed

**Solution**:
```bash
cd backend
pip install -r requirements.txt
```

## Using the Data for Bot Improvement

The stored interview data can be used to:

1. **Analyze Question Quality**
   - Review which questions get better responses
   - Identify confusing or poorly-worded questions

2. **Improve Scoring Accuracy**
   - Compare AI scores with human evaluations
   - Fine-tune the evaluation prompts

3. **Generate Better Questions**
   - Analyze successful interview patterns
   - Create a question bank based on job descriptions

4. **Understand Candidate Patterns**
   - Identify common strengths and weaknesses
   - Adjust difficulty levels appropriately

5. **Train Future Models**
   - Use the dataset to fine-tune LLMs
   - Improve question generation algorithms

## Example: Analyzing Data with Python

```python
import json

# Load interviews
with open('backend/interview_data/interviews.json', 'r') as f:
    interviews = json.load(f)

# Calculate average scores by experience level
from collections import defaultdict
scores_by_exp = defaultdict(list)

for interview in interviews:
    exp = interview['candidate_experience']
    score = interview['average_score']
    scores_by_exp[exp].append(score)

# Print results
for exp, scores in sorted(scores_by_exp.items()):
    avg = sum(scores) / len(scores)
    print(f"{exp} years experience: {avg:.2f} average score")
```

## Support

For issues or questions:
1. Check the backend logs: Look for error messages
2. Review this documentation carefully
3. Ensure all prerequisites are installed
4. Verify Google Cloud API credentials are valid

## Next Steps

Now that data persistence is set up:
1. Conduct multiple interviews to build your dataset
2. Analyze the data to identify patterns
3. Use insights to improve your interview process
4. Export data to Google Sheets for team collaboration
5. Consider building dashboards using the stored data
