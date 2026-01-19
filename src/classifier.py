"""
Local RAG+LLM Intent Classifier - Enhanced with:
1. Disambiguation - When confidence is low or multiple intents are close
2. Context-aware classification - Uses session history to boost relevant intents  
3. Multi-intent detection - Detects when user asks about multiple things
4. Slot filling - Extracts entities/parameters from user utterance
"""

import re
import numpy as np
from typing import Dict, List, Optional, Tuple, Set
from datetime import datetime
from collections import defaultdict
from .intents.knowledge_base import INTENT_KNOWLEDGE_BASE


#===============================================================================
# SLOT DEFINITIONS - Entity types to extract per intent
#===============================================================================
SLOT_DEFINITIONS = {
    "pharmacy": {
        "medication_name": {"patterns": [r"(?:for|refill|get|need)\s+(\w+(?:\s+\w+)?)", r"(\w+)\s+(?:prescription|medication|drug)"], "type": "medication"},
        "quantity": {"patterns": [r"(\d+)\s*(?:day|days|month|months)\s+supply", r"(\d+)\s+(?:pills|tablets|capsules)"], "type": "number"},
        "pharmacy_name": {"patterns": [r"(?:at|from|nearest)\s+(CVS|Walgreens|Rite Aid|Costco|Walmart)", r"(CVS|Walgreens|Rite Aid)"], "type": "pharmacy"}
    },
    "claims": {
        "claim_number": {"patterns": [r"claim\s*(?:#|number|id)?\s*[:\s]?\s*(\w{8,15})", r"(\d{10,15})"], "type": "claim_id"},
        "date_of_service": {"patterns": [r"(?:from|on|dated?)\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{1,2}(?:,?\s+\d{4})?)"], "type": "date"},
        "provider_name": {"patterns": [r"(?:from|at|with)\s+(?:Dr\.?\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", r"(?:doctor|physician|provider)\s+([A-Z][a-z]+)"], "type": "provider"}
    },
    "specialist": {
        "specialty_type": {"patterns": [r"(cardiologist|dermatologist|orthopedic|neurologist|gastroenterologist|oncologist|ENT|urologist|pulmonologist|rheumatologist|endocrinologist)"], "type": "specialty"},
        "location": {"patterns": [r"(?:near|in|around)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?(?:,\s*[A-Z]{2})?)", r"(?:zip|zipcode|zip code)\s*[:\s]?\s*(\d{5})"], "type": "location"}
    },
    "primaryCareProvider": {
        "doctor_name": {"patterns": [r"(?:Dr\.?\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", r"(?:doctor|physician)\s+([A-Z][a-z]+)"], "type": "provider"},
        "location": {"patterns": [r"(?:near|in|around)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", r"(\d{5})"], "type": "location"}
    },
    "deductible": {
        "plan_type": {"patterns": [r"(individual|family)\s+(?:deductible|plan)", r"(in[- ]?network|out[- ]?of[- ]?network)"], "type": "plan_type"},
        "year": {"patterns": [r"(?:for|in)\s+(20\d{2})", r"(this year|last year|next year)"], "type": "year"}
    },
    "eligibility": {
        "member_type": {"patterns": [r"(?:for\s+)?(?:my\s+)?(spouse|child|dependent|self)", r"(family|individual)\s+coverage"], "type": "member_type"},
        "date": {"patterns": [r"(?:as of|on|starting)\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"], "type": "date"}
    },
    "idCard": {
        "card_type": {"patterns": [r"(digital|physical|paper|temporary)\s+(?:ID\s+)?card", r"(replacement|new)\s+card"], "type": "card_type"},
        "member_type": {"patterns": [r"(?:for\s+)?(?:my\s+)?(spouse|child|dependent)"], "type": "member_type"}
    },
    "hsa": {
        "action": {"patterns": [r"(balance|contribution|withdrawal|transfer|investment)", r"(contribute|withdraw|transfer)\s+"], "type": "action"},
        "amount": {"patterns": [r"\$?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)", r"(\d+)\s+dollars"], "type": "currency"}
    },
    "appeals": {
        "claim_number": {"patterns": [r"claim\s*(?:#|number)?\s*[:\s]?\s*(\w{8,15})"], "type": "claim_id"},
        "appeal_type": {"patterns": [r"(first level|second level|external|expedited|urgent)\s+(?:appeal|review)"], "type": "appeal_type"}
    },
    "maternity": {
        "trimester": {"patterns": [r"(first|second|third|1st|2nd|3rd)\s+trimester", r"(\d+)\s+weeks?\s+pregnant"], "type": "trimester"},
        "service_type": {"patterns": [r"(prenatal|delivery|postpartum|ultrasound|c-section|cesarean)"], "type": "service"}
    }
}

