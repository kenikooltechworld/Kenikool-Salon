"""
Audio Preprocessing Utilities
Functions for audio format conversion, noise reduction, and normalization
"""

import io
import logging
import numpy as np
from typing import Optional, Tuple
from pydub import AudioSegment
from pydub.effects import normalize, compress_dynamic_range
from scipy.signal import butter, filtfilt

logger = logging.getLogger(__name__)


class AudioPreprocessor:
    """Audio preprocessing for voice commands"""
    
    # Supported audio formats
    SUPPORTED_FORMATS = ['wav', 'mp3', 'ogg', 'flac', 'webm', 'm4a']
    
    # Target format for STT
    TARGET_FORMAT = 'wav'
    TARGET_SAMPLE_RATE = 16000  # 16kHz for speech recognition
    TARGET_CHANNELS = 1  # Mono
    
    @staticmethod
    def convert_to_wav(
        audio_data: bytes,
        source_format: str = 'webm'
    ) -> bytes:
        """
        Convert audio to WAV format
        
        Args:
            audio_data: Input audio bytes
            source_format: Source audio format
            
        Returns:
            WAV audio bytes
        """
        try:
            # Load audio
            audio = AudioSegment.from_file(
                io.BytesIO(audio_data),
                format=source_format
            )
            
            # Convert to target specs
            audio = audio.set_frame_rate(AudioPreprocessor.TARGET_SAMPLE_RATE)
            audio = audio.set_channels(AudioPreprocessor.TARGET_CHANNELS)
            audio = audio.set_sample_width(2)  # 16-bit
            
            # Export as WAV
            output = io.BytesIO()
            audio.export(output, format='wav')
            
            wav_data = output.getvalue()
            
            logger.info(f"Converted {len(audio_data)} bytes {source_format} to {len(wav_data)} bytes WAV")
            
            return wav_data
            
        except Exception as e:
            logger.error(f"Audio conversion failed: {e}")
            raise
    
    @staticmethod
    def reduce_noise(audio_data: bytes) -> bytes:
        """
        Apply noise reduction to audio
        
        Args:
            audio_data: WAV audio bytes
            
        Returns:
            Noise-reduced WAV audio bytes
        """
        try:
            # Load audio
            audio = AudioSegment.from_wav(io.BytesIO(audio_data))
            
            # Apply high-pass filter to remove low-frequency noise
            audio = audio.high_pass_filter(80)
            
            # Apply low-pass filter to remove high-frequency noise
            audio = audio.low_pass_filter(8000)
            
            # Normalize audio
            audio = normalize(audio)
            
            # Compress dynamic range
            audio = compress_dynamic_range(audio)
            
            # Export
            output = io.BytesIO()
            audio.export(output, format='wav')
            
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Noise reduction failed: {e}")
            # Return original if noise reduction fails
            return audio_data
    
    @staticmethod
    def normalize_volume(audio_data: bytes, target_dBFS: float = -20.0) -> bytes:
        """
        Normalize audio volume
        
        Args:
            audio_data: WAV audio bytes
            target_dBFS: Target volume in dBFS
            
        Returns:
            Volume-normalized WAV audio bytes
        """
        try:
            audio = AudioSegment.from_wav(io.BytesIO(audio_data))
            
            # Calculate gain needed
            change_in_dBFS = target_dBFS - audio.dBFS
            
            # Apply gain
            audio = audio.apply_gain(change_in_dBFS)
            
            # Export
            output = io.BytesIO()
            audio.export(output, format='wav')
            
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Volume normalization failed: {e}")
            return audio_data
    
    @staticmethod
    def trim_silence(
        audio_data: bytes,
        silence_thresh: int = -40,
        min_silence_len: int = 500
    ) -> bytes:
        """
        Trim silence from beginning and end of audio
        
        Args:
            audio_data: WAV audio bytes
            silence_thresh: Silence threshold in dBFS
            min_silence_len: Minimum silence length in ms
            
        Returns:
            Trimmed WAV audio bytes
        """
        try:
            audio = AudioSegment.from_wav(io.BytesIO(audio_data))
            
            # Detect non-silent chunks
            from pydub.silence import detect_nonsilent
            
            nonsilent_ranges = detect_nonsilent(
                audio,
                min_silence_len=min_silence_len,
                silence_thresh=silence_thresh
            )
            
            if not nonsilent_ranges:
                # No speech detected, return original
                return audio_data
            
            # Get first and last non-silent timestamps
            start_trim = nonsilent_ranges[0][0]
            end_trim = nonsilent_ranges[-1][1]
            
            # Trim audio
            audio = audio[start_trim:end_trim]
            
            # Export
            output = io.BytesIO()
            audio.export(output, format='wav')
            
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Silence trimming failed: {e}")
            return audio_data
    
    @staticmethod
    def get_audio_duration(audio_data: bytes) -> float:
        """
        Get audio duration in seconds
        
        Args:
            audio_data: Audio bytes
            
        Returns:
            Duration in seconds
        """
        try:
            audio = AudioSegment.from_wav(io.BytesIO(audio_data))
            return len(audio) / 1000.0  # Convert ms to seconds
            
        except Exception as e:
            logger.error(f"Failed to get audio duration: {e}")
            return 0.0
    
    @staticmethod
    def validate_audio(audio_data: bytes, max_duration: int = 60) -> Tuple[bool, Optional[str]]:
        """
        Validate audio data
        
        Args:
            audio_data: Audio bytes
            max_duration: Maximum allowed duration in seconds
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if not audio_data or len(audio_data) == 0:
                return False, "Audio data is empty"
            
            # Check file size (max 10MB)
            if len(audio_data) > 10 * 1024 * 1024:
                return False, "Audio file too large (max 10MB)"
            
            # Try to load audio
            audio = AudioSegment.from_wav(io.BytesIO(audio_data))
            
            # Check duration
            duration = len(audio) / 1000.0
            if duration > max_duration:
                return False, f"Audio too long (max {max_duration}s)"
            
            if duration < 0.1:
                return False, "Audio too short (min 0.1s)"
            
            return True, None
            
        except Exception as e:
            return False, f"Invalid audio format: {str(e)}"
    
    @staticmethod
    def preprocess_for_stt(
        audio_data: bytes,
        source_format: str = 'webm',
        apply_noise_reduction: bool = True
    ) -> bytes:
        """
        Complete preprocessing pipeline for STT
        
        Args:
            audio_data: Input audio bytes
            source_format: Source audio format
            apply_noise_reduction: Whether to apply noise reduction
            
        Returns:
            Preprocessed WAV audio bytes
        """
        try:
            # Step 1: Convert to WAV
            wav_data = AudioPreprocessor.convert_to_wav(audio_data, source_format)
            
            # Step 2: Trim silence
            wav_data = AudioPreprocessor.trim_silence(wav_data)
            
            # Step 3: Normalize volume
            wav_data = AudioPreprocessor.normalize_volume(wav_data)
            
            # Step 4: Reduce noise (optional)
            if apply_noise_reduction:
                wav_data = AudioPreprocessor.reduce_noise(wav_data)
            
            logger.info("Audio preprocessing complete")
            
            return wav_data
            
        except Exception as e:
            logger.error(f"Audio preprocessing failed: {e}")
            raise
