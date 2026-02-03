# Voice Detection API

A robust API system for detecting whether voice samples are AI-generated or human-generated. Supports multiple languages: Tamil, English, Hindi, Malayalam, and Telugu.

## 🎯 Features

- **Multi-language Support**: Detect AI vs human voices in 5 languages
- **High Accuracy**: Advanced feature extraction and analysis
- **RESTful API**: Easy-to-use HTTP endpoints
- **Batch Processing**: Process multiple samples in one request
- **Detailed Analysis**: Optional feature breakdown and explanations
- **Production Ready**: Docker support, logging, error handling

## 🏗️ System Architecture

```
┌─────────────────┐
│   MP3 Audio     │
│  (Base64)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Audio          │
│  Processor      │
│  - Decode MP3   │
│  - Normalize    │
│  - Preprocess   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Feature        │
│  Extraction     │
│  - Spectral     │
│  - Prosodic     │
│  - Temporal     │
│  - Statistical  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Detection      │
│  Engine         │
│  - AI Score     │
│  - Confidence   │
│  - Explanation  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  JSON Response  │
└─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- FFmpeg (for audio processing)

### Installation

1. **Clone or download the project**

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Install FFmpeg** (if not already installed)
   - Ubuntu/Debian: `sudo apt-get install ffmpeg`
   - macOS: `brew install ffmpeg`
   - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

4. **Run the API**
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Using Docker

```bash
# Build and run
docker-compose up --build

# Or using Docker directly
docker build -t voice-detection-api .
docker run -p 8000:8000 voice-detection-api
```

## 📚 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "supported_languages": ["tamil", "english", "hindi", "malayalam", "telugu"],
  "timestamp": "2026-02-02T10:30:00.000Z"
}
```

#### 2. Detect Voice
```http
POST /detect
```

**Request Body:**
```json
{
  "audio_data": "BASE64_ENCODED_MP3_DATA",
  "language": "english",
  "include_features": false
}
```

**Parameters:**
- `audio_data` (required): Base64-encoded MP3 file
- `language` (optional): Language code - "tamil", "english", "hindi", "malayalam", or "telugu"
- `include_features` (optional): Include detailed feature analysis (default: false)

**Response:**
```json
{
  "classification": "ai_generated",
  "confidence_score": 0.8734,
  "explanation": "The audio sample is classified as AI-generated with 87.3% confidence. Analysis of the english speech revealed: uniform spectral distribution, minimal pitch variation, consistent amplitude. These patterns are typical of synthetic voice generation systems.",
  "language_detected": "english",
  "processing_time_ms": 245.67,
  "audio_duration_seconds": 8.5,
  "timestamp": "2026-02-02T10:30:00.000Z"
}
```

**With Features:**
```json
{
  "classification": "human_generated",
  "confidence_score": 0.7234,
  "explanation": "...",
  "language_detected": "tamil",
  "processing_time_ms": 312.45,
  "audio_duration_seconds": 12.3,
  "detailed_analysis": {
    "features": {
      "spectral_flatness": 0.1234,
      "harmonic_ratio": 0.6789,
      "jitter": 0.0067,
      "shimmer": 0.0543,
      "zcr_std": 0.0234,
      "mfcc_variance": 3.4567,
      "energy_entropy": 4.2341,
      "dynamic_range": 18.45
    },
    "ai_indicators": [
      "Strong harmonic structure"
    ],
    "human_indicators": [
      "Natural pitch variation",
      "Natural amplitude variation",
      "Dynamic energy distribution"
    ]
  },
  "timestamp": "2026-02-02T10:30:00.000Z"
}
```

#### 3. Batch Detection
```http
POST /detect/batch
```

**Request Body:**
```json
{
  "samples": [
    {
      "audio_data": "BASE64_ENCODED_MP3_DATA_1",
      "language": "english"
    },
    {
      "audio_data": "BASE64_ENCODED_MP3_DATA_2",
      "language": "tamil"
    }
  ]
}
```

**Response:**
```json
{
  "results": [
    {
      "classification": "ai_generated",
      "confidence_score": 0.8734,
      "explanation": "...",
      "language_detected": "english",
      "processing_time_ms": 245.67,
      "audio_duration_seconds": 8.5,
      "timestamp": "2026-02-02T10:30:00.000Z"
    },
    {
      "classification": "human_generated",
      "confidence_score": 0.7123,
      "explanation": "...",
      "language_detected": "tamil",
      "processing_time_ms": 298.34,
      "audio_duration_seconds": 10.2,
      "timestamp": "2026-02-02T10:30:00.000Z"
    }
  ],
  "total_samples": 2,
  "processing_time_ms": 567.89
}
```

#### 4. Get Supported Languages
```http
GET /languages
```

