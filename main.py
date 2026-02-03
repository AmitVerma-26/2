"""
Voice Detection API - Main Application
Detects AI-generated vs Human-generated voice samples in multiple languages
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Literal, Optional, Dict, List
import base64
import io
import logging
from datetime import datetime
import uvicorn

# Import detection modules
from voice_detector import VoiceDetector
from audio_processor import AudioProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Voice Detection API",
    description="API for detecting AI-generated vs human-generated voice samples",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize detector and processor
detector = VoiceDetector()
audio_processor = AudioProcessor()


# Request/Response Models
class VoiceDetectionRequest(BaseModel):
    """Request model for voice detection"""
    audio_data: str = Field(..., description="Base64-encoded MP3 audio file")
    language: Optional[Literal["tamil", "english", "hindi", "malayalam", "telugu"]] = Field(
        None, 
        description="Language of the audio sample (optional, will be auto-detected if not provided)"
    )
    include_features: bool = Field(
        False, 
        description="Include detailed audio features in response"
    )
    
    @validator('audio_data')
    def validate_base64(cls, v):
        """Validate that the audio_data is valid base64"""
        try:
            base64.b64decode(v)
            return v
        except Exception:
            raise ValueError("Invalid base64 encoding")


class VoiceDetectionResponse(BaseModel):
    """Response model for voice detection"""
    classification: Literal["ai_generated", "human_generated"]
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0 and 1")
    explanation: str
    language_detected: str
    processing_time_ms: float
    audio_duration_seconds: float
    detailed_analysis: Optional[Dict] = None
    timestamp: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    supported_languages: List[str]
    timestamp: str


class BatchDetectionRequest(BaseModel):
    """Request model for batch detection"""
    samples: List[VoiceDetectionRequest] = Field(..., max_items=10)


class BatchDetectionResponse(BaseModel):
    """Response model for batch detection"""
    results: List[VoiceDetectionResponse]
    total_samples: int
    processing_time_ms: float


# API Endpoints
@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - API information"""
    return {
        "status": "operational",
        "version": "1.0.0",
        "supported_languages": ["tamil", "english", "hindi", "malayalam", "telugu"],
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "supported_languages": ["tamil", "english", "hindi", "malayalam", "telugu"],
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/detect", response_model=VoiceDetectionResponse)
async def detect_voice(request: VoiceDetectionRequest):
    """
    Main endpoint for voice detection
    
    Analyzes an audio sample and determines if it's AI-generated or human-generated
    """
    start_time = datetime.now()
    
    try:
        # Decode base64 audio
        logger.info("Processing voice detection request")
        audio_bytes = base64.b64decode(request.audio_data)
        
        # Process audio
        audio_data, sample_rate, duration = audio_processor.process_audio(audio_bytes)
        
        # Detect language if not provided
        language = request.language
        if language is None:
            language = detector.detect_language(audio_data, sample_rate)
            logger.info(f"Language auto-detected: {language}")
        
        # Perform detection
        result = detector.detect(
            audio_data=audio_data,
            sample_rate=sample_rate,
            language=language,
            include_features=request.include_features
        )
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Build response
        response = {
            "classification": result["classification"],
            "confidence_score": result["confidence_score"],
            "explanation": result["explanation"],
            "language_detected": language,
            "processing_time_ms": round(processing_time, 2),
            "audio_duration_seconds": round(duration, 2),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if request.include_features and "detailed_analysis" in result:
            response["detailed_analysis"] = result["detailed_analysis"]
        
        logger.info(f"Detection completed: {result['classification']} ({result['confidence_score']:.2f})")
        return response
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing audio: {str(e)}"
        )


@app.post("/detect/batch", response_model=BatchDetectionResponse)
async def detect_batch(request: BatchDetectionRequest):
    """
    Batch endpoint for processing multiple voice samples
    
    Maximum 10 samples per request
    """
    start_time = datetime.now()
    results = []
    
    try:
        for idx, sample in enumerate(request.samples):
            logger.info(f"Processing batch sample {idx + 1}/{len(request.samples)}")
            result = await detect_voice(sample)
            results.append(result)
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return {
            "results": results,
            "total_samples": len(results),
            "processing_time_ms": round(processing_time, 2)
        }
        
    except Exception as e:
        logger.error(f"Batch processing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing batch: {str(e)}"
        )


@app.get("/languages")
async def get_supported_languages():
    """Get list of supported languages with details"""
    return {
        "languages": [
            {"code": "tamil", "name": "Tamil", "native_name": "தமிழ்"},
            {"code": "english", "name": "English", "native_name": "English"},
            {"code": "hindi", "name": "Hindi", "native_name": "हिन्दी"},
            {"code": "malayalam", "name": "Malayalam", "native_name": "മലയാളം"},
            {"code": "telugu", "name": "Telugu", "native_name": "తెలుగు"}
        ],
        "total": 5
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
