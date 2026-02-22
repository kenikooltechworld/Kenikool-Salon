"""
FFmpeg Docker Utility
Provides functions to use ffmpeg from Docker container for audio/video processing
"""
import subprocess
import os
from pathlib import Path
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

FFMPEG_CONTAINER = "salon-ffmpeg"
TEMP_DIR = Path(__file__).parent.parent.parent / "temp"


def ensure_temp_dir():
    """Ensure temp directory exists"""
    TEMP_DIR.mkdir(exist_ok=True)
    return TEMP_DIR


def is_ffmpeg_available() -> bool:
    """Check if ffmpeg Docker container is running"""
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", f"name={FFMPEG_CONTAINER}", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return FFMPEG_CONTAINER in result.stdout
    except Exception as e:
        logger.warning(f"Could not check ffmpeg container: {e}")
        return False


def run_ffmpeg_command(args: List[str], input_data: Optional[bytes] = None) -> subprocess.CompletedProcess:
    """
    Run ffmpeg command in Docker container
    
    Args:
        args: List of ffmpeg arguments (without 'ffmpeg' prefix)
        input_data: Optional input data to pipe to ffmpeg
        
    Returns:
        CompletedProcess with result
        
    Raises:
        RuntimeError: If ffmpeg container is not available
        subprocess.CalledProcessError: If ffmpeg command fails
    """
    if not is_ffmpeg_available():
        raise RuntimeError(
            f"FFmpeg container '{FFMPEG_CONTAINER}' is not running. "
            "Please start it with: start-services.cmd"
        )
    
    cmd = ["docker", "exec", "-i", FFMPEG_CONTAINER, "ffmpeg"] + args
    
    try:
        result = subprocess.run(
            cmd,
            input=input_data,
            capture_output=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            logger.error(f"FFmpeg error: {result.stderr.decode('utf-8', errors='ignore')}")
            result.check_returncode()
            
        return result
        
    except subprocess.TimeoutExpired:
        logger.error("FFmpeg command timed out")
        raise
    except Exception as e:
        logger.error(f"FFmpeg command failed: {e}")
        raise


def convert_audio(
    input_path: str,
    output_path: str,
    sample_rate: int = 16000,
    channels: int = 1,
    format: str = "wav"
) -> bool:
    """
    Convert audio file to specified format
    
    Args:
        input_path: Path to input audio file
        output_path: Path to output audio file
        sample_rate: Target sample rate (default: 16000 Hz for speech)
        channels: Number of audio channels (default: 1 for mono)
        format: Output format (default: wav)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Read input file
        with open(input_path, 'rb') as f:
            input_data = f.read()
        
        # Build ffmpeg command
        args = [
            "-i", "pipe:0",  # Read from stdin
            "-ar", str(sample_rate),
            "-ac", str(channels),
            "-f", format,
            "pipe:1"  # Write to stdout
        ]
        
        result = run_ffmpeg_command(args, input_data=input_data)
        
        # Write output file
        with open(output_path, 'wb') as f:
            f.write(result.stdout)
        
        logger.info(f"Converted audio: {input_path} -> {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Audio conversion failed: {e}")
        return False


def get_audio_info(file_path: str) -> Optional[dict]:
    """
    Get audio file information using ffprobe
    
    Args:
        file_path: Path to audio file
        
    Returns:
        Dictionary with audio info or None if failed
    """
    try:
        with open(file_path, 'rb') as f:
            input_data = f.read()
        
        args = [
            "-i", "pipe:0",
            "-hide_banner"
        ]
        
        result = run_ffmpeg_command(args, input_data=input_data)
        
        # Parse ffmpeg output (this is simplified, you might want to use ffprobe instead)
        output = result.stderr.decode('utf-8', errors='ignore')
        
        info = {
            "raw_output": output,
            "success": True
        }
        
        return info
        
    except Exception as e:
        logger.error(f"Failed to get audio info: {e}")
        return None


def extract_audio_from_video(video_path: str, audio_path: str) -> bool:
    """
    Extract audio track from video file
    
    Args:
        video_path: Path to input video file
        audio_path: Path to output audio file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(video_path, 'rb') as f:
            input_data = f.read()
        
        args = [
            "-i", "pipe:0",
            "-vn",  # No video
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            "-f", "wav",
            "pipe:1"
        ]
        
        result = run_ffmpeg_command(args, input_data=input_data)
        
        with open(audio_path, 'wb') as f:
            f.write(result.stdout)
        
        logger.info(f"Extracted audio from video: {video_path} -> {audio_path}")
        return True
        
    except Exception as e:
        logger.error(f"Audio extraction failed: {e}")
        return False
