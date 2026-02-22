@echo off
echo Installing Voice Assistant Dependencies...
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo Python found. Installing dependencies...
echo.

pip install --upgrade pip setuptools wheel

echo Installing all dependencies from requirements.txt...
pip install -r requirements.txt

echo.
echo Downloading NLTK data...
python -m nltk.downloader punkt averaged_perceptron_tagger maxent_ne_chunker words stopwords

echo.
echo Voice Assistant Dependencies Installed Successfully!
pause
