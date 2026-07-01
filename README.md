# 📚 Classroom Minutes Generator

An AI-powered system that automatically generates structured minutes of class, summaries, and study notes from classroom audio. Built with HuggingFace models for multilingual (English-Tamil) support.

## ✨ Features

### Core Processing
- 🎙️ **Automatic Transcription** - Convert lecture audio to text using OpenAI Whisper (base/large models)
- 🗣️ **Speaker Diarization** - Identify who spoke using pyannote (with fallback)
- 📝 **Structured Minutes** - Generate organized meeting minutes
- 🌐 **Multilingual Support** - English, Tamil, and auto-detection

### AI & Advanced Features
- ❓ **Question Generation** - Create practice questions from lecture content
- 📋 **Action Item Extraction** - Automatically extract action items and tasks
- 📑 **Topic Segmentation** - Split transcripts into topics by time
- 🃏 **Flashcard Generation** - Create study flashcards from content
- 📝 **Multiple Choice Questions (MCQ)** - Generate MCQs with distractors
- 📊 **Lecture Analytics** - Word count, readability, keywords, sentiment
- 💬 **RAG Chat** - Chat with transcript content (placeholder)

### Export Options
- 📄 **PDF Export** - With or without timestamps
- 📝 **DOCX Export** - Microsoft Word format
- 🌐 **Translation Export** - Translate to other languages (DOCX + TXT)
- 📊 **Summary Export** - Export structured summary as DOCX

### Frontend (Flutter)
- 📱 **Mobile & Web** - Cross-platform Flutter app
- 🎯 **File Picker** - Upload MP3, WAV, M4A, FLAC, etc.
- 🌍 **Language Selection** - Auto / English / Tamil
- ⚡ **Full Pipeline** - One-click full processing or transcription-only
- 📊 **Results Dashboard** - View transcript, summary, questions, and all advanced feature outputs
- 📤 **Export Buttons** - Download PDF, DOCX, translations directly from UI
- 🔌 **Health Check** - Monitor API status

## 🧑‍💻 Tech Stack

- **Backend**: Python, FastAPI, SQLite
- **AI/ML**: PyTorch, Transformers, Whisper, pyannote.audio, BART, T5
- **Frontend**: Flutter (Dart), Provider state management
- **Export**: python-docx, fpdf2, reportlab, google-translate

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip
- Flutter 3.x (for frontend development)
- (Optional) GPU for faster processing

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/classroom-minutes.git
cd classroom-minutes
```

2. **Install backend dependencies**
```bash
cd backend
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
# Edit backend/.env with your settings
# Required: HUGGINGFACE_TOKEN for pyannote diarization
```

4. **Run the backend server**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

5. **Run the Flutter frontend**
```bash
cd frontend
flutter pub get
flutter run -d chrome  # Web
# or
flutter run            # Mobile/Desktop
```

## 📖 API Endpoints

### Core
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/upload` | POST | Upload audio file |
| `/api/transcribe` | POST | Transcribe audio |
| `/api/summarize` | POST | Generate summary |
| `/api/process` | POST | Full processing pipeline |
| `/api/diarize` | POST | Speaker diarization |
| `/api/questions` | POST | Generate questions |

### Advanced Features
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Chat with transcript (RAG) |
| `/api/actions` | POST | Extract action items |
| `/api/topics` | POST | Topic segmentation |
| `/api/flashcards` | POST | Generate flashcards |
| `/api/mcq` | POST | Generate multiple choice questions |
| `/api/analytics` | GET | Lecture analytics |

### Export
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/export/pdf` | POST | Export as PDF |
| `/api/export/docx` | POST | Export as DOCX |
| `/api/export/clean` | POST | Export without timestamps |
| `/api/export/translated` | POST | Export with translation |
| `/api/export/summary` | POST | Export summary |

### Status
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/status/{job_id}` | GET | Get processing status |

## 📖 Usage

### Web Interface

1. Start the backend server (`uvicorn app.main:app --reload --port 8000`)
2. Run the Flutter web app (`cd frontend && flutter run -d chrome`)
3. Upload an audio file (MP3, WAV, M4A, FLAC)
4. Select the language (Auto-detect, English, Tamil)
5. Click **Full Process** or **Transcribe Only**
6. Use **Advanced Features** to run diarization, generate questions, extract actions, etc.
7. **Export** results as PDF, DOCX, or translated documents

