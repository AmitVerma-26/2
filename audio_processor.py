"""
Audio Processor Module
Handles audio file processing, decoding, and preprocessing
"""

import io
import numpy as np
from pydub import AudioSegment
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Class for processing audio files"""
    
    def __init__(self):
        """Initialize audio processor"""
        self.target_sample_rate = 16000  # Standard for speech processing
        self.max_duration = 300  # Maximum 5 minutes
        self.min_duration = 0.5  # Minimum 0.5 seconds
    
    def process_audio(self, audio_bytes: bytes) -> Tuple[np.ndarray, int, float]:
        """
        Process audio bytes to numpy array
        
        Args:
            audio_bytes: Raw audio file bytes (MP3)
            
        Returns:
            Tuple of (audio_data, sample_rate, duration_seconds)
        """
        try:
            # Load audio using pydub
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
            
            # Get duration
            duration = len(audio) / 1000.0  # Convert to seconds
            
            # Validate duration
            if duration < self.min_duration:
                raise ValueError(f"Audio too short: {duration:.2f}s (minimum: {self.min_duration}s)")
            
            if duration > self.max_duration:
                raise ValueError(f"Audio too long: {duration:.2f}s (maximum: {self.max_duration}s)")
            
            # Convert to mono if stereo
            if audio.channels > 1:
                audio = audio.set_channels(1)
                logger.info("Converted stereo to mono")
            
            # Resample to target sample rate if needed
            if audio.frame_rate != self.target_sample_rate:
                audio = audio.set_frame_rate(self.target_sample_rate)
                logger.info(f"Resampled from {audio.frame_rate}Hz to {self.target_sample_rate}Hz")
            
            # Convert to numpy array
            samples = np.array(audio.get_array_of_samples())
            
            # Normalize to [-1, 1]
            audio_data = samples.astype(np.float32) / (2**15)
            
            # Remove DC offset
            audio_data = audio_data - np.mean(audio_data)
            
            # Apply pre-emphasis filter (typical for speech)
            audio_data = self._apply_preemphasis(audio_data)
            
            logger.info(f"Processed audio: {duration:.2f}s, {self.target_sample_rate}Hz")
            
            return audio_data, self.target_sample_rate, duration
            
        except Exception as e:
            logger.error(f"Error processing audio: {str(e)}")
            raise ValueError(f"Failed to process audio file: {str(e)}")
    
    def _apply_preemphasis(self, audio_data: np.ndarray, coef: float = 0.97) -> np.ndarray:
        """
        Apply pre-emphasis filter to boost high frequencies
        Common in speech processing
        """
        return np.append(audio_data[0], audio_data[1:] - coef * audio_data[:-1])
    
    def validate_audio_quality(self, audio_data: np.ndarray, sample_rate: int) -> dict:
        """
        Validate audio quality metrics
        
        Returns:
            Dictionary with quality metrics
        """
        quality = {}
        
        # Check for clipping
        clipping_ratio = np.sum(np.abs(audio_data) > 0.99) / len(audio_data)
        quality['clipping_ratio'] = float(clipping_ratio)
        quality['is_clipped'] = clipping_ratio > 0.01
        
        # Check signal-to-noise ratio (simplified)
        signal_power = np.mean(audio_data ** 2)
        quality['signal_power'] = float(signal_power)
        quality['is_silent'] = signal_power < 0.001
        
        # Check for DC offset
        dc_offset = np.mean(audio_data)
        quality['dc_offset'] = float(dc_offset)
        
        return quality
