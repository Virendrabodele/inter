# 🎙️ AI Voice Interviewer

A cutting-edge, **voice-based AI interview platform** that simulates real human interviews using Google Gemini AI and browser speech APIs. 

**Powered by Google Gemini. Browser-based speech recognition. Fully customizable.**

---

## ✨ What It Does

```
📝 User pastes job description
     ↓
🤖 AI generates first question
     ↓
🗣️ AI speaks question aloud
     ↓
🎤 Candidate speaks answer
     ↓
📊 AI evaluates answer (0-10 score)
     ↓
🔄 Repeat for 5 questions
     ↓
📈 Generate comprehensive final report
```

---

## 🎯 Key Features

✅ **Voice-Only Interview**: No typing—pure voice interaction  
✅ **Real-time Transcription**: Browser Web Speech API (free)  
✅ **Intelligent Questions**: AI generates questions dynamically based on candidate answers  
✅ **Scoring & Feedback**: Automatic evaluation with detailed rubric (communication, technical accuracy, completeness)  
✅ **Job-Specific**: Tailors questions to actual job description  
✅ **Google Gemini AI**: Powered by Google's advanced Gemini models  
✅ **Beautiful UI**: Modern, responsive design with animations  
✅ **Comprehensive Reports**: Final score, strengths, weaknesses, recommendations  
✅ **Data Persistence**: Automatically saves all interviews and responses  
✅ **Google Sheets Export**: Optional export to Google Sheets for analysis  

---

## 🚀 Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| Backend | FastAPI (Python) | Fast, async, easy to extend |
| LLM | Google Gemini | Advanced AI, reliable, scalable |
| Frontend | React 18 | Modern, responsive, interactive |
| Speech Recognition | Web Speech API | Browser-native, no APIs needed |
| Speech Synthesis | Web Speech API | Browser-native text-to-speech |
| Styling | CSS3 + Animations | Beautiful, modern UI |

---

## 📋 Prerequisites

Before starting, install:

