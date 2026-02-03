# 🎙️ AI Voice Interviewer

A cutting-edge, **voice-based AI interview platform** that simulates real human interviews using local LLMs and browser speech APIs. 

**Zero cost. No API keys. Fully private.**

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
✅ **Scoring & Feedback**: Automatic evaluation with detailed feedback  
✅ **Job-Specific**: Tailors questions to actual job description  
✅ **Local LLM**: Uses Ollama (Mistral/Llama2)—no cloud costs  
✅ **Beautiful UI**: Modern, responsive design with animations  
✅ **Comprehensive Reports**: Final score, strengths, weaknesses, recommendations  

---

## 🚀 Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| Backend | FastAPI (Python) | Fast, async, easy to extend |
| LLM | Ollama + Mistral/Llama2 | Local, free, no API costs |
| Frontend | React 18 | Modern, responsive, interactive |
| Speech Recognition | Web Speech API | Browser-native, no APIs needed |
| Speech Synthesis | Web Speech API | Browser-native text-to-speech |
| Styling | CSS3 + Animations | Beautiful, modern UI |

---

## 📋 Prerequisites

Before starting, install:

1. **Python 3.9+**: [python.org](https://python.org)
2. **Node.js 16+**: [nodejs.org](https://nodejs.org)
3. **Ollama**: [ollama.ai](https://ollama.ai)

Check installations:
```bash
python --version    # Python 3.9+
node --version      # Node 16+
ollama --version    # Should be installed
```

---

## ⚡ Quick Start (5 minutes)

### Step 1: Pull LLM Model
```bash
# Choose one (or install both)
ollama pull mistral    # Recommended: Fast & accurate
ollama pull llama2     # Alternative: Slower, more accurate
```

### Step 2: Start Ollama Server
```bash
ollama serve
# Runs on http://localhost:11434
```

### Step 3: Setup Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py               # Runs on http://localhost:8000
```

### Step 4: Setup Frontend
```bash
# In new terminal
cd frontend
npm install
npm run dev                  # Runs on http://localhost:5173
```

### Step 5: Open Application
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

### Change LLM Model
**File**: `backend/app.py` (line ~40)
```python
llm_engine = LLMEngine(model="mistral")  # or "llama2"
```

### Change Number of Questions
**File**: `backend/interview_manager.py` (line ~35)
```python
self.total_questions = 5  # Change to desired number
```

### Customize Interview Prompts
**File**: `backend/llm_engine.py`  
Edit the `prompt` variables in `generate_question()` method

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

### Ollama Connection Failed
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start it
ollama serve
```

### Model Not Found
```bash
ollama pull mistral
ollama pull llama2
```

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

## 🔒 Privacy & Security

✅ **All local**: LLM runs on your machine  
✅ **No data storage**: Interviews don't persist  
✅ **No cloud calls**: Speech recognition happens in browser  
✅ **No API keys**: Everything is free and private  
✅ **No tracking**: No analytics or telemetry  

---

## 📊 Performance

| Metric | Value |
|--------|-------|
| First question generation | ~3-5 seconds |
| Answer evaluation | ~2-3 seconds |
| Speech recognition latency | ~1 second |
| Text-to-speech latency | ~500ms |
| Total Q→A→Q cycle | ~6-10 seconds |

*Times vary based on LLM model and system specs*

---

## 🚀 Future Roadmap

- [ ] Video recording (camera + facial expressions)
- [ ] Emotion/sentiment analysis
- [ ] Resume upload & parsing
- [ ] Multiple languages
- [ ] Interview history & analytics
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
6. **Database integration** for history

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
