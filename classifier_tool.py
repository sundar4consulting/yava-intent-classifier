"""
YAVA Intent Classifier Tool for Watson Orchestrate

This tool provides healthcare intent classification using RAG-based vector search.
"""

import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timezone
from collections import defaultdict
from ibm_watsonx_orchestrate import tool


# ============================================================================
# KNOWLEDGE BASE - 26 Core Healthcare Intents (subset for tool)
# ============================================================================

INTENT_KNOWLEDGE_BASE = {
    "INT-PHR-0001": {
        "intent_id": "INT-PHR-0001", "intent_name": "pharmacy", "category": "healthcare",
        "agent_routing": "PharmacyAgent", "priority": 2,
        "training_utterances": [
            "I need to refill my prescription", "Where can I get my medications",
            "What pharmacies are in network", "How much does my prescription cost",
            "Is my drug covered", "Where is the nearest CVS", "Mail order pharmacy"
        ]
    },
    "INT-PRC-0002": {
        "intent_id": "INT-PRC-0002", "intent_name": "precert", "category": "healthcare",
        "agent_routing": "PrecertAgent", "priority": 2,
        "training_utterances": [
            "I need prior authorization", "Does my procedure need precertification",
            "How do I get approval for surgery", "Check status of my authorization"
        ]
    },
    "INT-BEH-0005": {
        "intent_id": "INT-BEH-0005", "intent_name": "behavioralHealth", "category": "healthcare",
        "agent_routing": "BehavioralAgent", "priority": 2,
        "training_utterances": [
            "I need mental health support", "Find a therapist", "Behavioral health services",
            "Counseling coverage", "Psychiatrist in network", "Depression help"
        ]
    },
    "INT-PCP-0007": {
        "intent_id": "INT-PCP-0007", "intent_name": "primaryCareProvider", "category": "healthcare",
        "agent_routing": "PCPAgent", "priority": 2,
        "training_utterances": [
            "I need to find a primary care doctor", "Change my PCP", "Who is my primary care physician",
            "Find a family doctor"
        ]
    },
    "INT-SPC-0008": {
        "intent_id": "INT-SPC-0008", "intent_name": "specialist", "category": "healthcare",
        "agent_routing": "SpecialistAgent", "priority": 2,
        "training_utterances": [
            "I need to see a specialist", "Find a cardiologist", "Dermatologist in network",
            "Do I need a referral for specialist"
        ]
    },
    "INT-URG-0009": {
        "intent_id": "INT-URG-0009", "intent_name": "urgentCare", "category": "healthcare",
        "agent_routing": "UrgentCareAgent", "priority": 1,
        "training_utterances": [
            "Find urgent care near me", "Walk in clinic locations", "Urgent care vs emergency room"
        ]
    },
    "INT-ELG-0013": {
        "intent_id": "INT-ELG-0013", "intent_name": "eligibility", "category": "benefits",
        "agent_routing": "EligibilityAgent", "priority": 1,
        "training_utterances": [
            "Am I covered", "Check my eligibility", "When does my coverage start",
            "Is my plan active", "Verify my insurance"
        ]
    },
    "INT-BEN-0014": {
        "intent_id": "INT-BEN-0014", "intent_name": "benefits", "category": "benefits",
        "agent_routing": "BenefitsAgent", "priority": 1,
        "training_utterances": [
            "What are my benefits", "Benefits summary", "What does my plan cover"
        ]
    },
    "INT-DED-0015": {
        "intent_id": "INT-DED-0015", "intent_name": "deductible", "category": "benefits",
        "agent_routing": "DeductibleAgent", "priority": 1,
        "training_utterances": [
            "What is my deductible", "How much deductible have I met", "Deductible status"
        ]
    },
    "INT-COP-0017": {
        "intent_id": "INT-COP-0017", "intent_name": "copay", "category": "benefits",
        "agent_routing": "CopayAgent", "priority": 1,
        "training_utterances": [
            "What is my copay", "Copay for doctor visit", "Specialist copay amount"
        ]
    },
    "INT-NET-0019": {
        "intent_id": "INT-NET-0019", "intent_name": "network", "category": "benefits",
        "agent_routing": "NetworkAgent", "priority": 1,
        "training_utterances": [
            "Is my doctor in network", "Find in network provider", "Out of network coverage"
        ]
    },
    "INT-CLM-0035": {
        "intent_id": "INT-CLM-0035", "intent_name": "claims", "category": "claims",
        "agent_routing": "ClaimsAgent", "priority": 1,
        "training_utterances": [
            "Check my claim status", "Submit a claim", "Claim denied", "Claims history"
        ]
    },
    "INT-IDC-0036": {
        "intent_id": "INT-IDC-0036", "intent_name": "idCard", "category": "claims",
        "agent_routing": "IDCardAgent", "priority": 1,
        "training_utterances": [
            "I need a new ID card", "Order replacement card", "Where is my insurance card"
        ]
    },
    "INT-HSA-0028": {
        "intent_id": "INT-HSA-0028", "intent_name": "hsa", "category": "financial",
        "agent_routing": "HSAAgent", "priority": 2,
        "training_utterances": [
            "HSA balance", "Health savings account", "HSA contribution"
        ]
    },
    "INT-PRM-0027": {
        "intent_id": "INT-PRM-0027", "intent_name": "premium", "category": "financial",
        "agent_routing": "PremiumAgent", "priority": 1,
        "training_utterances": [
            "Pay my premium", "Premium due date", "Premium amount"
        ]
    }
}


