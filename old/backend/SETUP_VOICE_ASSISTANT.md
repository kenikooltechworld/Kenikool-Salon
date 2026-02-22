# Voice Assistant Setup Instructions

## Quick Setup

### Windows
```bash
cd backend
install_voice_deps.bat
```

### macOS/Linux
```bash
cd backend
chmod +x install_voice_deps.sh
./install_voice_deps.sh
```

## Manual Installation

If the scripts don't work, install manually:

```bash
# Core dependencies
pip install openai-whisper==20240930
pip install pyttsx3==2.90
pip install langdetect==1.0.9
pip install spacy==3.7.2
pip install librosa==0.10.0
pip install soundfile==0.12.1
pip install scipy==1.14.1

# Download spaCy model
python -m spacy download en_core_web_sm
```

## Verify Installation

```bash
python -c "import whisper; print('Whisper OK')"
python -c "import pyttsx3; print('pyttsx3 OK')"
python -c "import langdetect; print('langdetect OK')"
python -c "import spacy; print('spaCy OK')"
python -c "import librosa; print('librosa OK')"
```

## Start Backend

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Test Voice API

```bash
# Health check
curl http://localhost:8000/api/voice/health

# Get supported languages
curl http://localhost:8000/api/voice/languages
```

## Frontend Setup

```bash
cd salon
npm install
npm run dev
```

## Access Voice Assistant

Navigate to: `http://localhost:5173/voice-assistant`

## Troubleshooting

### Whisper model download fails
- Ensure 1.5GB free disk space
- Check internet connection
- Try: `python -c "import whisper; whisper.load_model('base')"`

### spaCy model not found
- Run: `python -m spacy download en_core_web_sm`

### pyttsx3 issues on Linux
- Install: `sudo apt-get install espeak`

### Redis connection issues
- Optional: Install Redis for persistent sessions
- Without Redis, uses in-memory storage
