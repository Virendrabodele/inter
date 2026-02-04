import React, { useState, useRef, useEffect } from 'react';
import './App.css';

// Get API base URL from environment variable or use default
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export default function App() {
  // Interview state
  const [stage, setStage] = useState('setup'); // setup|interviewing|completed
  const [isRecording, setIsRecording] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [transcript, setTranscript] = useState('');
  
  // Setup form
  const [jobDescription, setJobDescription] = useState('');
  const [candidateName, setCandidateName] = useState('');
  const [experience, setExperience] = useState(0);
  const [difficulty, setDifficulty] = useState('intermediate');
  
  // Interview data
  const [sessionId, setSessionId] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState('');
  const [questionNumber, setQuestionNumber] = useState(0);
  const [totalQuestions, setTotalQuestions] = useState(5);
  const [currentAnswer, setCurrentAnswer] = useState('');
  const [progress, setProgress] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [finalReport, setFinalReport] = useState(null);
  
  // Settings
  const [autoStartRecording, setAutoStartRecording] = useState(true);
  const [speechRecognitionSupported, setSpeechRecognitionSupported] = useState(true);
  const [storageInfo, setStorageInfo] = useState(null);
  
  // Audio refs
  const mediaRecorderRef = useRef(null);
  const audioContextRef = useRef(null);
  const audioStreamRef = useRef(null);
  const audioElementRef = useRef(null);
  
  // Web Speech API (fallback for transcription)
  const recognitionRef = useRef(null);
  
  // Check health on mount to get storage info
  useEffect(() => {
    fetch(`${API_BASE_URL}/api/health`)
      .then(res => res.json())
      .then(data => setStorageInfo(data))
      .catch(err => console.error('Failed to fetch health:', err));
  }, []);
  
  // Initialize Web Speech API
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.language = 'en-US';
      
      recognitionRef.current.onstart = () => {
        setIsRecording(true);
        setTranscript('');
      };
      
      recognitionRef.current.onresult = (event) => {
        let interim = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcriptPart = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            setCurrentAnswer(prev => prev + transcriptPart + ' ');
          } else {
            interim += transcriptPart;
          }
        }
        setTranscript(interim);
      };
      
      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsRecording(false);
      };
      
      recognitionRef.current.onend = () => {
        setIsRecording(false);
      };
      setSpeechRecognitionSupported(true);
    } else {
      setSpeechRecognitionSupported(false);
      console.warn('Speech recognition not supported in this browser');
    }
  }, []);
  
  // Handle setup submission
  const handleStartInterview = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/start-interview`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          job_description: jobDescription,
          candidate_name: candidateName,
          experience_years: parseInt(experience),
          difficulty: difficulty
        })
      });
      
      if (!response.ok) throw new Error('Failed to start interview');
      
      const data = await response.json();
      setSessionId(data.session_id);
      setCurrentQuestion(data.question);
      setQuestionNumber(data.question_number);
      setTotalQuestions(data.total_questions);
      setProgress(1 / data.total_questions);
      setStage('interviewing');
      
      // Speak the question
      speakQuestion(data.question);
    } catch (error) {
      alert('Error starting interview: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Speak question using Web Speech API
  const speakQuestion = (question) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(question);
      utterance.rate = 0.95;
      utterance.pitch = 1.0;
      utterance.volume = 1.0;
      
      utterance.onstart = () => setIsPlaying(true);
      utterance.onend = () => {
        setIsPlaying(false);
        // Start listening after question is spoken (if auto-start is enabled)
        if (autoStartRecording && speechRecognitionSupported) {
          setTimeout(() => startRecording(), 500);
        }
      };
      
      window.speechSynthesis.cancel(); // Cancel any previous speech
      window.speechSynthesis.speak(utterance);
    }
  };
  
  // Start recording user answer
  const startRecording = async () => {
    if (!speechRecognitionSupported) {
      // If speech recognition is not supported, just allow manual typing
      return;
    }
    
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioStreamRef.current = stream;
      
      if (recognitionRef.current) {
        recognitionRef.current.start();
      }
    } catch (error) {
      alert('Microphone access denied: ' + error.message);
    }
  };
  
  // Stop recording
  const stopRecording = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    
    if (audioStreamRef.current) {
      audioStreamRef.current.getTracks().forEach(track => track.stop());
    }
    
    setIsRecording(false);
  };
  
  // Toggle recording
  const toggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };
  
  // Submit answer
  const handleSubmitAnswer = async () => {
    if (!currentAnswer.trim()) {
      alert('Please provide an answer');
      return;
    }
    
    stopRecording();
    setIsLoading(true);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/submit-answer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          answer: currentAnswer.trim()
        })
      });
      
      if (!response.ok) throw new Error('Failed to submit answer');
      
      const data = await response.json();
      
      if (data.status === 'next_question') {
        // Move to next question
        setCurrentAnswer('');
        setTranscript('');
        setCurrentQuestion(data.question);
        setQuestionNumber(data.question_number);
        setProgress(data.progress);
        
        // Speak next question
        setTimeout(() => speakQuestion(data.question), 1000);
      } else if (data.status === 'interview_complete') {
        // Interview finished
        setFinalReport(data.report);
        setStage('completed');
      }
    } catch (error) {
      alert('Error: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Export to sheets
  const handleExportToSheets = async () => {
    if (!sessionId) return;
    
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/export/${sessionId}`, {
        method: 'POST'
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to export');
      }
      
      const data = await response.json();
      alert(`✓ ${data.message}`);
    } catch (error) {
      alert('Export failed: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Speak answer for review
  const speakAnswer = () => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(currentAnswer);
      utterance.rate = 0.95;
      window.speechSynthesis.cancel();
      window.speechSynthesis.speak(utterance);
    }
  };
  
  // Restart interview
  const handleRestart = () => {
    setStage('setup');
    setJobDescription('');
    setCandidateName('');
    setExperience(0);
    setCurrentAnswer('');
    setTranscript('');
    setFinalReport(null);
  };
  
  return (
    <div className="app">
      {stage === 'setup' && <SetupStage 
        jobDescription={jobDescription}
        setJobDescription={setJobDescription}
        candidateName={candidateName}
        setCandidateName={setCandidateName}
        experience={experience}
        setExperience={setExperience}
        difficulty={difficulty}
        setDifficulty={setDifficulty}
        onSubmit={handleStartInterview}
        isLoading={isLoading}
        speechRecognitionSupported={speechRecognitionSupported}
        storageInfo={storageInfo}
      />}
      
      {stage === 'interviewing' && <InterviewStage
        currentQuestion={currentQuestion}
        questionNumber={questionNumber}
        totalQuestions={totalQuestions}
        progress={progress}
        isRecording={isRecording}
        isPlaying={isPlaying}
        isLoading={isLoading}
        currentAnswer={currentAnswer}
        setCurrentAnswer={setCurrentAnswer}
        transcript={transcript}
        onToggleRecording={toggleRecording}
        onSubmitAnswer={handleSubmitAnswer}
        onSpeakAnswer={speakAnswer}
        speechRecognitionSupported={speechRecognitionSupported}
        autoStartRecording={autoStartRecording}
        setAutoStartRecording={setAutoStartRecording}
      />}
      
      {stage === 'completed' && <CompletedStage
        report={finalReport}
        onRestart={handleRestart}
        onExport={handleExportToSheets}
        canExport={storageInfo?.storage_mode?.includes('sheets') || false}
        isLoading={isLoading}
      />}
    </div>
  );
}