#===============================================================================
# MULTI-INTENT CONJUNCTIONS - Words that signal multiple intents
#===============================================================================
MULTI_INTENT_SIGNALS = [
    r"\b(?:and also|and|also|plus|as well as|additionally|another thing|one more thing)\b",
    r"\b(?:oh and|btw|by the way|while I'm here|while you're at it)\b",
    r"\b(?:first|second|third|lastly|finally|next)\b"
]


class InMemoryVectorStore:
    """In-memory vector store for RAG similarity search."""
    
    def __init__(self):
        self.vectors: List[np.ndarray] = []
        self.metadata: List[Dict] = []
        
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


class SessionManager:
    """Manages conversation session history for context tracking."""
    
    def __init__(self):
        self.sessions: Dict[str, List[Dict]] = defaultdict(list)
        self.slot_memory: Dict[str, Dict] = defaultdict(dict)  # Stores filled slots per session
        
    def add(self, session_id: str, utterance: str, intent: str, confidence: float, 
            slots: Optional[Dict] = None, multi_intents: Optional[List] = None):
        entry = {
            "utterance": utterance, 
            "intent": intent, 
            "confidence": confidence, 
            "timestamp": datetime.utcnow().isoformat(),
            "slots": slots or {},
            "multi_intents": multi_intents or []
        }
        self.sessions[session_id].append(entry)
        
        # Update slot memory
        if slots:
            self.slot_memory[session_id].update(slots)
        
        # Keep last 10 turns per session
        if len(self.sessions[session_id]) > 10:
            self.sessions[session_id] = self.sessions[session_id][-10:]
    
    def get(self, session_id: str, n: int = 5) -> List[Dict]:
        return self.sessions.get(session_id, [])[-n:]
    
    def get_recent_intents(self, session_id: str, n: int = 3) -> List[str]:
        history = self.get(session_id, n)
        return [h["intent"] for h in history]
    
    def get_slot_memory(self, session_id: str) -> Dict:
        """Get all remembered slots for session."""
        return self.slot_memory.get(session_id, {})
    
    def get_pending_intents(self, session_id: str) -> List[str]:
        """Get intents that were detected but not yet handled."""
        history = self.get(session_id, n=1)
        if history and history[-1].get("multi_intents"):
            return history[-1]["multi_intents"][1:]  # Skip first (already handled)
        return []


class EmbeddingGenerator:
    """Simple deterministic embedding generator."""
    
    def __init__(self, dim: int = 384):
        self.dim = dim
        
    def generate(self, text: str) -> np.ndarray:
        """Generate deterministic embedding for text."""
        text = text.lower()
        np.random.seed(hash(text) % (2**32))
        emb = np.random.randn(self.dim)
        return emb / (np.linalg.norm(emb) + 1e-10)