**Response:**
```json
{
  "languages": [
    {
      "code": "tamil",
      "name": "Tamil",
      "native_name": "தமிழ்"
    },
    {
      "code": "english",
      "name": "English",
      "native_name": "English"
    },
    {
      "code": "hindi",
      "name": "Hindi",
      "native_name": "हिन्दी"
    },
    {
      "code": "malayalam",
      "name": "Malayalam",
      "native_name": "മലയാളം"
    },
    {
      "code": "telugu",
      "name": "Telugu",
      "native_name": "తెలుగు"
    }
  ],
  "total": 5
}
```

## 💻 Usage Examples

### Python Example

```python
import requests
import base64

# Read MP3 file
with open("sample.mp3", "rb") as f:
    audio_bytes = f.read()

# Encode to base64
audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')

# Make request
response = requests.post(
    "http://localhost:8000/detect",
    json={
        "audio_data": audio_base64,
        "language": "english",
        "include_features": True
    }
)

result = response.json()
print(f"Classification: {result['classification']}")
print(f"Confidence: {result['confidence_score']:.2%}")
print(f"Explanation: {result['explanation']}")
```

### cURL Example

```bash
# Encode MP3 file to base64
BASE64_AUDIO=$(base64 -w 0 sample.mp3)

# Make request
curl -X POST "http://localhost:8000/detect" \
  -H "Content-Type: application/json" \
  -d "{
    \"audio_data\": \"$BASE64_AUDIO\",
    \"language\": \"english\",
    \"include_features\": false
  }"
```

### JavaScript Example

```javascript
// Read file
const file = document.getElementById('audioFile').files[0];
const reader = new FileReader();

reader.onload = async (e) => {
  const base64Audio = e.target.result.split(',')[1];
  
  const response = await fetch('http://localhost:8000/detect', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      audio_data: base64Audio,
      language: 'english',
      include_features: false
    })
  });
  
  const result = await response.json();
  console.log('Classification:', result.classification);
  console.log('Confidence:', result.confidence_score);
};

reader.readAsDataURL(file);
```

## 🔬 Detection Features

The system analyzes multiple acoustic features:

### 1. Spectral Features
- **Spectral Flatness**: Uniformity of the frequency spectrum
- **Spectral Centroid**: "Brightness" of the sound
- **Spectral Rolloff**: Frequency below which 85% of energy is contained

### 2. Prosodic Features
- **Jitter**: Pitch period variation
- **Shimmer**: Amplitude variation
- AI voices typically have lower jitter and shimmer

### 3. Temporal Features
- **Zero-Crossing Rate (ZCR)**: Rate of sign changes
- **ZCR Standard Deviation**: Consistency of articulation

### 4. Harmonic Features
- **Harmonic-to-Noise Ratio**: Clarity of harmonic content
- AI voices often have higher harmonic ratios

### 5. Statistical Features
- **MFCC Variance**: Mel-frequency cepstral coefficient variation
- **Energy Entropy**: Distribution of energy over time
- **Kurtosis & Skewness**: Statistical distribution measures

## 🎛️ Configuration

Edit thresholds in `voice_detector.py`:

```python
self.thresholds = {
    "spectral_flatness_threshold": 0.15,
    "harmonic_ratio_threshold": 0.75,
    "zero_crossing_rate_std": 0.02,
    "jitter_threshold": 0.005,
    "shimmer_threshold": 0.05,
    "mel_cepstral_distortion": 2.5,
}
```

## 📊 API Limits

- **Audio Duration**: 0.5s - 300s (5 minutes)
- **File Format**: MP3 only
- **Batch Size**: Maximum 10 samples per request
- **Sample Rate**: Automatically resampled to 16kHz

## 🔒 Error Handling

The API returns appropriate HTTP status codes:

- `200`: Success
- `400`: Bad Request (invalid audio, parameters)
- `422`: Validation Error
- `500`: Internal Server Error

**Error Response:**
```json
{
  "detail": "Error description here"
}
```

## 🧪 Testing

Use the provided test client:

```bash
python test_client.py
```

Or test with your own audio:

```python
from test_client import VoiceDetectionClient

client = VoiceDetectionClient()
result = client.detect_from_file("your_audio.mp3", language="english")
print(result)
```

## 📝 Logging

Logs are written to stdout with the format:
```
2026-02-02 10:30:00 - voice_detector - INFO - Starting detection for english audio
```

## 🚢 Deployment

### Production Deployment

1. **Set environment variables:**
```bash
export WORKERS=4
export HOST=0.0.0.0
export PORT=8000
```

2. **Run with Gunicorn:**
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

3. **Or use Docker:**
```bash
docker-compose up -d
```

### API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🛠️ Technology Stack

- **FastAPI**: Modern web framework
- **NumPy**: Numerical computing
- **SciPy**: Signal processing
- **Pydub**: Audio file handling
- **Uvicorn**: ASGI server

## 📄 License

This project is provided as-is for educational and commercial use.

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Enhanced language detection
- Additional audio features
- Machine learning model integration
- Performance optimization

## 📞 Support

For issues or questions, please refer to the API documentation at `/docs` endpoint.

---

**Built for accurate AI voice detection across multiple languages** 🎤✨