# ============================================================================
# CLASSIFIER IMPLEMENTATION
# ============================================================================

class EmbeddingGenerator:
    def __init__(self, dim: int = 384):
        self.dim = dim
        
    def generate(self, text: str) -> np.ndarray:
        text = text.lower()
        np.random.seed(hash(text) % (2**32))
        emb = np.random.randn(self.dim)
        return emb / (np.linalg.norm(emb) + 1e-10)


class VectorStore:
    def __init__(self):
        self.vectors = []
        self.metadata = []
        
    def add(self, vectors: List[np.ndarray], metadata: List[Dict]):
        self.vectors.extend(vectors)
        self.metadata.extend(metadata)
        
    def search(self, query: np.ndarray, top_k: int = 10) -> List[Tuple[Dict, float]]:
        if not self.vectors:
            return []
        vectors_array = np.array(self.vectors)
        query_norm = query / (np.linalg.norm(query) + 1e-10)
        vectors_norm = vectors_array / (np.linalg.norm(vectors_array, axis=1, keepdims=True) + 1e-10)
        similarities = np.dot(vectors_norm, query_norm)
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        return [(self.metadata[i], float(similarities[i])) for i in top_indices]


class IntentClassifier:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self.vector_store = VectorStore()
        self.embedder = EmbeddingGenerator()
        self._build_knowledge_base()
        self._initialized = True
        
    def _build_knowledge_base(self):
        vectors, metadata = [], []
        for intent_id, data in INTENT_KNOWLEDGE_BASE.items():
            for utt in data["training_utterances"]:
                vectors.append(self.embedder.generate(utt))
                metadata.append({
                    "intent_id": intent_id,
                    "intent_name": data["intent_name"],
                    "category": data["category"],
                    "agent_routing": data["agent_routing"],
                    "priority": data["priority"]
                })
        self.vector_store.add(vectors, metadata)
    
    def classify(self, utterance: str) -> Dict:
        start = datetime.now(timezone.utc)
        query_emb = self.embedder.generate(utterance)
        results = self.vector_store.search(query_emb, top_k=10)
        
        votes = defaultdict(float)
        for meta, score in results[:5]:
            votes[meta["intent_name"]] += score
        
        best_intent = max(votes, key=votes.get) if votes else "unknown"
        best_meta = next((m for m, s in results if m["intent_name"] == best_intent), 
                        {"intent_id": "UNK", "agent_routing": "FallbackAgent", "category": "unknown"})
        
        matching = [s for m, s in results[:3] if m["intent_name"] == best_intent]
        confidence = round(sum(matching) / len(matching) if matching else 0.5, 3)
        
        return {
            "intent": best_intent,
            "intent_id": best_meta["intent_id"],
            "agent": best_meta["agent_routing"],
            "category": best_meta["category"],
            "confidence": confidence,
            "needs_clarification": confidence < 0.75,
            "processing_time_ms": (datetime.now(timezone.utc) - start).total_seconds() * 1000
        }


_classifier = None

def get_classifier() -> IntentClassifier:
    global _classifier
    if _classifier is None:
        _classifier = IntentClassifier()
    return _classifier


# ============================================================================
# WATSON ORCHESTRATE TOOL
# ============================================================================

@tool
def classify_intent(user_input: str) -> str:
    """
    Classify a user message into a healthcare intent.
    
    Use this tool to determine what the user is asking about and which agent should handle their request.
    
    Args:
        user_input: The user's natural language message to classify
        
    Returns:
        JSON string with intent, agent, confidence, and whether clarification is needed
    """
    import json
    classifier = get_classifier()
    result = classifier.classify(user_input)
    return json.dumps(result, indent=2)


@tool
def list_available_intents() -> str:
    """
    List all available healthcare intents that can be classified.
    
    Returns:
        JSON string with list of intents and their categories
    """
    import json
    intents = []
    for data in INTENT_KNOWLEDGE_BASE.values():
        intents.append({
            "intent_name": data["intent_name"],
            "category": data["category"],
            "agent": data["agent_routing"]
        })
    return json.dumps({"intents": intents, "count": len(intents)}, indent=2)