### Mobile Interface

1. Start the backend server
2. Run the Flutter app on Android/iOS/Desktop
3. Same workflow as web interface

## 🏗️ Project Structure

```
classroom-minutes/
├── backend/
│   ├── app/
│   │   ├── config/           # Configuration (settings, constants)
│   │   ├── db/               # SQLAlchemy models + repositories
│   │   ├── routes/           # FastAPI route handlers
│   │   ├── schemas/          # Pydantic request/response models
│   │   ├── services/         # Business logic
│   │   │   ├── pipeline.py          # Main orchestration pipeline
│   │   │   ├── transcriber.py       # Whisper transcription
│   │   │   ├── diarizer.py          # Speaker diarization
│   │   │   ├── summarizer.py        # BART summarization
│   │   │   ├── question_generator.py # T5 question generation
│   │   │   ├── audio_processor.py   # Audio preprocessing
│   │   │   └── ...
│   │   └── main.py           # FastAPI app entry point
│   ├── .env                  # Environment variables
│   └── requirements.txt      # Python dependencies
├── frontend/                 # Flutter web/mobile app
│   ├── lib/
│   │   ├── screens/          # Home, Results, Process screens
│   │   ├── providers/        # App state management
│   │   ├── services/         # API + Audio services
│   │   ├── models/           # Dart data models
│   │   └── widgets/          # Reusable UI components
│   └── pubspec.yaml
├── classroom_minutes_app/    # Alternative/reference Flutter app
├── data/                     # Runtime data storage
│   ├── raw/                  # Uploaded audio files
│   ├── transcripts/          # Generated transcripts
│   ├── summaries/            # Generated summaries
│   └── temp/                 # Temporary processing files
├── ERRORS_FIXED.md           # Known issues and fixes
└── README.md
```

## ⚙️ Configuration

Edit `backend/.env` or `backend/app/config/settings.py`:

- **HuggingFace**: `HUGGINGFACE_TOKEN` (required for diarization)
- **Models**: `WHISPER_MODEL`, `SUMMARIZATION_MODEL`
- **Server**: `PORT` (default 8000), `DEBUG`
- **Storage**: `UPLOAD_DIR`, `TRANSCRIPT_DIR`, `SUMMARY_DIR`
- **CORS**: Pre-configured for common Flutter dev ports

## 🤖 Models Used

| Component | Model | Purpose |
|-----------|-------|---------|
| Transcription | `openai/whisper-base` | English speech-to-text |
| Tamil Transcription | `openai/whisper-large` | Tamil speech-to-text |
| Summarization | `facebook/bart-large-cnn` | Text summarization |
| Questions | `valhalla/t5-small-qg-hl` | Question generation |
| Diarization | `pyannote/speaker-diarization` | Speaker identification |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` | Semantic search |

## 🐛 Troubleshooting

### Model Loading Issues
- Ensure you have enough RAM (8GB+ recommended)
- For GPU acceleration, install CUDA-enabled PyTorch
- First run downloads models (~1-3GB each)

### Tamil Transcription
- Use `language: "ta"` for best Tamil results
- Auto-detection works for filenames with Tamil characters

### Large Files
- Maximum file size: 500MB
- Longer lectures may take several minutes to process

### Flutter Frontend
- Ensure backend is running on `http://127.0.0.1:8000`
- Check API health using the health check button in the app
- For mobile, update `apiBaseUrl` in `lib/utils/constants.dart` to your machine's IP

## 📝 License

MIT License
#   M i n u t e s - o f - C l a s s r o o m  
 #   M i n u t e s - o f - C l a s s r o o m  
 #   M i n u t e s - o f - C l a s s r o o m  
 #   M i n u t e s - o f - C l a s s r o o m  
 #   M i n u t e s - o f - C l a s s r o o m  
 #   M i n u t e s - o f - C l a s s r o o m  
 #   L e c t u r e S c r i b e  
 # LectureScribe
