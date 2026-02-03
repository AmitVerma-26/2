"""
Sample Audio Generator and Test Script
Creates synthetic test audio for demonstration purposes
"""

import numpy as np
from scipy.io import wavfile
from pydub import AudioSegment
import io
import base64
import requests
import os


def generate_synthetic_voice(duration=3.0, sample_rate=16000, is_ai=True):
    """
    Generate synthetic audio for testing
    
    Args:
        duration: Duration in seconds
        sample_rate: Sample rate in Hz
        is_ai: If True, generate AI-like characteristics; else human-like
    """
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Base frequency (fundamental)
    base_freq = 150  # Hz
    
    if is_ai:
        # AI-like voice characteristics
        # More consistent pitch
        pitch_variation = np.sin(2 * np.pi * 0.5 * t) * 5
        
        # Lower jitter and shimmer
        jitter = 0.002
        shimmer = 0.01
        
        # More harmonic content
        harmonics = [1, 2, 3, 4, 5, 6]
        harmonic_weights = [1.0, 0.7, 0.5, 0.3, 0.2, 0.1]
    else:
        # Human-like voice characteristics
        # More natural pitch variation
        pitch_variation = np.sin(2 * np.pi * 0.3 * t) * 15 + \
                         np.sin(2 * np.pi * 1.2 * t) * 8
        
        # Higher jitter and shimmer
        jitter = 0.01
        shimmer = 0.08
        
        # Less uniform harmonics
        harmonics = [1, 2, 3, 4, 5]
        harmonic_weights = [1.0, 0.6, 0.3, 0.15, 0.08]
    
    # Generate signal with harmonics
    signal = np.zeros_like(t)
    
    for harmonic, weight in zip(harmonics, harmonic_weights):
        # Add jitter (pitch variation)
        freq_modulation = base_freq * harmonic + pitch_variation
        freq_modulation += np.random.randn(len(t)) * jitter * base_freq * harmonic
        
        # Calculate phase
        phase = 2 * np.pi * np.cumsum(freq_modulation) / sample_rate
        
        # Add shimmer (amplitude variation)
        amplitude = weight * (1 + shimmer * np.sin(2 * np.pi * 3 * t))
        amplitude += np.random.randn(len(t)) * shimmer * 0.1
        
        # Add harmonic component
        signal += amplitude * np.sin(phase)
    
    # Add noise
    if is_ai:
        noise_level = 0.02  # Less noise for AI
    else:
        noise_level = 0.05  # More noise for human
    
    signal += np.random.randn(len(t)) * noise_level
    
    # Normalize
    signal = signal / np.max(np.abs(signal)) * 0.8
    
    # Add breathing/pauses for realism
    if not is_ai:
        # Add more variation in energy
        envelope = 1 + 0.3 * np.sin(2 * np.pi * 0.7 * t)
        signal *= envelope
    
    # Convert to int16
    signal = (signal * 32767).astype(np.int16)
    
    return signal, sample_rate


def save_as_mp3(signal, sample_rate, filename):
    """Save audio signal as MP3 file"""
    # First save as WAV
    wav_io = io.BytesIO()
    wavfile.write(wav_io, sample_rate, signal)
    wav_io.seek(0)
    
    # Convert to MP3
    audio = AudioSegment.from_wav(wav_io)
    audio.export(filename, format="mp3", bitrate="128k")
    
    print(f"Saved: {filename}")


def test_api_with_sample(filename, language="english", include_features=True):
    """Test the API with a generated sample"""
    # Read MP3 file
    with open(filename, 'rb') as f:
        audio_bytes = f.read()
    
    # Encode to base64
    audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
    
    # Make request
    try:
        response = requests.post(
            "http://localhost:8000/detect",
            json={
                "audio_data": audio_base64,
                "language": language,
                "include_features": include_features
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n{'='*60}")
            print(f"File: {filename}")
            print(f"Classification: {result['classification'].upper()}")
            print(f"Confidence: {result['confidence_score']:.2%}")
            print(f"Language: {result['language_detected']}")
            print(f"Duration: {result['audio_duration_seconds']:.2f}s")
            print(f"Processing Time: {result['processing_time_ms']:.2f}ms")
            print(f"\nExplanation:")
            print(f"  {result['explanation']}")
            
            if include_features and 'detailed_analysis' in result:
                print(f"\nKey Features:")
                features = result['detailed_analysis']['features']
                print(f"  Spectral Flatness: {features['spectral_flatness']:.4f}")
                print(f"  Jitter: {features['jitter']:.4f}")
                print(f"  Shimmer: {features['shimmer']:.4f}")
                print(f"  Harmonic Ratio: {features['harmonic_ratio']:.4f}")
                
                print(f"\nAI Indicators: {result['detailed_analysis']['ai_indicators']}")
                print(f"Human Indicators: {result['detailed_analysis']['human_indicators']}")
            
            print(f"{'='*60}\n")
            
            return result
        else:
            print(f"Error: {response.status_code}")
            print(response.json())
            
    except Exception as e:
        print(f"Error testing {filename}: {str(e)}")


if __name__ == "__main__":
    print("Generating sample audio files for testing...")
    print("-" * 60)
    
    # Create samples directory
    os.makedirs("samples", exist_ok=True)
    
    # Generate AI-like samples
    print("\nGenerating AI-like voices...")
    for i in range(2):
        signal, sr = generate_synthetic_voice(duration=3.0, is_ai=True)
        filename = f"samples/ai_sample_{i+1}.mp3"
        save_as_mp3(signal, sr, filename)
    
    # Generate human-like samples
    print("\nGenerating human-like voices...")
    for i in range(2):
        signal, sr = generate_synthetic_voice(duration=3.0, is_ai=False)
        filename = f"samples/human_sample_{i+1}.mp3"
        save_as_mp3(signal, sr, filename)
    
    print("\n" + "=" * 60)
    print("Testing with API (make sure API is running on port 8000)")
    print("=" * 60)
    
    # Test if API is available
    try:
        health = requests.get("http://localhost:8000/health", timeout=5)
        if health.status_code == 200:
            print("✓ API is running")
            
            # Test AI samples
            print("\n\nTesting AI-Generated Samples:")
            print("-" * 60)
            test_api_with_sample("samples/ai_sample_1.mp3", include_features=True)
            test_api_with_sample("samples/ai_sample_2.mp3", include_features=False)
            
            # Test human samples
            print("\n\nTesting Human-Generated Samples:")
            print("-" * 60)
            test_api_with_sample("samples/human_sample_1.mp3", include_features=True)
            test_api_with_sample("samples/human_sample_2.mp3", include_features=False)
            
        else:
            print("✗ API is not responding correctly")
    except requests.exceptions.ConnectionError:
        print("✗ API is not running. Start it with: python main.py")
    except Exception as e:
        print(f"✗ Error connecting to API: {str(e)}")
    
    print("\n" + "=" * 60)
    print("Sample files have been saved in the 'samples' directory")
    print("You can use these files to test the API manually")
    print("=" * 60)
