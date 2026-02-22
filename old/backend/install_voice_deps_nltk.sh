#!/bin/bash

echo "Installing Voice Assistant Dependencies..."
echo ""

if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

echo "Python found. Installing dependencies..."
echo ""

pip install --upgrade pip setuptools wheel

echo "Installing all dependencies from requirements.txt..."
pip install -r requirements.txt

echo ""
echo "Downloading NLTK data..."
python3 -m nltk.downloader punkt averaged_perceptron_tagger maxent_ne_chunker words stopwords

echo ""
echo "Voice Assistant Dependencies Installed Successfully!"
