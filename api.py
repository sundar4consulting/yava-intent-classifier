"""
YAVA Intent Classifier - REST API
Deploy as a skill for Watson Orchestrate
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
import uvicorn
import os
import logging
from datetime import datetime
from collections import deque

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Track recent API calls (in-memory, last 100)
api_call_log = deque(maxlen=100)

# Import classifier
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.classifier import get_classifier
from src.intents.knowledge_base import get_all_intents

app = FastAPI(
    title="YAVA Intent Classifier API",
    description="Healthcare intent classification using RAG+LLM. Classifies user utterances into 47 healthcare-related intents.",
    version="1.0.0"
)

# CORS for Watson Orchestrate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class ClassifyRequest(BaseModel):
    user_input: str
    conversation_id: Optional[str] = None
    member_id: Optional[str] = None

class ClassifyResponse(BaseModel):
    intent: str
    agent: str
    confidence: float
    needs_clarification: bool
    metadata: Dict

class IntentsResponse(BaseModel):
    intents: List[Dict]
    count: int

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


@app.post("/classify", response_model=ClassifyResponse, summary="Classify user intent")
async def classify_intent(request: ClassifyRequest, req: Request):
    """
    Classify a user message into one of 47 healthcare intents.
    
    Returns the detected intent, target agent for routing, and confidence score.
    """
    try:
        # Log the API call
        call_info = {
            "timestamp": datetime.utcnow().isoformat(),
            "input": request.user_input,
            "conversation_id": request.conversation_id,
            "member_id": request.member_id,
            "source_ip": req.client.host if req.client else "unknown",
            "user_agent": req.headers.get("user-agent", "unknown")
        }
        logger.info(f"🎯 CLASSIFIER CALLED: {call_info}")
        
        classifier = get_classifier()
        session_id = request.conversation_id or f"api-{request.member_id}" or "default"
        result = classifier.classify(request.user_input, session_id)
        
        # Log result
        call_info["result"] = {
            "intent": result["intent"],
            "confidence": result["confidence"],
            "agent": result["agent_routing"]
        }
        api_call_log.append(call_info)
        logger.info(f"✅ RESULT: {result['intent']} ({result['confidence']*100:.0f}%)")
        
        return ClassifyResponse(
            intent=result["intent"],
            agent=result["agent_routing"],
            confidence=result["confidence"],
            needs_clarification=result["needs_disambiguation"],
            metadata={
                "intent_id": result["intent_id"],
                "category": result["category"],
                "processing_time_ms": result["processing_time_ms"]
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/intents", response_model=IntentsResponse, summary="List all intents")
async def list_intents():
    """
    List all 47 available healthcare intents with their metadata.
    """
    intents = get_all_intents()
    return IntentsResponse(intents=intents, count=len(intents))


@app.get("/health", response_model=HealthResponse, summary="Health check")
async def health_check():
    """
    Check API health status.
    """
    return HealthResponse(
        status="healthy",
        service="yava-intent-classifier",
        version="1.0.0"
    )


@app.get("/logs", summary="View recent API calls")
async def get_logs():
    """
    View recent classifier API calls to verify the tool is being used.
    Returns the last 100 classification requests.
    """
    return {
        "total_calls": len(api_call_log),
        "recent_calls": list(api_call_log)
    }


@app.get("/", summary="Root endpoint")
async def root():
    return {"message": "YAVA Intent Classifier API", "docs": "/docs"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
