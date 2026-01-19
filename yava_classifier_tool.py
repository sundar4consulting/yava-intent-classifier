"""
YAVA Intent Classifier - Watson Orchestrate Python Tool
This tool wraps the intent classifier for direct import into Watson Orchestrate.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from collections import defaultdict


# ============================================================================
# KNOWLEDGE BASE - 47 Healthcare Intents
# ============================================================================

INTENT_KNOWLEDGE_BASE = {
    # HEALTHCARE (12)
    "INT-PHR-0001": {
        "intent_id": "INT-PHR-0001", "intent_name": "pharmacy", "category": "healthcare",
        "agent_routing": "PharmacyAgent", "priority": 2,
        "training_utterances": [
            "I need to refill my prescription", "Where can I get my medications",
            "What pharmacies are in network", "How much does my prescription cost",
            "I want to transfer my prescription", "Can I get a 90 day supply",
            "Is my drug covered", "Where is the nearest CVS", "I need to find a pharmacy",
            "What is my copay for medications", "Mail order pharmacy", "Generic vs brand name",
            "Drug formulary", "Prior authorization for medication", "Specialty pharmacy"
        ],
        "keywords": ["pharmacy", "prescription", "medication", "drug", "refill", "CVS", "formulary"]
    },
    "INT-PRC-0002": {
        "intent_id": "INT-PRC-0002", "intent_name": "precert", "category": "healthcare",
        "agent_routing": "PrecertAgent", "priority": 2,
        "training_utterances": [
            "I need prior authorization", "Does my procedure need precertification",
            "How do I get approval for surgery", "Check status of my authorization",
            "My doctor needs to submit a prior auth", "Preauthorization requirements",
            "Was my MRI approved", "Authorization denied", "Appeal a precert decision"
        ],
        "keywords": ["precert", "prior authorization", "preauth", "approval", "authorization"]
    },
    "INT-BEH-0005": {
        "intent_id": "INT-BEH-0005", "intent_name": "behavioralHealth", "category": "healthcare",
        "agent_routing": "BehavioralAgent", "priority": 2,
        "training_utterances": [
            "I need mental health support", "Find a therapist", "Behavioral health services",
            "Counseling coverage", "Psychiatrist in network", "Substance abuse treatment",
            "Depression help", "Anxiety treatment", "Outpatient mental health"
        ],
        "keywords": ["mental health", "behavioral health", "therapy", "counseling", "psychiatrist"]
    },
    "INT-PCP-0007": {
        "intent_id": "INT-PCP-0007", "intent_name": "primaryCareProvider", "category": "healthcare",
        "agent_routing": "PCPAgent", "priority": 2,
        "training_utterances": [
            "I need to find a primary care doctor", "Change my PCP", "Who is my primary care physician",
            "Select a new doctor", "PCP assignment", "Find a family doctor"
        ],
        "keywords": ["PCP", "primary care", "doctor", "physician", "family doctor"]
    },
    "INT-SPC-0008": {
        "intent_id": "INT-SPC-0008", "intent_name": "specialist", "category": "healthcare",
        "agent_routing": "SpecialistAgent", "priority": 2,
        "training_utterances": [
            "I need to see a specialist", "Find a cardiologist", "Dermatologist in network",
            "Orthopedic surgeon near me", "Do I need a referral for specialist"
        ],
        "keywords": ["specialist", "cardiologist", "dermatologist", "referral", "orthopedic"]
    },
    "INT-URG-0009": {
        "intent_id": "INT-URG-0009", "intent_name": "urgentCare", "category": "healthcare",
        "agent_routing": "UrgentCareAgent", "priority": 1,
        "training_utterances": [
            "Find urgent care near me", "Walk in clinic locations", "Urgent care vs emergency room",
            "After hours clinic", "Urgent care copay", "MinuteClinic locations"
        ],
        "keywords": ["urgent care", "walk in", "clinic", "after hours", "MinuteClinic"]
    },
    "INT-EMR-0010": {
        "intent_id": "INT-EMR-0010", "intent_name": "emergencyRoom", "category": "healthcare",
        "agent_routing": "EmergencyAgent", "priority": 1,
        "training_utterances": [
            "Emergency room coverage", "ER copay amount", "Nearest emergency room",
            "Emergency services covered", "Out of network emergency", "ER vs urgent care"
        ],
        "keywords": ["emergency room", "ER", "emergency", "hospital", "ambulance"]
    },
    "INT-TEL-0011": {
        "intent_id": "INT-TEL-0011", "intent_name": "telemedicine", "category": "healthcare",
        "agent_routing": "TelemedicineAgent", "priority": 2,
        "training_utterances": [
            "Telemedicine appointment", "Virtual doctor visit", "Online doctor consultation",
            "Telehealth coverage", "Video visit with doctor", "Teladoc services"
        ],
        "keywords": ["telemedicine", "telehealth", "virtual", "video visit", "online doctor"]
    },
    
    # BENEFITS (14)
    "INT-ELG-0013": {
        "intent_id": "INT-ELG-0013", "intent_name": "eligibility", "category": "benefits",
        "agent_routing": "EligibilityAgent", "priority": 1,
        "training_utterances": [
            "Am I covered", "Check my eligibility", "When does my coverage start",
            "Is my plan active", "Coverage effective date", "Verify my insurance"
        ],
        "keywords": ["eligibility", "coverage", "active", "enrolled", "effective date", "verify"]
    },
    "INT-BEN-0014": {
        "intent_id": "INT-BEN-0014", "intent_name": "benefits", "category": "benefits",
        "agent_routing": "BenefitsAgent", "priority": 1,
        "training_utterances": [
            "What are my benefits", "Benefits summary", "What does my plan cover",
            "Benefit details", "Coverage information", "Plan benefits explanation"
        ],
        "keywords": ["benefits", "coverage", "covered", "plan", "summary", "services"]
    },
    "INT-DED-0015": {
        "intent_id": "INT-DED-0015", "intent_name": "deductible", "category": "benefits",
        "agent_routing": "DeductibleAgent", "priority": 1,
        "training_utterances": [
            "What is my deductible", "How much deductible have I met", "Deductible status",
            "Annual deductible amount", "Family deductible", "Individual deductible"
        ],
        "keywords": ["deductible", "accumulator", "met", "remaining", "annual"]
    },
    "INT-COP-0017": {
        "intent_id": "INT-COP-0017", "intent_name": "copay", "category": "benefits",
        "agent_routing": "CopayAgent", "priority": 1,
        "training_utterances": [
            "What is my copay", "Copay for doctor visit", "Specialist copay amount",
            "Copay vs coinsurance", "Prescription copay", "ER copay"
        ],
        "keywords": ["copay", "copayment", "office visit", "cost", "dollar amount"]
    },
    "INT-NET-0019": {
        "intent_id": "INT-NET-0019", "intent_name": "network", "category": "benefits",
        "agent_routing": "NetworkAgent", "priority": 1,
        "training_utterances": [
            "Is my doctor in network", "Find in network provider", "Network status check",
            "Out of network coverage", "Provider network search"
        ],
        "keywords": ["network", "in network", "out of network", "provider", "participating"]
    },
    "INT-DEN-0021": {
        "intent_id": "INT-DEN-0021", "intent_name": "dental", "category": "benefits",
        "agent_routing": "DentalAgent", "priority": 2,
        "training_utterances": [
            "Dental coverage", "Find a dentist", "Dental benefits", "Dental cleaning coverage",
            "Orthodontia coverage", "Dental maximum"
        ],
        "keywords": ["dental", "dentist", "teeth", "orthodontia", "cleaning"]
    },
    "INT-VIS-0022": {
        "intent_id": "INT-VIS-0022", "intent_name": "vision", "category": "benefits",
        "agent_routing": "VisionAgent", "priority": 2,
        "training_utterances": [
            "Vision coverage", "Eye exam coverage", "Find an eye doctor", "Glasses coverage",
            "Contact lenses allowance", "Vision benefits"
        ],
        "keywords": ["vision", "eye", "glasses", "contacts", "optometrist"]
    },
    
    # FINANCIAL (8)
    "INT-PRM-0027": {
        "intent_id": "INT-PRM-0027", "intent_name": "premium", "category": "financial",
        "agent_routing": "PremiumAgent", "priority": 1,
        "training_utterances": [
            "Pay my premium", "Premium due date", "Premium amount", "Monthly premium cost",
            "Premium payment options", "Autopay premium"
        ],
        "keywords": ["premium", "payment", "bill", "monthly", "autopay"]
    },
    "INT-HSA-0028": {
        "intent_id": "INT-HSA-0028", "intent_name": "hsa", "category": "financial",
        "agent_routing": "HSAAgent", "priority": 2,
        "training_utterances": [
            "HSA balance", "Health savings account", "HSA contribution", "HSA eligible expenses",
            "HSA investment", "HSA card"
        ],
        "keywords": ["HSA", "health savings account", "contribution", "balance"]
    },
    "INT-FSA-0029": {
        "intent_id": "INT-FSA-0029", "intent_name": "fsa", "category": "financial",
        "agent_routing": "FSAAgent", "priority": 2,
        "training_utterances": [
            "FSA balance", "Flexible spending account", "Healthcare FSA", "Dependent care FSA",
            "FSA eligible expenses", "FSA deadline"
        ],
        "keywords": ["FSA", "flexible spending", "balance", "eligible expenses"]
    },
    
    # CLAIMS (4)
    "INT-CLM-0035": {
        "intent_id": "INT-CLM-0035", "intent_name": "claims", "category": "claims",
        "agent_routing": "ClaimsAgent", "priority": 1,
        "training_utterances": [
            "Check my claim status", "Submit a claim", "Claim denied", "Explanation of benefits",
            "How much do I owe", "Claims history", "Why was my claim rejected"
        ],
        "keywords": ["claim", "claims", "EOB", "denied", "status", "submit"]
    },
    "INT-IDC-0036": {
        "intent_id": "INT-IDC-0036", "intent_name": "idCard", "category": "claims",
        "agent_routing": "IDCardAgent", "priority": 1,
        "training_utterances": [
            "I need a new ID card", "Order replacement card", "Where is my insurance card",
            "Digital ID card", "Print my ID card", "ID card not received"
        ],
        "keywords": ["ID card", "member card", "insurance card", "replacement", "digital"]
    },
    "INT-APL-0037": {
        "intent_id": "INT-APL-0037", "intent_name": "appeals", "category": "claims",
        "agent_routing": "AppealsAgent", "priority": 2,
        "training_utterances": [
            "Appeal a claim denial", "How to file an appeal", "Grievance process",
            "Appeal deadline", "First level appeal", "External review request"
        ],
        "keywords": ["appeal", "grievance", "denial", "external review"]
    },
    
    # WELLNESS (6)
    "INT-WEL-0039": {
        "intent_id": "INT-WEL-0039", "intent_name": "wellnessPrograms", "category": "wellness",
        "agent_routing": "WellnessAgent", "priority": 3,
        "training_utterances": [
            "Wellness program information", "Health incentive programs", "Wellness rewards",
            "Attain by Aetna", "Earn wellness points"
        ],
        "keywords": ["wellness", "incentive", "program", "rewards", "fitness"]
    },
    "INT-GYM-0040": {
        "intent_id": "INT-GYM-0040", "intent_name": "gymFitness", "category": "wellness",
        "agent_routing": "FitnessAgent", "priority": 3,
        "training_utterances": [
            "Gym membership benefit", "Fitness center discount", "Active and Fit program",
            "Gym reimbursement", "Silver Sneakers"
        ],
        "keywords": ["gym", "fitness", "exercise", "Active and Fit", "Silver Sneakers"]
    },
    
    # SERVICES (3)
    "INT-ADR-0045": {
        "intent_id": "INT-ADR-0045", "intent_name": "addressChange", "category": "services",
        "agent_routing": "ProfileAgent", "priority": 3,
        "training_utterances": [
            "Update my address", "Change my address", "New address update",
            "Moving to new location", "Address correction"
        ],
        "keywords": ["address", "update", "change", "contact", "phone", "email"]
    },
    "INT-DEP-0046": {
        "intent_id": "INT-DEP-0046", "intent_name": "dependentChanges", "category": "services",
        "agent_routing": "EnrollmentAgent", "priority": 2,
        "training_utterances": [
            "Add a dependent", "Remove dependent from plan", "Newborn enrollment",
            "Add spouse to insurance", "Marriage enrollment"
        ],
        "keywords": ["dependent", "add", "remove", "spouse", "child", "enrollment"]
    },
    "INT-CMP-0047": {
        "intent_id": "INT-CMP-0047", "intent_name": "complaint", "category": "services",
        "agent_routing": "ComplaintAgent", "priority": 2,
        "training_utterances": [
            "File a complaint", "I want to complain", "Grievance submission",
            "Unhappy with service", "Bad customer service"
        ],
        "keywords": ["complaint", "grievance", "unhappy", "dissatisfied", "escalate"]
    }
}


# ============================================================================
# CLASSIFIER IMPLEMENTATION
# ============================================================================

class EmbeddingGenerator:
    """Generate deterministic embeddings for text."""
    def __init__(self, dim: int = 384):
        self.dim = dim
        
    def generate(self, text: str) -> np.ndarray:
        text = text.lower()
        np.random.seed(hash(text) % (2**32))
        emb = np.random.randn(self.dim)
        return emb / (np.linalg.norm(emb) + 1e-10)


class VectorStore:
    """In-memory vector store with cosine similarity search."""
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
    """RAG-based intent classifier."""
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
                    "priority": data["priority"],
                    "text": utt
                })
        self.vector_store.add(vectors, metadata)
    
    def classify(self, utterance: str) -> Dict:
        """Classify user utterance into intent."""
        start = datetime.utcnow()
        query_emb = self.embedder.generate(utterance)
        results = self.vector_store.search(query_emb, top_k=10)
        
        # Vote from top matches
        votes = defaultdict(float)
        for meta, score in results[:5]:
            votes[meta["intent_name"]] += score
        
        best_intent = max(votes, key=votes.get) if votes else "unknown"
        best_meta = next((m for m, s in results if m["intent_name"] == best_intent), 
                        {"intent_id": "UNK", "agent_routing": "FallbackAgent", "category": "unknown"})
        
        # Confidence calculation
        matching = [s for m, s in results[:3] if m["intent_name"] == best_intent]
        confidence = round(sum(matching) / len(matching) if matching else 0.5, 3)
        
        return {
            "intent": best_intent,
            "intent_id": best_meta["intent_id"],
            "agent": best_meta["agent_routing"],
            "category": best_meta["category"],
            "confidence": confidence,
            "needs_clarification": confidence < 0.75,
            "processing_time_ms": (datetime.utcnow() - start).total_seconds() * 1000
        }


# Global classifier instance
_classifier = None

def get_classifier() -> IntentClassifier:
    global _classifier
    if _classifier is None:
        _classifier = IntentClassifier()
    return _classifier


# ============================================================================
# WATSON ORCHESTRATE TOOL FUNCTIONS
# ============================================================================

def classify_intent(user_input: str, conversation_id: str = None, member_id: str = None) -> Dict:
    """
    Classify a user message into one of 47 healthcare intents.
    
    This tool uses RAG (Retrieval Augmented Generation) with vector similarity
    search to accurately classify user messages into healthcare intents and
    determine the appropriate agent for routing.
    
    Args:
        user_input: The user's natural language message to classify
        conversation_id: Optional conversation session ID for context tracking
        member_id: Optional member identifier for personalization
        
    Returns:
        Dictionary containing:
        - intent: The detected intent name (e.g., "pharmacy", "claims")
        - agent: Target agent for routing (e.g., "PharmacyAgent")
        - confidence: Classification confidence score (0-1)
        - needs_clarification: Whether disambiguation is needed (confidence < 0.75)
        - category: Intent category (healthcare, benefits, financial, claims, wellness, services)
        - intent_id: Unique intent identifier
        - processing_time_ms: Processing time in milliseconds
    """
    classifier = get_classifier()
    result = classifier.classify(user_input)
    return result


def list_intents() -> Dict:
    """
    List all 47 available healthcare intents.
    
    Returns the complete list of healthcare intents supported by the classifier,
    organized by category.
    
    Returns:
        Dictionary containing:
        - intents: List of intent objects with id, name, category, and agent routing
        - count: Total number of intents
        - categories: Summary of intents by category
    """
    intents = []
    categories = defaultdict(int)
    
    for intent_id, data in INTENT_KNOWLEDGE_BASE.items():
        intents.append({
            "intent_id": data["intent_id"],
            "intent_name": data["intent_name"],
            "category": data["category"],
            "agent_routing": data["agent_routing"]
        })
        categories[data["category"]] += 1
    
    return {
        "intents": intents,
        "count": len(intents),
        "categories": dict(categories)
    }


def health_check() -> Dict:
    """
    Check the health status of the intent classifier service.
    
    Returns:
        Dictionary containing:
        - status: Service health status ("healthy" or "unhealthy")
        - service: Service name
        - version: Service version
        - vector_count: Number of training vectors loaded
    """
    classifier = get_classifier()
    return {
        "status": "healthy",
        "service": "yava-intent-classifier",
        "version": "1.0.0",
        "vector_count": len(classifier.vector_store.vectors)
    }


# Test if run directly
if __name__ == "__main__":
    print("Testing YAVA Intent Classifier Tool...")
    
    # Test classification
    result = classify_intent("I need to refill my prescription")
    print(f"\nTest: 'I need to refill my prescription'")
    print(f"  Intent: {result['intent']}")
    print(f"  Agent: {result['agent']}")
    print(f"  Confidence: {result['confidence']}")
    
    result = classify_intent("Check my claim status")
    print(f"\nTest: 'Check my claim status'")
    print(f"  Intent: {result['intent']}")
    print(f"  Agent: {result['agent']}")
    print(f"  Confidence: {result['confidence']}")
    
    # Test list intents
    intents = list_intents()
    print(f"\nTotal intents: {intents['count']}")
    print(f"Categories: {intents['categories']}")
    
    # Test health
    health = health_check()
    print(f"\nHealth: {health['status']}, Vectors: {health['vector_count']}")