// Setup Stage Component
function SetupStage({
  jobDescription, setJobDescription,
  candidateName, setCandidateName,
  experience, setExperience,
  difficulty, setDifficulty,
  onSubmit, isLoading,
  speechRecognitionSupported,
  storageInfo
}) {
  return (
    <div className="stage setup-stage">
      <div className="setup-container">
        <div className="setup-header">
          <h1 className="setup-title">🎙️ Voice Interview</h1>
          <p className="setup-subtitle">Powered by AI</p>
          {storageInfo && (
            <p className="storage-info" style={{fontSize: '0.85rem', marginTop: '0.5rem', color: '#888'}}>
              Storage: {storageInfo.storage_mode || 'local'}
              {storageInfo.sheet_name && ` (${storageInfo.sheet_name})`}
            </p>
          )}
        </div>
        
        {!speechRecognitionSupported && (
          <div className="warning-banner" style={{
            background: '#fff3cd',
            border: '1px solid #ffc107',
            padding: '1rem',
            borderRadius: '8px',
            marginBottom: '1rem'
          }}>
            <strong>⚠️ Speech Recognition Not Supported</strong>
            <p style={{margin: '0.5rem 0 0 0', fontSize: '0.9rem'}}>
              Your browser doesn't support speech recognition. You can still take the interview by typing your answers manually.
            </p>
          </div>
        )}
        
        <form onSubmit={onSubmit} className="setup-form">
          <div className="form-group">
            <label htmlFor="name">Your Name</label>
            <input
              id="name"
              type="text"
              placeholder="John Doe"
              value={candidateName}
              onChange={(e) => setCandidateName(e.target.value)}
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="experience">Years of Experience</label>
            <input
              id="experience"
              type="number"
              min="0"
              max="50"
              placeholder="5"
              value={experience}
              onChange={(e) => setExperience(e.target.value)}
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="difficulty">Interview Difficulty</label>
            <select
              id="difficulty"
              value={difficulty}
              onChange={(e) => setDifficulty(e.target.value)}
            >
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </div>
          
          <div className="form-group">
            <label htmlFor="job">Job Description</label>
            <textarea
              id="job"
              placeholder="Paste the job description here..."
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              rows="8"
              required
            />
          </div>
          
          <button
            type="submit"
            disabled={isLoading}
            className="btn btn-primary"
          >
            {isLoading ? 'Starting...' : 'Start Interview'}
          </button>
        </form>
      </div>
    </div>
  );
}

