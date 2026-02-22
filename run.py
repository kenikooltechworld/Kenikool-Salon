#!/usr/bin/env python3
"""
Backend startup script - runs FastAPI with hot reload
Usage: python run.py
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    # Run uvicorn with unbuffered output and proper logging
    cmd = [
        sys.executable, 
        "-u",  # Unbuffered output
        "-m", 
        "uvicorn", 
        "app.main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--log-level", "info",
        "--access-log",
    ]
    
    # Set environment to ensure logs are not buffered
    env = os.environ.copy()
    env['PYTHONUNBUFFERED'] = '1'
    
    subprocess.run(cmd, env=env)

if __name__ == "__main__":
    main()
