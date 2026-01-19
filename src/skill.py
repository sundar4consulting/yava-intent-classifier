"""
Watson Orchestrate Skill Interface - Exposed as Tool/API for Agent

ENHANCED with:
- Full NLU Classification (disambiguation, context, multi-intent, slots)
- Slot Extraction API
- Multi-Intent Detection API
- Disambiguation Management API
- Context-Aware Classification API
"""

import json
from typing import Dict, List, Optional
from .classifier import get_classifier
from .intents.knowledge_base import get_all_intents as _get_all_intents


#===============================================================================
# TOOL 1: FULL CLASSIFICATION (Primary Tool - Called for every utterance)
#===============================================================================
def classify_intent(user_input: str, 
                   conversation_id: Optional[str] = None,
                   member_id: Optional[str] = None,
                   context_aware: bool = True) -> Dict:
    """
    Tool: Full NLU Classification with all features.
    Called by Agent for EVERY user message.
    
    Features:
        - Intent classification with confidence
        - Slot extraction (dates, IDs, amounts, names)
        - Multi-intent detection (compound sentences)
        - Context-aware boosting from conversation history
        - Disambiguation when intents are ambiguous
    
    Returns:
        - intent: Primary detected intent
        - agent: Target agent for routing
        - confidence: Classification confidence (0-1)
        - slots: Extracted entities {slot_type: value}
        - missing_slots: Required slots not yet provided
        - multi_intents: Array of intents if multiple detected
        - needs_disambiguation: True if clarification needed
        - disambiguation_prompt: Question to ask user for clarity
        - candidates: Top 3 intent candidates
        - context_applied: Whether history was used for boosting
    """
    session_id = conversation_id or f"watson-{member_id}" if member_id else "default"
    classifier = get_classifier()
    
    # Full classification with all features
    result = classifier.classify(user_input, session_id, context_aware=context_aware)
    
    # Get session history for context
    session_history = classifier.session_manager.get(session_id, n=5)
    
    return {
        # Primary Classification
        "intent": result["intent"],
        "intent_id": result["intent_id"],
        "agent": result["agent_routing"],
        "category": result["category"],
        "confidence": result["confidence"],
        
        # Slot Filling
        "slots": result.get("slots", {}),
        "merged_slots": result.get("merged_slots", {}),  # With session memory
        "missing_slots": result.get("missing_slots", []),
        "slot_filling_complete": result.get("slot_filling_complete", True),
        
        # Multi-Intent Detection
        "has_multi_intents": result.get("has_multi_intents", False),
        "multi_intents": result.get("multi_intents"),  # [{segment, intent, confidence, agent}]
        
        # Disambiguation
        "needs_disambiguation": result.get("needs_disambiguation", False),
        "disambiguation_prompt": result.get("disambiguation", {}).get("prompt", ""),
        "disambiguation_options": result.get("disambiguation", {}).get("options", []),
        
        # Context
        "context_applied": result.get("context_applied", False),
        "context_boosted": result.get("context_boosted", False),
        
        # Candidates for UI/Review
        "candidates": result.get("candidates", []),
        
        # Session
        "session": {
            "conversation_id": session_id,
            "recent_intents": [h["intent"] for h in session_history],
            "turn_count": len(session_history)
        },
        
        # Metadata
        "metadata": {
            "processing_time_ms": result.get("processing_time_ms", 0),
            "top_match_score": result.get("top_match_score", 0)
        }
    }


#===============================================================================
# TOOL 2: SLOT EXTRACTION
#===============================================================================
def extract_slots(user_input: str, intent: Optional[str] = None) -> Dict:
    """
    Tool: Extract entities/parameters from user utterance.
    
    Extracts:
        - Dates (MM/DD/YYYY, tomorrow, next week, etc.)
        - Claim/Reference IDs (CLM-12345, REF-ABC)
        - Member IDs (MEM-123456, member number patterns)
        - Currency amounts ($100.50, $1,234.56)
        - Names (Dr. Smith, proper nouns)
        - Pharmacy names
        - Medication names
        - Procedure codes (CPT, ICD-10)
    
    Returns:
        - extracted_slots: {slot_type: value}
        - slot_count: Number of slots found
        - slot_types: List of slot types found
        - required_slots: Slots typically needed for this intent
        - missing_required: Required slots not yet provided
    """
    classifier = get_classifier()
    
    # Extract slots
    slots = classifier.slot_filler.extract_slots(user_input, intent or "general")
    
    # Get required slots for intent
    required = classifier.slot_filler.get_missing_required_slots(intent or "general", {})
    missing = classifier.slot_filler.get_missing_required_slots(intent or "general", slots)
    
    return {
        "extracted_slots": slots,
        "slot_count": len(slots),
        "slot_types": list(slots.keys()),
        "required_slots": required,
        "missing_required": missing,
        "slot_prompts": _generate_slot_prompts(missing),
        "original_input": user_input
    }