class SlotFiller:
    """Extracts entity slots from user utterances."""
    
    def __init__(self):
        self.slot_definitions = SLOT_DEFINITIONS
    
    def extract_slots(self, utterance: str, intent: str) -> Dict[str, any]:
        """Extract slots relevant to the detected intent."""
        slots = {}
        
        # Get slot definitions for this intent
        intent_slots = self.slot_definitions.get(intent, {})
        
        for slot_name, slot_config in intent_slots.items():
            for pattern in slot_config["patterns"]:
                match = re.search(pattern, utterance, re.IGNORECASE)
                if match:
                    slots[slot_name] = {
                        "value": match.group(1),
                        "type": slot_config["type"],
                        "confidence": 0.9,
                        "source": "extracted"
                    }
                    break
        
        # Extract common slots (applicable to any intent)
        common_slots = self._extract_common_slots(utterance)
        slots.update(common_slots)
        
        return slots
    
    def _extract_common_slots(self, utterance: str) -> Dict[str, any]:
        """Extract common entities that apply to any intent."""
        slots = {}
        
        # Member ID
        member_match = re.search(r"(?:member\s*(?:id|#|number)?|id)[:\s]*([A-Z0-9]{8,12})", utterance, re.IGNORECASE)
        if member_match:
            slots["member_id"] = {"value": member_match.group(1), "type": "member_id", "confidence": 0.95, "source": "extracted"}
        
        # Phone number
        phone_match = re.search(r"(\d{3}[-.]?\d{3}[-.]?\d{4})", utterance)
        if phone_match:
            slots["phone"] = {"value": phone_match.group(1), "type": "phone", "confidence": 0.9, "source": "extracted"}
        
        # Date (generic)
        date_match = re.search(r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", utterance)
        if date_match and "date" not in slots:
            slots["date"] = {"value": date_match.group(1), "type": "date", "confidence": 0.8, "source": "extracted"}
        
        # Dollar amount
        amount_match = re.search(r"\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)", utterance)
        if amount_match:
            slots["amount"] = {"value": amount_match.group(1), "type": "currency", "confidence": 0.9, "source": "extracted"}
        
        # Zip code
        zip_match = re.search(r"\b(\d{5})(?:-\d{4})?\b", utterance)
        if zip_match:
            slots["zip_code"] = {"value": zip_match.group(1), "type": "location", "confidence": 0.85, "source": "extracted"}
        
        return slots
    
    def get_missing_required_slots(self, intent: str, filled_slots: Dict) -> List[Dict]:
        """Identify which required slots are still missing."""
        intent_slots = self.slot_definitions.get(intent, {})
        missing = []
        
        for slot_name, slot_config in intent_slots.items():
            if slot_name not in filled_slots:
                missing.append({
                    "slot_name": slot_name,
                    "type": slot_config["type"],
                    "prompt": self._get_slot_prompt(slot_name, intent)
                })
        
        return missing
    
    def _get_slot_prompt(self, slot_name: str, intent: str) -> str:
        """Generate a natural language prompt for missing slot."""
        prompts = {
            "medication_name": "What medication do you need help with?",
            "claim_number": "Can you provide the claim number?",
            "date_of_service": "What was the date of service?",
            "provider_name": "What is the provider or doctor's name?",
            "specialty_type": "What type of specialist are you looking for?",
            "location": "What is your location or zip code?",
            "doctor_name": "What is the doctor's name?",
            "plan_type": "Is this for individual or family coverage?",
            "member_type": "Is this for yourself or a dependent?",
            "amount": "What amount would you like to contribute/withdraw?"
        }
        return prompts.get(slot_name, f"Please provide the {slot_name.replace('_', ' ')}.")


class MultiIntentDetector:
    """Detects when user message contains multiple intents."""
    
    def __init__(self):
        self.signals = MULTI_INTENT_SIGNALS
    
    def has_multiple_intents(self, utterance: str) -> bool:
        """Check if utterance likely contains multiple intents."""
        for pattern in self.signals:
            if re.search(pattern, utterance, re.IGNORECASE):
                return True
        return False
    
    def split_utterance(self, utterance: str) -> List[str]:
        """Split utterance into potential separate intent segments."""
        # Split on conjunctions that typically separate intents
        split_patterns = [
            r"\s+and also\s+",
            r"\s+also\s+",
            r"\s+and\s+(?=I\s+)",
            r"\s+plus\s+",
            r"\s+as well as\s+",
            r"\.\s+(?=[A-Z])",
            r"\s+oh and\s+",
            r"\s+btw\s+",
            r"\s+by the way\s+"
        ]
        
        segments = [utterance]
        for pattern in split_patterns:
            new_segments = []
            for seg in segments:
                parts = re.split(pattern, seg, flags=re.IGNORECASE)
                new_segments.extend([p.strip() for p in parts if p.strip()])
            segments = new_segments
        
        # Filter out very short segments
        return [s for s in segments if len(s.split()) >= 2]


class DisambiguationEngine:
    """Handles disambiguation when intent is unclear."""
    
    # Natural language descriptions for intents
    INTENT_DESCRIPTIONS = {
        "pharmacy": "prescription or medication refills",
        "precert": "prior authorization for a procedure",
        "claims": "claim status or submission",
        "benefits": "coverage and benefit information",
        "eligibility": "enrollment or coverage status",
        "deductible": "deductible amount or status",
        "copay": "copay amounts",
        "coinsurance": "coinsurance percentages",
        "outOfPocketMax": "out-of-pocket maximum",
        "idCard": "insurance ID card",
        "primaryCareProvider": "primary care doctor (PCP)",
        "specialist": "specialist referral or search",
        "urgentCare": "urgent care locations",
        "emergencyRoom": "emergency room coverage",
        "telemedicine": "virtual or telehealth visits",
        "behavioralHealth": "mental health services",
        "behavioralEmergency": "mental health crisis support",
        "dental": "dental coverage",
        "vision": "vision coverage",
        "hsa": "Health Savings Account (HSA)",
        "fsa": "Flexible Spending Account (FSA)",
        "hra": "Health Reimbursement Arrangement (HRA)",
        "appeals": "appeal a claim denial",
        "maternity": "pregnancy and maternity coverage",
        "24HourNurseLine": "24-hour nurse advice line"
    }
    
    def generate_disambiguation(self, candidates: List[Dict], utterance: str) -> Dict:
        """Generate disambiguation response for ambiguous intent."""
        if len(candidates) < 2:
            return {"needed": False}
        
        # Check if top candidates are close in score
        score_diff = candidates[0]["score"] - candidates[1]["score"]
        if score_diff > 0.15:  # Clear winner
            return {"needed": False, "reason": "clear_winner"}
        
        # Build disambiguation options
        options = []
        for i, candidate in enumerate(candidates[:3]):
            desc = self.INTENT_DESCRIPTIONS.get(candidate["intent"], candidate["intent"])
            options.append({
                "option_number": i + 1,
                "intent": candidate["intent"],
                "description": desc,
                "agent": candidate["agent"]
            })
        
        # Generate natural language prompt
        if len(options) == 2:
            prompt = f"I want to make sure I help you correctly. Are you asking about {options[0]['description']} or {options[1]['description']}?"
        else:
            descs = [o['description'] for o in options]
            prompt = f"I want to make sure I understand. Are you asking about {descs[0]}, {descs[1]}, or {descs[2]}?"
        
        return {
            "needed": True,
            "reason": "ambiguous_intent",
            "prompt": prompt,
            "options": options,
            "original_utterance": utterance
        }


class LocalIntentClassifier:
    """
    RAG-based Intent Classifier with:
    - Disambiguation
    - Context-aware classification
    - Multi-intent detection
    - Slot filling
    """
    
    def __init__(self):
        self.vector_store = InMemoryVectorStore()
        self.session_manager = SessionManager()
        self.embedder = EmbeddingGenerator()
        self.slot_filler = SlotFiller()
        self.multi_intent_detector = MultiIntentDetector()
        self.disambiguation_engine = DisambiguationEngine()
        self._build_kb()
        
    def _build_kb(self):
        """Build vector knowledge base from intent training data."""
        vectors, metadata = [], []
        for intent_id, data in INTENT_KNOWLEDGE_BASE.items():
            for idx, utt in enumerate(data["training_utterances"]):
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
    
    def classify(self, utterance: str, session_id: str = "default", 
                 context_aware: bool = True) -> Dict:
        """
        Full classification with all features:
        - Basic intent classification
        - Context boosting
        - Multi-intent detection
        - Slot extraction
        - Disambiguation check
        """
        start = datetime.utcnow()
        
        # 1. MULTI-INTENT DETECTION
        multi_intents = []
        if self.multi_intent_detector.has_multiple_intents(utterance):
            segments = self.multi_intent_detector.split_utterance(utterance)
            if len(segments) > 1:
                for seg in segments:
                    seg_result = self._classify_single(seg)
                    multi_intents.append({
                        "segment": seg,
                        "intent": seg_result["intent"],
                        "confidence": seg_result["confidence"],
                        "agent": seg_result["agent_routing"]
                    })
        
        # 2. PRIMARY CLASSIFICATION
        result = self._classify_single(utterance)
        
        # 3. CONTEXT-AWARE BOOSTING
        if context_aware:
            result = self._apply_context_boost(result, utterance, session_id)
        
        # 4. SLOT FILLING
        slots = self.slot_filler.extract_slots(utterance, result["intent"])
        
        # Merge with session slot memory
        session_slots = self.session_manager.get_slot_memory(session_id)
        merged_slots = {**session_slots, **slots}  # New slots override old
        
        # Check for missing required slots
        missing_slots = self.slot_filler.get_missing_required_slots(result["intent"], merged_slots)
        
        # 5. DISAMBIGUATION CHECK
        candidates = self.get_candidates(utterance, top_k=3)
        disambiguation = self.disambiguation_engine.generate_disambiguation(candidates, utterance)
        
        # 6. BUILD FINAL RESULT
        result.update({
            "slots": slots,
            "merged_slots": merged_slots,
            "missing_slots": missing_slots,
            "slot_filling_complete": len(missing_slots) == 0,
            "multi_intents": multi_intents if multi_intents else None,
            "has_multi_intents": len(multi_intents) > 1,
            "disambiguation": disambiguation,
            "needs_disambiguation": disambiguation["needed"],
            "candidates": candidates,
            "processing_time_ms": (datetime.utcnow() - start).total_seconds() * 1000
        })
        
        # Track in session
        self.session_manager.add(
            session_id, utterance, result["intent"], result["confidence"],
            slots=slots, multi_intents=[m["intent"] for m in multi_intents]
        )
        
        return result
    
    def _classify_single(self, utterance: str) -> Dict:
        """Basic single-intent classification."""
        query_emb = self.embedder.generate(utterance)
        results = self.vector_store.search(query_emb, top_k=10)
        
        # Vote from top matches
        votes = defaultdict(float)
        for meta, score in results[:5]:
            votes[meta["intent_name"]] += score
        
        best_intent = max(votes, key=votes.get) if votes else "unknown"
        best_meta = next((m for m, s in results if m["intent_name"] == best_intent), 
                        {"intent_id": "UNK", "agent_routing": "FallbackAgent", 
                         "category": "unknown", "priority": 5})
        
        # Confidence calculation
        matching = [s for m, s in results[:3] if m["intent_name"] == best_intent]
        confidence = round(sum(matching) / len(matching) if matching else 0.5, 3)
        
        return {
            "intent": best_intent,
            "intent_id": best_meta["intent_id"],
            "agent_routing": best_meta["agent_routing"],
            "category": best_meta["category"],
            "priority": best_meta["priority"],
            "confidence": confidence,
            "top_match_score": results[0][1] if results else 0.0
        }
    
    def _apply_context_boost(self, result: Dict, utterance: str, session_id: str) -> Dict:
        """Apply context-aware boosting based on session history."""
        recent_intents = self.session_manager.get_recent_intents(session_id, n=3)
        
        if not recent_intents:
            result["context_applied"] = False
            return result
        
        # Check for continuation signals
        continuation_signals = ["also", "and", "what about", "how about", "another", 
                               "same", "that", "this", "it", "more"]
        utterance_lower = utterance.lower()
        has_continuation = any(sig in utterance_lower for sig in continuation_signals)
        
        # Short utterance + recent context = likely continuation
        is_short = len(utterance.split()) <= 4
        
        if (has_continuation or is_short) and result["confidence"] < 0.8:
            candidates = self.get_candidates(utterance, top_k=5)
            
            for candidate in candidates:
                if candidate["intent"] in recent_intents:
                    # Boost this intent
                    boost_amount = 0.15 if has_continuation else 0.10
                    result["original_intent"] = result["intent"]
                    result["original_confidence"] = result["confidence"]
                    result["intent"] = candidate["intent"]
                    result["confidence"] = min(0.95, result["confidence"] + boost_amount)
                    result["context_boosted"] = True
                    result["context_match"] = candidate["intent"]
                    result["context_applied"] = True
                    return result
        
        result["context_applied"] = True
        result["context_boosted"] = False
        return result
    
    def get_candidates(self, utterance: str, top_k: int = 3) -> List[Dict]:
        """Get top candidate intents for disambiguation."""
        query_emb = self.embedder.generate(utterance)
        results = self.vector_store.search(query_emb, top_k=20)
        
        # Aggregate scores by intent
        intent_scores = defaultdict(list)
        intent_meta = {}
        
        for meta, score in results:
            intent_name = meta["intent_name"]
            intent_scores[intent_name].append(score)
            if intent_name not in intent_meta:
                intent_meta[intent_name] = meta
        
        # Calculate average score per intent
        intent_avg = {
            intent: sum(scores) / len(scores) 
            for intent, scores in intent_scores.items()
        }
        
        # Sort and take top_k
        sorted_intents = sorted(intent_avg.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        candidates = []
        for intent_name, avg_score in sorted_intents:
            meta = intent_meta[intent_name]
            candidates.append({
                "intent": intent_name,
                "intent_id": meta["intent_id"],
                "agent": meta["agent_routing"],
                "category": meta["category"],
                "score": round(avg_score, 3)
            })
        
        return candidates
    
    def handle_disambiguation_response(self, session_id: str, selected_option: int) -> Dict:
        """Process user's disambiguation selection."""
        history = self.session_manager.get(session_id, n=1)
        if not history:
            return {"error": "No disambiguation pending"}
        
        # Would retrieve the candidates from the last classification
        # For now, return confirmation structure
        return {
            "status": "disambiguation_resolved",
            "selected_option": selected_option,
            "session_id": session_id
        }
    
    def get_next_pending_intent(self, session_id: str) -> Optional[Dict]:
        """Get the next unhandled intent from multi-intent detection."""
        pending = self.session_manager.get_pending_intents(session_id)
        if pending:
            return {"intent": pending[0], "remaining_count": len(pending) - 1}
        return None


# Singleton instance
_instance = None

def get_classifier() -> LocalIntentClassifier:
    global _instance
    if _instance is None:
        _instance = LocalIntentClassifier()
    return _instance