1. **Python 3.9+**: [python.org](https://python.org)
2. **Node.js 16+**: [nodejs.org](https://nodejs.org)
3. **Google Gemini API Key**: Get free API key from [ai.google.dev](https://ai.google.dev)

Check installations:
```bash
python --version    # Python 3.9+
node --version      # Node 16+
```

---

## ⚡ Quick Start (5 minutes)

### Step 1: Get Gemini API Key
1. Visit [Google AI Studio](https://ai.google.dev)
2. Click "Get API Key"
3. Create a new API key
4. Copy the key for later use

### Step 2: Setup Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set environment variable for Gemini API key
export GEMINI_API_KEY="your-api-key-here"  # On Windows: set GEMINI_API_KEY=your-api-key-here

python app.py               # Runs on http://localhost:8000
```

### Step 3: Setup Frontend
```bash
# In new terminal
cd frontend
npm install
npm run dev                  # Runs on http://localhost:5173
```

### Step 4: Open Application
Open browser to: **http://localhost:5173**

---

## 📖 Usage

1. **Enter Setup Info**
   - Your name
   - Years of experience
   - Interview difficulty
   - Job description (paste from job posting)

2. **Interview Process**
   - AI asks first question (spoken aloud)
   - Press "Start Recording"
   - Speak your answer clearly
   - Press "Submit Answer"
   - Repeat for next question

3. **View Results**
   - Get final score (0-10)
   - See strengths and weaknesses
   - Read recommendations
   - View question-by-question breakdown

---

## 🎨 UI Features

### Setup Stage
- Clean form for interview configuration
- Job description editor
- Difficulty level selector

### Interview Stage
- Real-time question display
- Voice recording indicator
- Live transcription preview
- Answer playback (hear what you said)
- Progress bar

### Results Stage
- Overall score with recommendation
- Summary analysis
- Strengths highlight
- Improvement areas
- Individual question scores
- Export-ready report

---

## 📁 Project Structure

```
ai_voice_interviewer/
├── backend/                    # FastAPI Backend
│   ├── app.py                 # Main API server
│   ├── interview_manager.py   # Interview orchestration
│   ├── llm_engine.py         # LLM integration
│   ├── audio_processor.py    # Audio utilities
│   └── requirements.txt       # Python dependencies
│
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── App.jsx           # Main component
│   │   ├── App.css           # Styling
│   │   └── main.jsx          # Entry point
│   ├── public/
│   ├── package.json          # Node dependencies
│   ├── vite.config.js        # Vite config
│   └── index.html            # HTML template
│
├── SETUP.md                    # Detailed setup guide
└── README.md                   # This file
```

---

## 🔧 Configuration

## 🔧 Configuration

### Environment Variables

**Backend** (`backend/.env` or export):
```bash
GEMINI_API_KEY=your-api-key-here          # Required: Google Gemini API key
STORAGE_MODE=local                         # Optional: local|sheets|both (default: local)
GOOGLE_SHEETS_NAME=Interview Data          # Optional: Google Sheets name
GOOGLE_SHEETS_CREDENTIALS=path/to/creds.json  # Optional: For Google Sheets integration
```

**Frontend** (`frontend/.env`):
```bash
VITE_API_BASE_URL=http://localhost:8000   # Optional: Backend API URL (default: http://localhost:8000)
```

### Change LLM Model
**File**: `backend/app.py`
```python
llm_engine = LLMEngine(model="gemini-1.5-flash")  # or "gemini-1.5-pro" for better quality
```

### Change Number of Questions
**File**: `backend/interview_manager.py`
```python
self.total_questions = 5  # Change to desired number
```

### Customize Interview Prompts
**File**: `backend/llm_engine.py`  
Edit the `prompt` variables in `generate_question()` and `evaluate_answer()` methods

---

## 🎯 API Reference

### Start Interview
```
POST /api/start-interview
{
  "job_description": "...",
  "candidate_name": "John",
  "experience_years": 5,
  "difficulty": "intermediate"
}
```

### Submit Answer
```
POST /api/submit-answer
{
  "session_id": "abc123",
  "answer": "My answer text..."
}
```

### End Interview
```
POST /api/end-interview
{
  "session_id": "abc123"
}
```

### Health Check
```
GET /api/health
```

---

## 🐛 Troubleshooting

### Gemini API Key Issues
```bash
# Check if API key is set
echo $GEMINI_API_KEY  # Should show your key

# Set it if missing
export GEMINI_API_KEY="your-api-key-here"

# Verify key works
curl -H "x-goog-api-key: $GEMINI_API_KEY" \
  "https://generativelanguage.googleapis.com/v1/models"
```

### Backend Won't Start
- Ensure `GEMINI_API_KEY` environment variable is set
- Check Python dependencies: `pip install -r requirements.txt`
- Verify Python version: `python --version` (should be 3.9+)

### Microphone Not Working
- Check browser permissions (allow microphone)
- Try Chrome/Firefox/Safari
- Verify system audio settings

### CORS Errors
Check `backend/app.py` - update allowed origins if running on different ports

### Frontend Won't Start
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

---

## 🌐 Deployment

### Deploy Backend
```bash
# Option 1: Railway.app
railway add
railway up

# Option 2: Heroku
heroku create
git push heroku main

# Option 3: Docker
docker build -t interviewer-backend .
docker run -p 8000:8000 interviewer-backend
```

### Deploy Frontend
```bash
# Option 1: Vercel
npm install -g vercel
vercel

# Option 2: Netlify
npm run build
# Deploy dist/ folder to Netlify

# Option 3: GitHub Pages
npm run build
# Deploy dist/ folder to GitHub Pages
```

---

## 📊 Data Persistence & Analytics

The application now automatically stores all interview data for future improvements:

### Automatic Local Storage
All interviews are saved to `backend/interview_data/`:
- **interviews.json**: Complete interview sessions with scores and feedback
- **job_descriptions.json**: All job descriptions submitted
- **answers.json**: Individual Q&A pairs with scores

### Google Sheets Integration (Optional)
Export interview data automatically to Google Sheets for:
- Team collaboration and review
- Easy data analysis and visualization
- Building a knowledge base of interviews
- Tracking candidate performance over time

**Setup Guide**: See [GOOGLE_SHEETS_SETUP.md](./GOOGLE_SHEETS_SETUP.md) for detailed instructions

### API Endpoints for Data Access
```bash
# Get all stored interviews
GET /api/data/interviews

# Get interview statistics
GET /api/data/statistics

# Get specific interview by ID
GET /api/data/interview/{session_id}
```

### Using Data to Improve the Bot
- Analyze which questions work best
- Fine-tune scoring algorithms
- Identify patterns in successful candidates
- Build training datasets for future AI improvements
- Generate better questions based on historical data

---

## 🔒 Privacy & Security

✅ **Google Gemini API**: Secure cloud-based LLM processing  
✅ **Persistent storage**: Interview data saved locally for analysis  
✅ **Browser-based speech**: Speech recognition happens in browser  
✅ **Optional export**: Google Sheets integration is optional  
✅ **No tracking**: No analytics or telemetry  
⚠️ **Secure your API key**: Keep your Gemini API key and credentials secure  

---

## 📊 Performance

| Metric | Value |
|--------|-------|
| First question generation | ~2-4 seconds |
| Answer evaluation | ~1-3 seconds |
| Speech recognition latency | ~1 second |
| Text-to-speech latency | ~500ms |
| Total Q→A→Q cycle | ~6-10 seconds |

*Times vary based on LLM model and system specs*

---

## 🚀 Future Roadmap

- [x] Interview data persistence (JSON storage)
- [x] Google Sheets integration for data export
- [ ] Video recording (camera + facial expressions)
- [ ] Emotion/sentiment analysis
- [ ] Resume upload & parsing
- [ ] Multiple languages
- [ ] Interview history & analytics dashboard
- [ ] HR dashboard
- [ ] PDF report export
- [ ] Interview templates library
- [ ] Real-time feedback during answer
- [ ] Mobile app (native)

---

## 🤝 Contributing

Contributions welcome! Areas to improve:

1. **Better prompts** for question generation
2. **Additional LLM support** (GPT, Anthropic, etc.)
3. **Enhanced UI/UX** features
4. **Performance optimizations**
5. **Additional languages**
6. **Database integration** for history ✅ (Completed - JSON + Google Sheets)
7. **Data analytics** and visualization dashboards

---

## 📝 License

MIT - Use freely for personal or commercial projects

---

## 💡 Tips for Best Results

1. **Clear Job Description**: Copy-paste full job posting (title, description, requirements)
2. **Appropriate Difficulty**: Match difficulty to candidate experience
3. **Quiet Environment**: Minimize background noise for better speech recognition
4. **Clear Speech**: Speak clearly at normal pace
5. **Full Answers**: Longer answers allow better evaluation
6. **Multiple Takes**: Run multiple interviews to test different candidates

---

## 📞 Support

- 📖 See [SETUP.md](./SETUP.md) for detailed setup guide
- 🐛 Check troubleshooting section above
- 💬 Review backend logs for errors
- 🔍 Check browser console (F12) for frontend errors

---

## 🎓 Learn More

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev)
- [Ollama Documentation](https://github.com/ollama/ollama)
- [Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)

---

**Built with ❤️ using FastAPI, React, and local LLMs**

*Transform your hiring process with AI-powered voice interviews. Fast, fair, and free.*