def _generate_slot_prompts(missing_slots: List[str]) -> Dict[str, str]:
    """Generate user-friendly prompts for missing slots."""
    prompts = {
        "member_id": "Could you please provide your member ID?",
        "date_of_service": "What was the date of service?",
        "claim_id": "Do you have a claim ID or reference number?",
        "pharmacy_name": "Which pharmacy would you like to use?",
        "medication_name": "What medication do you need?",
        "provider_name": "What is the provider or doctor's name?",
        "amount": "What is the amount in question?",
        "procedure_code": "Do you have the procedure or service code?"
    }
    return {slot: prompts.get(slot, f"Please provide the {slot.replace('_', ' ')}") 
            for slot in missing_slots}


#===============================================================================
# TOOL 3: MULTI-INTENT DETECTION
#===============================================================================
def detect_multi_intent(user_input: str, 
                        conversation_id: Optional[str] = None) -> Dict:
    """
    Tool: Detect if user utterance contains multiple intents.
    
    Detects compound sentences like:
        - "I need to refill my prescription AND check my claims"
        - "What's my deductible and also my copay for specialists?"
        - "First check my eligibility, then tell me about my benefits"
    
    Returns:
        - has_multiple_intents: Boolean
        - intent_count: Number of intents detected
        - intents: Array of {segment, intent, confidence, agent}
        - suggested_order: Recommended processing order
        - combined_response_possible: Whether single response can address all
    """
    session_id = conversation_id or "default"
    classifier = get_classifier()
    
    # Check for multiple intents
    has_multi = classifier.multi_intent_detector.has_multiple_intents(user_input)
    
    if not has_multi:
        # Single intent - classify normally
        result = classifier.classify(user_input, session_id, context_aware=False)
        return {
            "has_multiple_intents": False,
            "intent_count": 1,
            "intents": [{
                "segment": user_input,
                "intent": result["intent"],
                "confidence": result["confidence"],
                "agent": result["agent_routing"]
            }],
            "suggested_order": [result["intent"]],
            "combined_response_possible": True
        }
    
    # Split and classify each segment
    segments = classifier.multi_intent_detector.split_utterance(user_input)
    intents = []
    
    for segment in segments:
        if segment.strip():
            seg_result = classifier._classify_single(segment)
            intents.append({
                "segment": segment,
                "intent": seg_result["intent"],
                "confidence": seg_result["confidence"],
                "agent": seg_result["agent_routing"],
                "priority": seg_result.get("priority", 3)
            })
    
    # Sort by priority (lower = higher priority)
    sorted_intents = sorted(intents, key=lambda x: x.get("priority", 3))
    
    # Check if same agent handles all (can combine response)
    unique_agents = set(i["agent"] for i in intents)
    combined_possible = len(unique_agents) == 1
    
    return {
        "has_multiple_intents": len(intents) > 1,
        "intent_count": len(intents),
        "intents": intents,
        "suggested_order": [i["intent"] for i in sorted_intents],
        "combined_response_possible": combined_possible,
        "unique_agents": list(unique_agents),
        "original_input": user_input
    }


