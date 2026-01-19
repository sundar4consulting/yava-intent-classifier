#!/usr/bin/env python3
"""Test YAVA Intent Classifier"""

import sys
sys.path.insert(0, '.')

from src.classifier import get_classifier
from src.skill import classify_intent, get_intents, health_check

def test():
    print("=" * 60)
    print("YAVA Intent Classifier - Test Suite")
    print("=" * 60)
    
    # Test initialization
    classifier = get_classifier()
    print(f"\n✓ Classifier initialized with {len(classifier.vector_store.vectors)} training vectors")
    
    # Test classification
    test_cases = [
        ("I need to refill my prescription", "pharmacy"),
        ("Check my claim status", "claims"),
        ("What is my deductible", "deductible"),
        ("Find urgent care near me", "urgentCare"),
        ("I need mental health support", "behavioralHealth"),
        ("Am I covered", "eligibility"),
        ("I need a new ID card", "idCard"),
        ("HSA balance", "hsa"),
    ]
    
    print("\nClassification Tests:")
    print("-" * 60)
    
    passed = 0
    for utterance, expected in test_cases:
        result = classifier.classify(utterance)
        status = "✓" if result["intent"] == expected else "✗"
        if result["intent"] == expected:
            passed += 1
        print(f"{status} '{utterance}'")
        print(f"  → {result['intent']} ({result['confidence']:.2f}) → {result['agent_routing']}")
    
    print(f"\nAccuracy: {passed}/{len(test_cases)} ({100*passed/len(test_cases):.0f}%)")
    
    # Test skill interface
    print("\n" + "-" * 60)
    print("Skill Interface Tests:")
    
    result = classify_intent("I need to see a specialist")
    print(f"✓ classify_intent: {result['intent']} → {result['agent']}")
    
    intents = get_intents()
    print(f"✓ get_intents: {intents['count']} intents")
    
    health = health_check()
    print(f"✓ health_check: {health['status']}")
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    test()
