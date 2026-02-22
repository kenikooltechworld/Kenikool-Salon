#!/bin/bash

# Install voice assistant dependencies
echo "Installing Voice Assistant Dependencies..."

# Core voice packages
pip install --no-cache-dir openai-whisper==20240930
pip install --no-cache-dir pyttsx3==2.90
pip install --no-cache-dir langdetect==1.0.9
pip install --no-cache-dir spacy==3.7.2
pip install --no-cache-dir librosa==0.10.0
pip install --no-cache-dir soundfile==0.12.1
pip install --no-cache-dir scipy==1.14.1

# Download spaCy model
python -m spacy download en_core_web_sm

echo "Voice Assistant Dependencies Installed Successfully!"