#===============================================================================
# TOOL 4: DISAMBIGUATION
#===============================================================================
def get_disambiguation(user_input: str, top_k: int = 3) -> Dict:
    """
    Tool: Get disambiguation options when intent is unclear.
    
    Use when:
        - Primary classification has low confidence (<0.75)
        - Top 2 candidates are close in score
        - User request is vague or ambiguous
    
    Returns:
        - needs_disambiguation: Boolean
        - prompt: Human-friendly question to ask user
        - options: Array of {option_number, intent, description, agent}
        - confidence_gap: Difference between top 2 candidates
    """
    classifier = get_classifier()
    candidates = classifier.get_candidates(user_input, top_k=top_k)
    disambiguation = classifier.disambiguation_engine.generate_disambiguation(candidates, user_input)
    
    return {
        "needs_disambiguation": disambiguation["needed"],
        "reason": disambiguation.get("reason", ""),
        "prompt": disambiguation.get("prompt", ""),
        "options": disambiguation.get("options", []),
        "candidates": candidates,
        "confidence_gap": round(candidates[0]["score"] - candidates[1]["score"], 3) if len(candidates) >= 2 else 1.0,
        "recommendation": "Ask user for clarification" if disambiguation["needed"] else "Proceed with top intent",
        "original_input": user_input
    }


def resolve_disambiguation(conversation_id: str, 
                          selected_option: int,
                          original_utterance: str) -> Dict:
    """
    Tool: Process user's disambiguation selection.
    
    Args:
        conversation_id: Session identifier
        selected_option: User's choice (1, 2, or 3)
        original_utterance: The original ambiguous utterance
    
    Returns:
        - resolved_intent: The selected intent
        - agent: Target agent for routing
        - status: Resolution status
    """
    classifier = get_classifier()
    candidates = classifier.get_candidates(original_utterance, top_k=3)
    
    if selected_option < 1 or selected_option > len(candidates):
        return {
            "status": "error",
            "error": f"Invalid option. Please select 1-{len(candidates)}"
        }
    
    selected = candidates[selected_option - 1]
    
    # Track in session
    classifier.session_manager.add(
        conversation_id, original_utterance, 
        selected["intent"], selected["score"],
        slots={}, disambiguation_resolved=True
    )
    
    return {
        "status": "resolved",
        "resolved_intent": selected["intent"],
        "intent_id": selected["intent_id"],
        "agent": selected["agent"],
        "category": selected["category"],
        "confidence": selected["score"],
        "conversation_id": conversation_id
    }


#===============================================================================
# TOOL 5: CONTEXT/SESSION MANAGEMENT
#===============================================================================
def get_session_context(conversation_id: str, turns: int = 5) -> Dict:
    """
    Tool: Get full conversation context including slot memory.
    
    Returns:
        - history: Recent conversation turns
        - slot_memory: Accumulated slots across conversation
        - recent_intents: List of recent intents
        - context_summary: Natural language summary
        - pending_intents: Unhandled intents from multi-intent detection
    """
    classifier = get_classifier()
    history = classifier.session_manager.get(conversation_id, n=turns)
    slot_memory = classifier.session_manager.get_slot_memory(conversation_id)
    pending = classifier.session_manager.get_pending_intents(conversation_id)
    
    return {
        "conversation_id": conversation_id,
        "history": history,
        "turn_count": len(history),
        "recent_intents": [h["intent"] for h in history],
        "slot_memory": slot_memory,
        "pending_intents": pending,
        "has_pending": len(pending) > 0,
        "context_summary": _summarize_context(history)
    }


def clear_session(conversation_id: str) -> Dict:
    """Tool: Clear session history and slot memory."""
    classifier = get_classifier()
    # Clear by setting empty
    if conversation_id in classifier.session_manager.sessions:
        del classifier.session_manager.sessions[conversation_id]
    if conversation_id in classifier.session_manager.slot_memory:
        del classifier.session_manager.slot_memory[conversation_id]
    
    return {
        "status": "cleared",
        "conversation_id": conversation_id
    }


#===============================================================================
# TOOL 6: INTENT CATALOG
#===============================================================================
def get_intents() -> Dict:
    """Tool: List all 47 available intents with routing info."""
    intents = _get_all_intents()
    
    # Group by category
    by_category = {}
    for intent in intents:
        cat = intent["category"]
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(intent)
    
    return {
        "total_count": len(intents),
        "categories": list(by_category.keys()),
        "by_category": by_category,
        "intents": intents
    }


def get_intent_details(intent_name: str) -> Dict:
    """Tool: Get details for a specific intent."""
    intents = _get_all_intents()
    
    for intent in intents:
        if intent["intent_name"] == intent_name:
            classifier = get_classifier()
            # Get slot requirements
            required_slots = classifier.slot_filler.SLOT_REQUIREMENTS.get(intent_name, [])
            
            return {
                "found": True,
                "intent": intent,
                "required_slots": required_slots,
                "slot_prompts": _generate_slot_prompts(required_slots)
            }
    
    return {
        "found": False,
        "error": f"Intent '{intent_name}' not found"
    }


