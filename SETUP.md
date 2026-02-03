# 🎙️ AI Voice Interviewer - Complete Setup Guide

## Project Overview

**What**: A full-stack web application for AI-powered voice-based interviews
**Tech Stack**: 
- Backend: Python FastAPI + Local LLM (Ollama)
- Frontend: React + Web Speech API
- LLM: Mistral or Llama2 (local, free)
- Speech: Browser Web Speech API (free, no API keys needed)

**No costs**: Everything runs locally or uses free browser APIs

---

## 🚀 Quick Start (5 minutes)

### Prerequisites
- Python 3.9+
- Node.js 16+
- Ollama installed (from https://ollama.ai)

### 1. Install Ollama and Download Model

```bash
# Install Ollama from https://ollama.ai (macOS/Windows/Linux)

# Pull a model (choose one)
ollama pull mistral      # Recommended: Fast and good quality
# OR
ollama pull llama2       # Alternative: Slightly slower, more accurate
```

**Start Ollama server** (should run by default on port 11434):
```bash
ollama serve
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
python app.py
```

Backend runs on: `http://localhost:8000`

### 3. Frontend Setup

```bash
# In new terminal
cd frontend

# Install dependencies
npm install

# Start React dev server
npm run dev
```

Frontend runs on: `http://localhost:5173` (or `http://localhost:3000`)

### 4. Open Application

Open browser to: `http://localhost:5173`

---

## 📁 Project Structure

```
ai_voice_interviewer/
├── backend/
│   ├── app.py                    # Main FastAPI application
│   ├── interview_manager.py      # Interview orchestration
│   ├── llm_engine.py            # LLM integration (Ollama)
│   ├── audio_processor.py       # Audio handling
│   ├── requirements.txt         # Python dependencies
│   └── .env                     # Configuration (optional)
│
└── frontend/
    ├── src/
    │   ├── App.jsx              # Main React component
    │   ├── App.css              # Styling
    │   └── index.html           # HTML entry point
    ├── package.json             # Node dependencies
    └── vite.config.js           # Vite configuration
```

---

## 🔧 Configuration

### Backend Configuration (optional .env file)

```env
# backend/.env
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=mistral
# or LLM_MODEL=llama2

FRONTEND_URL=http://localhost:5173
DEBUG=True
```

### Switch LLM Model

In `backend/app.py`, line ~40:
```python
llm_engine = LLMEngine(model="mistral")  # Change to "llama2" if preferred
```

---

## 🎯 How It Works

### Interview Flow

```
1. User enters setup info
   ↓
2. Backend generates first question from job description
   ↓
3. Frontend speaks question (browser text-to-speech)
   ↓
4. User records answer (microphone)
   ↓
5. Web Speech API converts audio → text
   ↓
6. Backend evaluates answer using LLM
   ↓
7. Backend generates next question based on answer quality
   ↓
8. Repeat for 5 questions
   ↓
9. Final report with scores and recommendations
```

### API Endpoints

```
POST /api/start-interview
  Body: { job_description, candidate_name, experience_years, difficulty }
  Returns: { session_id, question, question_number, total_questions }

POST /api/submit-answer
  Body: { session_id, answer }
  Returns: { status, evaluation, question, progress }
           OR { status, evaluation, report } (on final answer)

POST /api/end-interview
  Body: { session_id }
  Returns: { status, report }

GET /api/health
  Returns: { status, llm_ready }

GET /api/models
  Returns: { models }
```

---

## 🎙️ Features

### ✅ Implemented
- Voice-based interview Q&A
- Real-time speech recognition
- AI question generation from job description
- Answer evaluation with scoring
- Final comprehensive report
- Responsive UI (mobile + desktop)
- No API keys required (local LLM)

### 🚀 Future Enhancements
- Emotion/sentiment analysis
- Resume upload
- Video recording
- Multiple languages
- Interview history/database
- HR dashboard
- Export reports (PDF)

---

## 🐛 Troubleshooting

### Issue: "Ollama connection failed"

**Solution**: Make sure Ollama is running
```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# If not running, start it
ollama serve
```

### Issue: "Model not found"

**Solution**: Download the model
```bash
ollama pull mistral
ollama pull llama2
```

### Issue: Microphone not working

**Solution**: 
- Check browser permissions (allow microphone)
- Try Chrome/Firefox/Safari (not all browsers support Web Speech API)
- Check system audio settings

### Issue: Frontend won't start

**Solution**:
```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Issue: CORS errors

**Solution**: Backend is configured to accept localhost requests. If running on different ports:

In `backend/app.py`, update CORS settings:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://your-frontend-url:port"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📊 Interview Customization

### Change Number of Questions

In `backend/interview_manager.py`, line ~35:
```python
self.total_questions = 5  # Change to desired number
```

### Adjust Difficulty

Supported values: `beginner`, `intermediate`, `advanced`

Set during setup or in `backend/llm_engine.py` prompts.

### Customize Prompts

Edit the system prompts in `backend/llm_engine.py`:

```python
# In generate_question() method
prompt = f"""You are a professional technical interviewer...
# Modify this text to change question generation behavior
```

---

## 🔒 Security Notes

- No data is stored (runs locally)
- No external API calls to LLM (Ollama runs locally)
- Speech-to-text uses browser's Web Speech API (no cloud submission)
- CORS configured for localhost only

---

## 📱 Browser Compatibility

| Browser | Speech Recognition | Text-to-Speech | Supported |
|---------|-------------------|-----------------|-----------|
| Chrome  | ✅                | ✅              | ✅        |
| Firefox | ✅                | ✅              | ✅        |
| Safari  | ✅                | ✅              | ✅        |
| Edge    | ✅                | ✅              | ✅        |

---

## 💡 Usage Tips

1. **Job Description**: Paste the full job posting for best results
2. **Experience Level**: Set difficulty based on candidate experience
3. **Quiet Environment**: Use microphone in quiet space for better recognition
4. **Clear Speaking**: Speak clearly and at normal pace
5. **Answer Format**: Full sentences work better than short answers

---

## 🤝 Development

### Add New Features

1. Backend feature: Edit `backend/interview_manager.py` or create new module
2. Frontend UI: Edit `frontend/src/App.jsx` and `App.css`
3. API endpoints: Add to `backend/app.py`

### Deploy

- **Backend**: Deploy FastAPI to Heroku, Railway, or any Python-compatible host
- **Frontend**: Deploy React to Vercel, Netlify, or any static host
- **Ollama**: Run on same server or separate inference server

---

## 📞 Support

For issues:
1. Check troubleshooting section above
2. Check backend logs: `python app.py` shows detailed errors
3. Check browser console: Press F12 → Console tab
4. Verify Ollama is running: `curl http://localhost:11434/api/tags`

---

## 📄 License

MIT - Use freely for personal or commercial projects

---

**Built with ❤️ using FastAPI, React, and local LLMs**
