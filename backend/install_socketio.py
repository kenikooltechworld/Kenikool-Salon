"""Quick script to install python-socketio if missing."""
import subprocess
import sys

def install_socketio():
    """Install python-socketio package."""
    try:
        import socketio
        print("✓ python-socketio is already installed")
    except ImportError:
        print("Installing python-socketio...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-socketio", "python-engineio"])
        print("✓ python-socketio installed successfully")

if __name__ == "__main__":
    install_socketio()