#===============================================================================
# TOOL 7: HEALTH CHECK
#===============================================================================
def health_check() -> Dict:
    """Tool: Health check endpoint."""
    classifier = get_classifier()
    return {
        "status": "healthy",
        "service": "yava-intent-classifier",
        "version": "2.0.0",  # Updated for enhanced features
        "features": [
            "intent_classification",
            "slot_extraction",
            "multi_intent_detection",
            "disambiguation",
            "context_awareness",
            "session_management"
        ],
        "intent_count": 47,
        "vector_count": len(classifier.vector_store.vectors)
    }


#===============================================================================
# INTERNAL HELPERS
#===============================================================================
def _summarize_context(history: List[Dict]) -> str:
    """Summarize conversation context."""
    if not history:
        return "New conversation - no prior context"
    
    intents = [h["intent"] for h in history]
    unique_intents = list(dict.fromkeys(intents))
    
    if len(unique_intents) == 1:
        return f"User has been asking about {unique_intents[0]} ({len(history)} turns)"
    else:
        return f"User has discussed: {', '.join(unique_intents)} ({len(history)} turns)"


#===============================================================================
# MAIN ROUTER - Watson Orchestrate Entry Point
#===============================================================================
def main(params: Dict) -> Dict:
    """
    Main entry point for Watson Orchestrate skill/tool calls.
    
    Supported actions:
        - classify: Full NLU classification (default)
        - extract_slots: Extract entities from utterance
        - detect_multi: Detect multiple intents
        - disambiguate: Get disambiguation options
        - resolve_disambiguate: Process disambiguation selection
        - context: Get session context
        - clear_context: Clear session
        - intents: List all intents
        - intent_details: Get specific intent details
        - health: Health check
    """
    action = params.get("action", "classify")
    
    # CLASSIFY (default - full NLU)
    if action == "classify":
        return classify_intent(
            params.get("user_input", ""),
            params.get("conversation_id"),
            params.get("member_id"),
            params.get("context_aware", True)
        )
    
    # SLOT EXTRACTION
    elif action == "extract_slots":
        return extract_slots(
            params.get("user_input", ""),
            params.get("intent")
        )
    
    # MULTI-INTENT DETECTION
    elif action == "detect_multi":
        return detect_multi_intent(
            params.get("user_input", ""),
            params.get("conversation_id")
        )
    
    # DISAMBIGUATION
    elif action == "disambiguate":
        return get_disambiguation(
            params.get("user_input", ""),
            params.get("top_k", 3)
        )
    
    elif action == "resolve_disambiguate":
        return resolve_disambiguation(
            params.get("conversation_id", "default"),
            params.get("selected_option", 1),
            params.get("original_utterance", "")
        )
    
    # CONTEXT MANAGEMENT
    elif action == "context":
        return get_session_context(
            params.get("conversation_id", "default"),
            params.get("turns", 5)
        )
    
    elif action == "clear_context":
        return clear_session(params.get("conversation_id", "default"))
    
    # INTENT CATALOG
    elif action == "intents":
        return get_intents()
    
    elif action == "intent_details":
        return get_intent_details(params.get("intent_name", ""))
    
    # HEALTH
    elif action == "health":
        return health_check()
    
    else:
        return {
            "error": f"Unknown action: {action}",
            "available_actions": [
                "classify", "extract_slots", "detect_multi",
                "disambiguate", "resolve_disambiguate",
                "context", "clear_context",
                "intents", "intent_details", "health"
            ]
        }


if __name__ == "__main__":
    # Test enhanced classification
    print("=== TEST: Full Classification ===")
    result = classify_intent(
        "I need to refill my prescription for Lipitor and also check my claim from January 15th",
        "test-session"
    )
    print(json.dumps(result, indent=2))
    
    print("\n=== TEST: Slot Extraction ===")
    slots = extract_slots("I have a claim CLM-12345 from 03/15/2024 for $150.00")
    print(json.dumps(slots, indent=2))
    
    print("\n=== TEST: Multi-Intent Detection ===")
    multi = detect_multi_intent("Check my deductible and also tell me about my copay for specialists")
    print(json.dumps(multi, indent=2))