// Interview Stage Component
function InterviewStage({
  currentQuestion, questionNumber, totalQuestions, progress,
  isRecording, isPlaying, isLoading,
  currentAnswer, setCurrentAnswer, transcript,
  onToggleRecording, onSubmitAnswer, onSpeakAnswer,
  speechRecognitionSupported,
  autoStartRecording, setAutoStartRecording
}) {
  return (
    <div className="stage interview-stage">
      <div className="interview-container">
        {/* Progress bar */}
        <div className="progress-section">
          <div className="progress-bar">
            <div 
              className="progress-fill"
              style={{ width: `${progress * 100}%` }}
            />
          </div>
          <div className="progress-text">
            Question {questionNumber} of {totalQuestions}
          </div>
        </div>
        
        {/* Settings */}
        {speechRecognitionSupported && (
          <div className="settings-section" style={{
            textAlign: 'center',
            marginBottom: '1rem',
            fontSize: '0.9rem'
          }}>
            <label style={{cursor: 'pointer', userSelect: 'none'}}>
              <input 
                type="checkbox" 
                checked={autoStartRecording}
                onChange={(e) => setAutoStartRecording(e.target.checked)}
                style={{marginRight: '0.5rem'}}
              />
              Auto-start recording after AI speaks
            </label>
          </div>
        )}
        
        {/* Question display */}
        <div className="question-section">
          <div className={`question-box ${isPlaying ? 'speaking' : ''}`}>
            <div className="question-label">Current Question</div>
            <p className="question-text">{currentQuestion}</p>
          </div>
        </div>
        
        {/* Audio visualization */}
        <div className="audio-section">
          {isPlaying && (
            <div className="speaking-indicator">
              <div className="pulse"></div>
              <div className="pulse"></div>
              <div className="pulse"></div>
              AI Speaking...
            </div>
          )}
          
          {isRecording && (
            <div className="recording-indicator">
              <div className="record-dot"></div>
              Recording your answer...
            </div>
          )}
        </div>
        
        {/* Answer capture */}
        <div className="answer-section">
          <div className="answer-box">
            <div className="answer-label">Your Answer</div>
            {speechRecognitionSupported ? (
              <>
                <p className="answer-text">
                  {currentAnswer || (transcript ? `${currentAnswer}${transcript}` : 'Speak your answer...')}
                </p>
                <div className="interim-text">{transcript}</div>
              </>
            ) : (
              <textarea
                className="answer-textarea"
                value={currentAnswer}
                onChange={(e) => setCurrentAnswer(e.target.value)}
                placeholder="Type your answer here..."
                rows="6"
                style={{
                  width: '100%',
                  padding: '1rem',
                  borderRadius: '8px',
                  border: '2px solid #e0e0e0',
                  fontSize: '1rem',
                  fontFamily: 'inherit',
                  resize: 'vertical'
                }}
              />
            )}
          </div>
        </div>
        
        {/* Controls */}
        <div className="controls-section">
          {speechRecognitionSupported && (
            <button
              className={`btn btn-mic ${isRecording ? 'recording' : ''}`}
              onClick={onToggleRecording}
              disabled={isPlaying || isLoading}
            >
              {isRecording ? '⊙ Stop Recording' : '🎤 Start Recording'}
            </button>
          )}
          
          {currentAnswer && speechRecognitionSupported && (
            <button
              className="btn btn-secondary"
              onClick={onSpeakAnswer}
            >
              🔊 Hear Answer
            </button>
          )}
          
          <button
            className="btn btn-submit"
            onClick={onSubmitAnswer}
            disabled={!currentAnswer.trim() || isLoading || isRecording || isPlaying}
          >
            {isLoading ? 'Processing...' : '✓ Submit Answer'}
          </button>
        </div>
      </div>
    </div>
  );
}

