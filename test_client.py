"""
Test Client for Voice Detection API
Demonstrates how to use the API with example requests
"""

import requests
import base64
import json
from pathlib import Path


class VoiceDetectionClient:
    """Client for interacting with the Voice Detection API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize client with API base URL"""
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self):
        """Check API health status"""
        response = self.session.get(f"{self.base_url}/health")
        return response.json()
    
    def get_supported_languages(self):
        """Get list of supported languages"""
        response = self.session.get(f"{self.base_url}/languages")
        return response.json()
    
    def detect_from_file(self, file_path: str, language: str = None, include_features: bool = False):
        """
        Detect voice from an MP3 file
        
        Args:
            file_path: Path to MP3 file
            language: Optional language code (tamil, english, hindi, malayalam, telugu)
            include_features: Whether to include detailed features
            
        Returns:
            Detection result
        """
        # Read and encode file
        with open(file_path, 'rb') as f:
            audio_bytes = f.read()
        
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        # Prepare request
        payload = {
            "audio_data": audio_base64,
            "include_features": include_features
        }
        
        if language:
            payload["language"] = language
        
        # Send request
        response = self.session.post(f"{self.base_url}/detect", json=payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": True,
                "status_code": response.status_code,
                "detail": response.json()
            }
    
    def detect_from_base64(self, audio_base64: str, language: str = None, include_features: bool = False):
        """
        Detect voice from base64-encoded audio
        
        Args:
            audio_base64: Base64-encoded MP3 data
            language: Optional language code
            include_features: Whether to include detailed features
            
        Returns:
            Detection result
        """
        payload = {
            "audio_data": audio_base64,
            "include_features": include_features
        }
        
        if language:
            payload["language"] = language
        
        response = self.session.post(f"{self.base_url}/detect", json=payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": True,
                "status_code": response.status_code,
                "detail": response.json()
            }
    
    def detect_batch(self, file_paths: list, languages: list = None, include_features: bool = False):
        """
        Detect voice from multiple files
        
        Args:
            file_paths: List of paths to MP3 files
            languages: Optional list of language codes (same length as file_paths)
            include_features: Whether to include detailed features
            
        Returns:
            Batch detection results
        """
        samples = []
        
        for idx, file_path in enumerate(file_paths):
            with open(file_path, 'rb') as f:
                audio_bytes = f.read()
            
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            
            sample = {
                "audio_data": audio_base64,
                "include_features": include_features
            }
            
            if languages and idx < len(languages):
                sample["language"] = languages[idx]
            
            samples.append(sample)
        
        payload = {"samples": samples}
        
        response = self.session.post(f"{self.base_url}/detect/batch", json=payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": True,
                "status_code": response.status_code,
                "detail": response.json()
            }


def print_result(result: dict):
    """Pretty print detection result"""
    print("\n" + "="*60)
    
    if result.get("error"):
        print(f"ERROR: {result.get('detail')}")
        return
    
    print(f"Classification: {result['classification'].upper()}")
    print(f"Confidence Score: {result['confidence_score']:.2%}")
    print(f"Language: {result['language_detected']}")
    print(f"Audio Duration: {result['audio_duration_seconds']:.2f}s")
    print(f"Processing Time: {result['processing_time_ms']:.2f}ms")
    print(f"\nExplanation:")
    print(f"  {result['explanation']}")
    
    if 'detailed_analysis' in result:
        print("\nDetailed Analysis:")
        print(f"  Features: {json.dumps(result['detailed_analysis']['features'], indent=4)}")
        print(f"  AI Indicators: {result['detailed_analysis']['ai_indicators']}")
        print(f"  Human Indicators: {result['detailed_analysis']['human_indicators']}")
    
    print("="*60)


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = VoiceDetectionClient("http://localhost:8000")
    
    # Check health
    print("Checking API health...")
    health = client.health_check()
    print(f"Status: {health['status']}")
    print(f"Supported Languages: {health['supported_languages']}")
    
    # Get language details
    print("\nGetting language details...")
    languages = client.get_supported_languages()
    for lang in languages['languages']:
        print(f"  - {lang['name']} ({lang['code']}): {lang['native_name']}")
    
    # Example 1: Detect from file
    print("\n\nExample 1: Single File Detection")
    print("-" * 60)
    
    # NOTE: Replace with actual file path
    # result = client.detect_from_file(
    #     "sample_audio.mp3",
    #     language="english",
    #     include_features=True
    # )
    # print_result(result)
    
    # Example 2: Batch detection
    print("\n\nExample 2: Batch Detection")
    print("-" * 60)
    
    # NOTE: Replace with actual file paths
    # batch_result = client.detect_batch(
    #     file_paths=["sample1.mp3", "sample2.mp3"],
    #     languages=["english", "tamil"],
    #     include_features=False
    # )
    # 
    # if not batch_result.get("error"):
    #     print(f"Total Samples: {batch_result['total_samples']}")
    #     print(f"Total Processing Time: {batch_result['processing_time_ms']:.2f}ms")
    #     
    #     for idx, result in enumerate(batch_result['results'], 1):
    #         print(f"\nSample {idx}:")
    #         print_result(result)
    
    print("\n\nTo test with actual audio files:")
    print("1. Place MP3 files in the same directory")
    print("2. Uncomment the example code above")
    print("3. Replace file paths with your actual file names")
    print("4. Run: python test_client.py")
