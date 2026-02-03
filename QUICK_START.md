# 🎙️ AI Voice Interviewer - Quick Reference

## ⚡ 5-Minute Quick Start

### Terminal 1: Ollama
```bash
ollama pull mistral
ollama serve
# ✅ Runs on port 11434
```

### Terminal 2: Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
# ✅ Runs on http://localhost:8000
```

### Terminal 3: Frontend
```bash
cd frontend
npm install
npm run dev
# ✅ Runs on http://localhost:5173
```

### Open Browser
```
http://localhost:5173
```

---

## 🔑 Key Files

| File | Purpose | Edit For |
|------|---------|----------|
| `backend/app.py` | FastAPI server | API routes |
| `backend/interview_manager.py` | Interview logic | Q&A flow |
| `backend/llm_engine.py` | LLM calls | Prompts, model |
| `frontend/src/App.jsx` | React components | UI flow |
| `frontend/src/App.css` | Styling | Design |

---

## 🔄 Data Flow

```
Frontend (React)
    ↓
Browser Web Speech API (microphone)
    ↓
Backend FastAPI
    ↓
Ollama Local LLM
    ↓
Response back to Frontend
    ↓
Browser Synthesis API (speaker)
```

---

## 📚 API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/start-interview` | Begin interview |
| POST | `/api/submit-answer` | Submit answer & get next Q |
| POST | `/api/end-interview` | Finish & get report |
| GET | `/api/health` | Check health |
| GET | `/api/models` | List available models |

---

## 🎯 Customization Examples

### Use Different LLM Model
`backend/app.py` line 40:
```python
llm_engine = LLMEngine(model="llama2")  # Change this
```

### Change Question Count
`backend/interview_manager.py` line 35:
```python
self.total_questions = 10  # Was 5, now 10
```

### Modify Question Prompt
`backend/llm_engine.py` line ~120:
```python
prompt = f"""You are a hiring manager...
# Edit this text to change question style
"""
```

### Change UI Theme Colors
`frontend/src/App.css` top section:
```css
:root {
  --primary: #06b6d4;      /* Change these */
  --accent: #ec4899;
  --success: #4ade80;
}
```

---

## 🐛 Quick Troubleshooting

| Issue | Quick Fix |
|-------|-----------|
| Backend won't start | `ollama serve` in another terminal |
| Model not found | `ollama pull mistral` |
| Frontend won't load | `npm install` then `npm run dev` |
| CORS error | Check `allow_origins` in `backend/app.py` |
| Microphone not working | Check browser permissions |
| LLM slow | Try smaller model: `ollama pull orca` |

---

## 📊 Interview Flow

```
1. SetupStage (form)
   ↓ (POST /start-interview)
2. InterviewStage (Q1)
   ↓ (user speaks)
3. InterviewStage (Q2-Q5)
   ↓ (POST /submit-answer 5 times)
4. CompletedStage (report)
   ↓ (POST /end-interview)
Done
```

---

## 🔌 Add New Feature Checklist

- [ ] Backend logic: `backend/interview_manager.py` or new module
- [ ] API endpoint: `backend/app.py`
- [ ] Frontend component: `frontend/src/App.jsx`
- [ ] Styling: `frontend/src/App.css`
- [ ] Test locally
- [ ] Update documentation

---

## 📈 Performance Tuning

| Optimization | How |
|--------------|-----|
| Faster responses | Use smaller LLM (`orca`, `neural-chat`) |
| Better quality | Use larger LLM (`mistral 7b`, `neural-chat`) |
| Lower latency | Reduce question count (5 → 3) |
| Save memory | Run on GPU-enabled machine |

---

## 🚀 Deployment Checklist

- [ ] Update CORS origins in `backend/app.py`
- [ ] Set environment variables (`.env`)
- [ ] Build frontend: `npm run build`
- [ ] Test in production URLs
- [ ] Configure Ollama on production server
- [ ] Set up HTTPS (if needed)
- [ ] Monitor logs

---

## 📖 Documentation Files

- `README.md` - Project overview
- `SETUP.md` - Detailed setup guide
- `backend/app.py` - API documentation in docstrings
- Code comments - Throughout backend and frontend

---

## 💡 Pro Tips

1. **Test API independently**: Use Postman or curl
2. **Check Ollama logs**: See `ollama serve` output for errors
3. **Browser console**: F12 → Console for frontend errors
4. **Backend logs**: See `python app.py` output
5. **Clear cache**: CTRL+SHIFT+R (hard refresh) in browser

---

## 🔗 Useful Links

- Ollama: https://ollama.ai
- FastAPI: https://fastapi.tiangolo.com
- React: https://react.dev
- Web Speech API: https://w3c.github.io/speech-api/

---

## 📝 Git Commands

```bash
# Initial setup
git init
git add .
git commit -m "Initial commit: AI Voice Interviewer"

# After changes
git add .
git commit -m "Your message"
git push origin main
```

---

**Happy interviewing! 🎉**
