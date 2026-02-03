"""
Voice Detector Module
Core detection logic for identifying AI-generated vs human-generated voices
"""

import numpy as np
from typing import Dict, Tuple, Optional
import logging
from scipy import signal
from scipy.fft import fft
from scipy.stats import entropy, kurtosis, skew

logger = logging.getLogger(__name__)


class VoiceDetector:
    """Main class for voice detection analysis"""
    
    def __init__(self):
        """Initialize the voice detector with default thresholds"""
        self.thresholds = {
            # AI-generated voices often have these characteristics:
            "spectral_flatness_threshold": 0.15,  # More uniform spectrum
            "harmonic_ratio_threshold": 0.75,     # Higher harmonic content
            "zero_crossing_rate_std": 0.02,       # More consistent ZCR
            "jitter_threshold": 0.005,             # Less pitch variation
            "shimmer_threshold": 0.05,             # Less amplitude variation
            "mel_cepstral_distortion": 2.5,        # More uniform MFCCs
        }
        
        self.language_models = {
            "tamil": {"phoneme_weight": 1.1},
            "english": {"phoneme_weight": 1.0},
            "hindi": {"phoneme_weight": 1.05},
            "malayalam": {"phoneme_weight": 1.1},
            "telugu": {"phoneme_weight": 1.08}
        }
    
    def detect(
        self, 
        audio_data: np.ndarray, 
        sample_rate: int, 
        language: str,
        include_features: bool = False
    ) -> Dict:
        """
        Main detection method
        
        Args:
            audio_data: Audio signal as numpy array
            sample_rate: Sample rate of the audio
            language: Language of the speech
            include_features: Whether to include detailed features
            
        Returns:
            Dictionary with classification, confidence, and explanation
        """
        logger.info(f"Starting detection for {language} audio")
        
        # Extract features
        features = self._extract_features(audio_data, sample_rate, language)
        
        # Calculate AI probability based on features
        ai_probability = self._calculate_ai_probability(features, language)
        
        # Determine classification
        classification = "ai_generated" if ai_probability > 0.5 else "human_generated"
        confidence_score = ai_probability if classification == "ai_generated" else (1 - ai_probability)
        
        # Generate explanation
        explanation = self._generate_explanation(features, ai_probability, language)
        
        result = {
            "classification": classification,
            "confidence_score": round(confidence_score, 4),
            "explanation": explanation
        }
        
        if include_features:
            result["detailed_analysis"] = {
                "features": {k: round(float(v), 4) for k, v in features.items()},
                "ai_indicators": self._get_ai_indicators(features),
                "human_indicators": self._get_human_indicators(features)
            }
        
        return result
    
    def _extract_features(self, audio_data: np.ndarray, sample_rate: int, language: str) -> Dict:
        """Extract audio features for analysis"""
        features = {}
        
        # 1. Spectral Features
        features['spectral_flatness'] = self._calculate_spectral_flatness(audio_data)
        features['spectral_centroid'] = self._calculate_spectral_centroid(audio_data, sample_rate)
        features['spectral_rolloff'] = self._calculate_spectral_rolloff(audio_data, sample_rate)
        
        # 2. Harmonic Features
        features['harmonic_ratio'] = self._calculate_harmonic_ratio(audio_data)
        
        # 3. Temporal Features
        features['zero_crossing_rate'] = self._calculate_zero_crossing_rate(audio_data)
        features['zcr_std'] = self._calculate_zcr_std(audio_data)
        
        # 4. Prosodic Features (pitch variation)
        features['jitter'] = self._calculate_jitter(audio_data, sample_rate)
        features['shimmer'] = self._calculate_shimmer(audio_data)
        
        # 5. Mel-Frequency Cepstral Coefficients
        features['mfcc_variance'] = self._calculate_mfcc_variance(audio_data, sample_rate)
        
        # 6. Energy and Dynamics
        features['energy_entropy'] = self._calculate_energy_entropy(audio_data)
        features['dynamic_range'] = self._calculate_dynamic_range(audio_data)
        
        # 7. Statistical Features
        features['signal_kurtosis'] = kurtosis(audio_data)
        features['signal_skewness'] = skew(audio_data)
        
        return features
    
    def _calculate_spectral_flatness(self, audio_data: np.ndarray) -> float:
        """
        Calculate spectral flatness (Wiener entropy)
        AI voices tend to have flatter spectra (higher values)
        """
        spectrum = np.abs(fft(audio_data))
        spectrum = spectrum[:len(spectrum)//2]  # Take positive frequencies
        
        geometric_mean = np.exp(np.mean(np.log(spectrum + 1e-10)))
        arithmetic_mean = np.mean(spectrum)
        
        flatness = geometric_mean / (arithmetic_mean + 1e-10)
        return float(flatness)
    
    def _calculate_spectral_centroid(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """Calculate spectral centroid (brightness of sound)"""
        spectrum = np.abs(fft(audio_data))
        freqs = np.fft.fftfreq(len(audio_data), 1/sample_rate)
        freqs = freqs[:len(freqs)//2]
        spectrum = spectrum[:len(spectrum)//2]
        
        centroid = np.sum(freqs * spectrum) / (np.sum(spectrum) + 1e-10)
        return float(centroid)
    
    def _calculate_spectral_rolloff(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """Calculate spectral rolloff (85% of energy threshold)"""
        spectrum = np.abs(fft(audio_data))
        spectrum = spectrum[:len(spectrum)//2]
        
        total_energy = np.sum(spectrum)
        threshold = 0.85 * total_energy
        
        cumsum = np.cumsum(spectrum)
        rolloff_idx = np.where(cumsum >= threshold)[0]
        
        if len(rolloff_idx) > 0:
            rolloff_freq = rolloff_idx[0] * sample_rate / (2 * len(spectrum))
            return float(rolloff_freq)
        return 0.0
    
    def _calculate_harmonic_ratio(self, audio_data: np.ndarray) -> float:
        """
        Calculate harmonic-to-noise ratio
        AI voices often have higher harmonic content
        """
        # Use autocorrelation to estimate harmonicity
        autocorr = np.correlate(audio_data, audio_data, mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        
        if len(autocorr) < 2:
            return 0.5
        
        # Find peaks in autocorrelation
        peaks = signal.find_peaks(autocorr[1:], height=0)[0]
        
        if len(peaks) > 0:
            harmonic_strength = np.mean(autocorr[peaks + 1]) / (np.max(autocorr) + 1e-10)
            return float(min(harmonic_strength, 1.0))
        
        return 0.3
    
    def _calculate_zero_crossing_rate(self, audio_data: np.ndarray) -> float:
        """Calculate zero crossing rate"""
        zero_crossings = np.sum(np.abs(np.diff(np.sign(audio_data)))) / 2
        zcr = zero_crossings / len(audio_data)
        return float(zcr)
    
    def _calculate_zcr_std(self, audio_data: np.ndarray) -> float:
        """
        Calculate standard deviation of ZCR across frames
        AI voices tend to have more consistent ZCR (lower std)
        """
        frame_length = 1024
        hop_length = 512
        
        zcr_values = []
        for i in range(0, len(audio_data) - frame_length, hop_length):
            frame = audio_data[i:i+frame_length]
            zcr = self._calculate_zero_crossing_rate(frame)
            zcr_values.append(zcr)
        
        return float(np.std(zcr_values)) if zcr_values else 0.0
    
    def _calculate_jitter(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """
        Calculate jitter (pitch period variation)
        AI voices tend to have lower jitter
        """
        # Simplified jitter calculation using autocorrelation
        autocorr = np.correlate(audio_data, audio_data, mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        
        # Find pitch period
        peaks = signal.find_peaks(autocorr[1:], height=0.3*np.max(autocorr))[0]
        
        if len(peaks) > 1:
            periods = np.diff(peaks)
            jitter = np.std(periods) / (np.mean(periods) + 1e-10)
            return float(min(jitter, 1.0))
        
        return 0.01
    
    def _calculate_shimmer(self, audio_data: np.ndarray) -> float:
        """
        Calculate shimmer (amplitude variation)
        AI voices tend to have lower shimmer
        """
        frame_length = 1024
        hop_length = 512
        
        amplitudes = []
        for i in range(0, len(audio_data) - frame_length, hop_length):
            frame = audio_data[i:i+frame_length]
            amplitude = np.sqrt(np.mean(frame**2))
            amplitudes.append(amplitude)
        
        if len(amplitudes) > 1:
            shimmer = np.std(amplitudes) / (np.mean(amplitudes) + 1e-10)
            return float(min(shimmer, 1.0))
        
        return 0.05
    
    def _calculate_mfcc_variance(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """
        Calculate variance in MFCCs
        AI voices tend to have more uniform MFCCs (lower variance)
        """
        # Simplified MFCC variance using spectral features
        spectrum = np.abs(fft(audio_data))
        spectrum = spectrum[:len(spectrum)//2]
        
        # Apply mel filterbank (simplified)
        mel_spectrum = np.log(spectrum + 1e-10)
        
        # Calculate variance
        variance = np.var(mel_spectrum)
        return float(variance)
    
    def _calculate_energy_entropy(self, audio_data: np.ndarray) -> float:
        """Calculate entropy of energy distribution"""
        frame_length = 1024
        hop_length = 512
        
        energies = []
        for i in range(0, len(audio_data) - frame_length, hop_length):
            frame = audio_data[i:i+frame_length]
            energy = np.sum(frame**2)
            energies.append(energy)
        
        if energies:
            energies = np.array(energies)
            energies = energies / (np.sum(energies) + 1e-10)
            return float(entropy(energies + 1e-10))
        
        return 0.0
    
    def _calculate_dynamic_range(self, audio_data: np.ndarray) -> float:
        """Calculate dynamic range of the signal"""
        max_amplitude = np.max(np.abs(audio_data))
        rms = np.sqrt(np.mean(audio_data**2))
        
        if rms > 0:
            dynamic_range = 20 * np.log10(max_amplitude / (rms + 1e-10))
            return float(dynamic_range)
        
        return 0.0
    
    def _calculate_ai_probability(self, features: Dict, language: str) -> float:
        """
        Calculate probability that the voice is AI-generated
        Based on weighted feature analysis
        """
        ai_score = 0.0
        total_weight = 0.0
        
        # Language-specific weight
        lang_weight = self.language_models.get(language, {}).get("phoneme_weight", 1.0)
        
        # Spectral flatness (higher = more AI-like)
        if features['spectral_flatness'] > self.thresholds['spectral_flatness_threshold']:
            ai_score += 2.0
        total_weight += 2.0
        
        # Harmonic ratio (higher = more AI-like)
        if features['harmonic_ratio'] > self.thresholds['harmonic_ratio_threshold']:
            ai_score += 1.5
        total_weight += 1.5
        
        # ZCR standard deviation (lower = more AI-like)
        if features['zcr_std'] < self.thresholds['zero_crossing_rate_std']:
            ai_score += 1.8 * lang_weight
        total_weight += 1.8 * lang_weight
        
        # Jitter (lower = more AI-like)
        if features['jitter'] < self.thresholds['jitter_threshold']:
            ai_score += 2.2
        total_weight += 2.2
        
        # Shimmer (lower = more AI-like)
        if features['shimmer'] < self.thresholds['shimmer_threshold']:
            ai_score += 2.0
        total_weight += 2.0
        
        # MFCC variance (lower = more AI-like)
        if features['mfcc_variance'] < self.thresholds['mel_cepstral_distortion']:
            ai_score += 1.5
        total_weight += 1.5
        
        # Energy entropy (lower = more AI-like for consistent energy)
        if features['energy_entropy'] < 3.5:
            ai_score += 1.0
        total_weight += 1.0
        
        # Normalize to probability
        probability = ai_score / total_weight if total_weight > 0 else 0.5
        
        return probability
    
    def _generate_explanation(self, features: Dict, ai_probability: float, language: str) -> str:
        """Generate human-readable explanation"""
        classification = "AI-generated" if ai_probability > 0.5 else "human-generated"
        confidence = ai_probability if ai_probability > 0.5 else (1 - ai_probability)
        
        reasons = []
        
        # Analyze key indicators
        if features['spectral_flatness'] > self.thresholds['spectral_flatness_threshold']:
            reasons.append("uniform spectral distribution")
        
        if features['jitter'] < self.thresholds['jitter_threshold']:
            reasons.append("minimal pitch variation")
        
        if features['shimmer'] < self.thresholds['shimmer_threshold']:
            reasons.append("consistent amplitude")
        
        if features['zcr_std'] < self.thresholds['zero_crossing_rate_std']:
            reasons.append("stable zero-crossing rate")
        
        if features['harmonic_ratio'] > self.thresholds['harmonic_ratio_threshold']:
            reasons.append("high harmonic content")
        
        if not reasons:
            reasons = ["natural prosodic variation", "organic spectral characteristics"]
        
        explanation = (
            f"The audio sample is classified as {classification} with {confidence:.1%} confidence. "
            f"Analysis of the {language} speech revealed: {', '.join(reasons[:3])}. "
        )
        
        if ai_probability > 0.5:
            explanation += "These patterns are typical of synthetic voice generation systems."
        else:
            explanation += "These characteristics are consistent with natural human speech production."
        
        return explanation
    
    def _get_ai_indicators(self, features: Dict) -> list:
        """Get list of indicators suggesting AI generation"""
        indicators = []
        
        if features['spectral_flatness'] > self.thresholds['spectral_flatness_threshold']:
            indicators.append("High spectral uniformity")
        
        if features['jitter'] < self.thresholds['jitter_threshold']:
            indicators.append("Low pitch jitter")
        
        if features['shimmer'] < self.thresholds['shimmer_threshold']:
            indicators.append("Low amplitude shimmer")
        
        if features['zcr_std'] < self.thresholds['zero_crossing_rate_std']:
            indicators.append("Consistent zero-crossing rate")
        
        if features['harmonic_ratio'] > self.thresholds['harmonic_ratio_threshold']:
            indicators.append("Strong harmonic structure")
        
        return indicators
    
    def _get_human_indicators(self, features: Dict) -> list:
        """Get list of indicators suggesting human speech"""
        indicators = []
        
        if features['jitter'] > self.thresholds['jitter_threshold']:
            indicators.append("Natural pitch variation")
        
        if features['shimmer'] > self.thresholds['shimmer_threshold']:
            indicators.append("Natural amplitude variation")
        
        if features['zcr_std'] > self.thresholds['zero_crossing_rate_std']:
            indicators.append("Variable articulation")
        
        if features['energy_entropy'] > 3.5:
            indicators.append("Dynamic energy distribution")
        
        return indicators
    
    def detect_language(self, audio_data: np.ndarray, sample_rate: int) -> str:
        """
        Simple language detection based on spectral characteristics
        In production, use a proper language detection model
        """
        # This is a placeholder - in production, use a proper language detection system
        # For now, default to English
        logger.info("Language detection - defaulting to English (use language parameter for accuracy)")
        return "english"
