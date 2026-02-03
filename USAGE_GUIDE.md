# Voice Detection API - Complete Usage Guide

## Table of Contents
1. [Quick Start](#quick-start)
2. [API Endpoints](#api-endpoints)
3. [Request/Response Formats](#request-response-formats)
4. [Code Examples](#code-examples)
5. [Error Handling](#error-handling)
6. [Best Practices](#best-practices)

---

## Quick Start

### 1. Start the API Server

```bash
# Option 1: Direct Python
python main.py

# Option 2: Using Docker
docker-compose up

# Option 3: With custom settings
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Verify API is Running

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "supported_languages": ["tamil", "english", "hindi", "malayalam", "telugu"],
  "timestamp": "2026-02-02T10:30:00.000Z"
}
```

---

## API Endpoints

### 1. Health Check
**GET** `/health`

Returns the health status of the API.

### 2. Voice Detection (Single)
**POST** `/detect`

Analyzes a single audio sample.

### 3. Voice Detection (Batch)
**POST** `/detect/batch`

Analyzes multiple audio samples (max 10 per request).

### 4. Supported Languages
**GET** `/languages`

Returns list of supported languages with details.

---

## Request/Response Formats

### Single Detection Request

```json
{
  "audio_data": "BASE64_ENCODED_MP3",
  "language": "english",        // Optional: tamil, english, hindi, malayalam, telugu
  "include_features": false     // Optional: Include detailed analysis
}
```

### Single Detection Response

```json
{
  "classification": "ai_generated",  // or "human_generated"
  "confidence_score": 0.8734,        // 0.0 to 1.0
  "explanation": "Detailed explanation of the classification...",
  "language_detected": "english",
  "processing_time_ms": 245.67,
  "audio_duration_seconds": 8.5,
  "timestamp": "2026-02-02T10:30:00.000Z"
}
```

### Batch Detection Request

```json
{
  "samples": [
    {
      "audio_data": "BASE64_ENCODED_MP3_1",
      "language": "english"
    },
    {
      "audio_data": "BASE64_ENCODED_MP3_2",
      "language": "tamil"
    }
  ]
}
```

---

## Code Examples

### Python - Basic Detection

```python
import requests
import base64

def detect_voice(audio_file_path, language="english"):
    """Detect if voice is AI-generated or human"""
    
    # Read and encode audio file
    with open(audio_file_path, 'rb') as f:
        audio_bytes = f.read()
    
    audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
    
    # Make API request
    response = requests.post(
        "http://localhost:8000/detect",
        json={
            "audio_data": audio_base64,
            "language": language,
            "include_features": False
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Classification: {result['classification']}")
        print(f"Confidence: {result['confidence_score']:.2%}")
        print(f"Explanation: {result['explanation']}")
        return result
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
        return None

# Usage
result = detect_voice("my_audio.mp3", "english")
```

### Python - Detailed Analysis

```python
import requests
import base64
import json

def detailed_voice_analysis(audio_file_path, language="english"):
    """Get detailed analysis of voice sample"""
    
    with open(audio_file_path, 'rb') as f:
        audio_bytes = f.read()
    
    audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
    
    response = requests.post(
        "http://localhost:8000/detect",
        json={
            "audio_data": audio_base64,
            "language": language,
            "include_features": True  # Request detailed features
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"Classification: {result['classification']}")
        print(f"Confidence: {result['confidence_score']:.2%}")
        
        if 'detailed_analysis' in result:
            print("\nDetailed Features:")
            features = result['detailed_analysis']['features']
            for feature, value in features.items():
                print(f"  {feature}: {value:.4f}")
            
            print(f"\nAI Indicators:")
            for indicator in result['detailed_analysis']['ai_indicators']:
                print(f"  • {indicator}")
            
            print(f"\nHuman Indicators:")
            for indicator in result['detailed_analysis']['human_indicators']:
                print(f"  • {indicator}")
        
        return result
    else:
        print(f"Error: {response.status_code}")
        return None

# Usage
analysis = detailed_voice_analysis("sample.mp3", "tamil")
```

### Python - Batch Processing

```python
import requests
import base64
from pathlib import Path

def batch_detect_voices(audio_files, languages=None):
    """Detect multiple voice samples at once"""
    
    samples = []
    
    for idx, file_path in enumerate(audio_files):
        with open(file_path, 'rb') as f:
            audio_bytes = f.read()
        
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        sample = {
            "audio_data": audio_base64,
            "include_features": False
        }
        
        # Add language if provided
        if languages and idx < len(languages):
            sample["language"] = languages[idx]
        
        samples.append(sample)
    
    # Make batch request
    response = requests.post(
        "http://localhost:8000/detect/batch",
        json={"samples": samples}
    )
    
    if response.status_code == 200:
        batch_result = response.json()
        
        print(f"Processed {batch_result['total_samples']} samples")
        print(f"Total time: {batch_result['processing_time_ms']:.2f}ms")
        
        for idx, result in enumerate(batch_result['results']):
            print(f"\nSample {idx+1}: {audio_files[idx]}")
            print(f"  Classification: {result['classification']}")
            print(f"  Confidence: {result['confidence_score']:.2%}")
        
        return batch_result
    else:
        print(f"Error: {response.status_code}")
        return None

# Usage
files = ["audio1.mp3", "audio2.mp3", "audio3.mp3"]
languages = ["english", "tamil", "hindi"]
batch_result = batch_detect_voices(files, languages)
```

### JavaScript/Node.js - Basic Detection

```javascript
const fs = require('fs');
const axios = require('axios');

async function detectVoice(audioFilePath, language = 'english') {
    try {
        // Read and encode audio file
        const audioBuffer = fs.readFileSync(audioFilePath);
        const audioBase64 = audioBuffer.toString('base64');
        
        // Make API request
        const response = await axios.post('http://localhost:8000/detect', {
            audio_data: audioBase64,
            language: language,
            include_features: false
        });
        
        const result = response.data;
        console.log(`Classification: ${result.classification}`);
        console.log(`Confidence: ${(result.confidence_score * 100).toFixed(2)}%`);
        console.log(`Explanation: ${result.explanation}`);
        
        return result;
    } catch (error) {
        console.error('Error:', error.response?.data || error.message);
        return null;
    }
}

// Usage
detectVoice('my_audio.mp3', 'english');
```

### cURL - Command Line

```bash
# Encode audio file
BASE64_AUDIO=$(base64 -w 0 audio.mp3)

# Make request
curl -X POST "http://localhost:8000/detect" \
  -H "Content-Type: application/json" \
  -d "{
    \"audio_data\": \"$BASE64_AUDIO\",
    \"language\": \"english\",
    \"include_features\": false
  }" | jq .

# With detailed features
curl -X POST "http://localhost:8000/detect" \
  -H "Content-Type: application/json" \
  -d "{
    \"audio_data\": \"$BASE64_AUDIO\",
    \"language\": \"tamil\",
    \"include_features\": true
  }" | jq .
```

### Web Frontend - HTML/JavaScript

```html
<!DOCTYPE html>
<html>
<head>
    <title>Voice Detection</title>
</head>
<body>
    <h1>Voice Detection API Test</h1>
    
    <input type="file" id="audioFile" accept=".mp3">
    <select id="language">
        <option value="english">English</option>
        <option value="tamil">Tamil</option>
        <option value="hindi">Hindi</option>
        <option value="malayalam">Malayalam</option>
        <option value="telugu">Telugu</option>
    </select>
    <button onclick="detectVoice()">Detect</button>
    
    <div id="result"></div>
    
    <script>
        async function detectVoice() {
            const fileInput = document.getElementById('audioFile');
            const language = document.getElementById('language').value;
            const file = fileInput.files[0];
            
            if (!file) {
                alert('Please select an audio file');
                return;
            }
            
            // Read file as base64
            const reader = new FileReader();
            reader.onload = async (e) => {
                const base64Audio = e.target.result.split(',')[1];
                
                try {
                    const response = await fetch('http://localhost:8000/detect', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            audio_data: base64Audio,
                            language: language,
                            include_features: true
                        })
                    });
                    
                    const result = await response.json();
                    
                    document.getElementById('result').innerHTML = `
                        <h2>Result</h2>
                        <p><strong>Classification:</strong> ${result.classification}</p>
                        <p><strong>Confidence:</strong> ${(result.confidence_score * 100).toFixed(2)}%</p>
                        <p><strong>Language:</strong> ${result.language_detected}</p>
                        <p><strong>Explanation:</strong> ${result.explanation}</p>
                    `;
                } catch (error) {
                    console.error('Error:', error);
                    alert('Error detecting voice');
                }
            };
            
            reader.readAsDataURL(file);
        }
    </script>
</body>
</html>
```

---

## Error Handling

### Common Errors

#### 400 Bad Request
```json
{
  "detail": "Invalid base64 encoding"
}
```

**Solution:** Ensure audio data is properly base64-encoded

#### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "language"],
      "msg": "value is not a valid enumeration member",
      "type": "type_error.enum"
    }
  ]
}
```

**Solution:** Use valid language codes: tamil, english, hindi, malayalam, telugu

#### 500 Internal Server Error
```json
{
  "detail": "Failed to process audio file: unsupported format"
}
```

**Solution:** Ensure audio is in MP3 format

### Error Handling Example

```python
import requests
import base64

def safe_detect_voice(audio_path, language="english"):
    """Voice detection with comprehensive error handling"""
    
    try:
        # Validate file exists
        if not os.path.exists(audio_path):
            return {"error": "File not found"}
        
        # Validate file format
        if not audio_path.endswith('.mp3'):
            return {"error": "Only MP3 files are supported"}
        
        # Read and encode
        with open(audio_path, 'rb') as f:
            audio_bytes = f.read()
        
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        # Make request with timeout
        response = requests.post(
            "http://localhost:8000/detect",
            json={
                "audio_data": audio_base64,
                "language": language
            },
            timeout=30
        )
        
        # Check response
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 400:
            return {"error": "Bad request", "detail": response.json()}
        elif response.status_code == 422:
            return {"error": "Validation error", "detail": response.json()}
        else:
            return {"error": f"HTTP {response.status_code}", "detail": response.text}
    
    except requests.exceptions.Timeout:
        return {"error": "Request timeout"}
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to API"}
    except Exception as e:
        return {"error": str(e)}

# Usage
result = safe_detect_voice("audio.mp3", "english")
if "error" in result:
    print(f"Error: {result['error']}")
else:
    print(f"Classification: {result['classification']}")
```

---

## Best Practices

### 1. Audio File Preparation
- Use MP3 format
- Keep duration between 0.5s and 300s (5 minutes)
- Use clear audio with minimal background noise
- Ensure audio contains actual speech (not silence)

### 2. Language Selection
- Specify language when known for better accuracy
- Let API auto-detect if language is uncertain
- Use correct language codes: `tamil`, `english`, `hindi`, `malayalam`, `telugu`

### 3. Batch Processing
- Use batch endpoint for multiple files
- Maximum 10 samples per batch request
- Consider breaking large datasets into multiple batches

### 4. Performance Optimization
- Compress audio files before encoding
- Use lower bitrates (128kbps is sufficient)
- Cache results when processing the same file multiple times

### 5. Error Handling
- Always validate files before sending
- Implement timeout handling
- Log errors for debugging
- Provide user-friendly error messages

### 6. Security
- Validate file sizes on client side
- Implement rate limiting if exposing publicly
- Use HTTPS in production
- Never log sensitive audio content

---

## Testing the System

### Generate Test Samples

```bash
# Generate synthetic test samples
python generate_test_samples.py
```

This creates:
- 2 AI-like voice samples
- 2 human-like voice samples
- Automatically tests them with the API

### Manual Testing

```python
from test_client import VoiceDetectionClient

# Initialize client
client = VoiceDetectionClient("http://localhost:8000")

# Test health
print(client.health_check())

# Test detection
result = client.detect_from_file("audio.mp3", language="english")
print(result)
```

---

## Production Deployment Checklist

- [ ] Set environment variables
- [ ] Configure logging
- [ ] Set up monitoring
- [ ] Implement rate limiting
- [ ] Use HTTPS/TLS
- [ ] Set up load balancing (if needed)
- [ ] Configure CORS properly
- [ ] Implement authentication (if needed)
- [ ] Set up error alerting
- [ ] Document API for users

---

**For more information, visit the interactive API docs at:** `http://localhost:8000/docs`
