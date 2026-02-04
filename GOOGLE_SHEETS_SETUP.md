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
 - Candidate name and experience
 - Complete job descriptions
 - All interview questions asked
 - All candidate responses
 - Individual question scores
 - Final interview scores and evaluations
 - Timestamps for each interview
 
 ## Google Sheets Integration (Optional)
 
+If you want to store interview data in Google Sheets without local JSON files,
+set `STORAGE_MODE=sheets`. To keep both local JSON and Google Sheets exports,
+use `STORAGE_MODE=both`.
+
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
+STORAGE_MODE=both
+GOOGLE_SHEETS_NAME=Interview Data
+```
+
+### Storage Mode Options
+
+- `STORAGE_MODE=local` (default) → save to local JSON only
+- `STORAGE_MODE=sheets` → export to Google Sheets only
+- `STORAGE_MODE=both` → save locally and export to Sheets
+- `STORAGE_MODE=none` → disable all storage
+
+### Customize Sheet Name
+
+Set `GOOGLE_SHEETS_NAME` to control the target sheet name:
+
+```
+GOOGLE_SHEETS_NAME=AI Interview Logs
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
 
 
EOF
)