// Completed Stage Component
function CompletedStage({ report, onRestart, onExport, canExport, isLoading }) {
  if (!report) return null;
  
  const scoreColor = report.overall_score >= 7 ? '#4ade80' : report.overall_score >= 5 ? '#fbbf24' : '#f87171';
  
  return (
    <div className="stage completed-stage">
      <div className="report-container">
        <div className="report-header">
          <h1>Interview Complete 🎉</h1>
          <p className="candidate-name">{report.candidate_name}</p>
        </div>
        
        {/* Score display */}
        <div className="score-section">
          <div className="score-box" style={{ borderColor: scoreColor }}>
            <div className="score-value" style={{ color: scoreColor }}>
              {report.overall_score.toFixed(1)}/10
            </div>
            <div className="score-label">Overall Score</div>
            <div className="score-recommendation">
              {report.hire_recommendation && (
                <span className={`recommendation ${report.hire_recommendation}`}>
                  {report.hire_recommendation.toUpperCase()}
                </span>
              )}
            </div>
          </div>
        </div>
        
        {/* Summary */}
        <div className="summary-section">
          <h2>Summary</h2>
          <p>{report.summary}</p>
        </div>
        
        {/* Strengths and weaknesses */}
        <div className="details-section">
          <div className="detail-box">
            <h3>✅ Strengths</h3>
            <ul>
              {(report.strengths || []).map((str, i) => (
                <li key={i}>{str}</li>
              ))}
            </ul>
          </div>
          
          <div className="detail-box">
            <h3>⚠️ Areas for Improvement</h3>
            <ul>
              {(report.weaknesses || []).map((weak, i) => (
                <li key={i}>{weak}</li>
              ))}
            </ul>
          </div>
        </div>
        
        {/* Recommendations */}
        <div className="recommendations-section">
          <h2>💡 Recommendations</h2>
          <ol>
            {(report.recommendations || []).map((rec, i) => (
              <li key={i}>{rec}</li>
            ))}
          </ol>
        </div>
        
        {/* Individual scores */}
        <div className="scores-section">
          <h2>Question Scores</h2>
          <div className="scores-grid">
            {(report.individual_scores || []).map((score, i) => (
              <div key={i} className="score-item">
                <div className="score-number">Q{i + 1}</div>
                <div className="score-bar">
                  <div 
                    className="score-bar-fill"
                    style={{
                      width: `${(score / 10) * 100}%`,
                      backgroundColor: score >= 7 ? '#4ade80' : score >= 5 ? '#fbbf24' : '#f87171'
                    }}
                  />
                </div>
                <div className="score-val">{score}/10</div>
              </div>
            ))}
          </div>
        </div>
        
        {/* Action buttons */}
        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
          {canExport && (
            <button
              className="btn btn-secondary btn-large"
              onClick={onExport}
              disabled={isLoading}
              style={{ minWidth: '200px' }}
            >
              {isLoading ? 'Exporting...' : '📊 Save to Google Sheets'}
            </button>
          )}
          
          <button
            className="btn btn-primary btn-large"
            onClick={onRestart}
            style={{ minWidth: '200px' }}
          >
            Take Another Interview
          </button>
        </div>
      </div>
    </div>
  );
}
