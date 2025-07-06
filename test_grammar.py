#!/usr/bin/env python3
"""
Test script for grammar correction system
"""

import os
import sys
from grammar import GrammarCorrector

def test_grammar_correction():
    """Test the grammar correction system"""
    
    # Test API key
    api_key = "AIzaSyBoQm-M71m6R480usN11JUNN9kzeqqsu7Q"
    
    print("Testing Grammar Correction System...")
    print("=" * 50)
    
    # Test text with common dyslexic errors
    test_text = "I sore buterflis in the garden. I did not under stand It was winter at home bet it was sumer at the garden. I notest it was time for school. So I ran awte so that I wood not be late. wen I got to school I told my frends abwte the garden."
    
    print(f"Original Text: {test_text}")
    print("-" * 50)
    
    try:
        # Initialize corrector
        print("Initializing GrammarCorrector...")
        corrector = GrammarCorrector(api_key)
        print("✓ GrammarCorrector initialized successfully")
        
        # Test correction
        print("\nTesting text correction...")
        result = corrector.correct_text(test_text)
        
        print(f"✓ Correction completed")
        print(f"Result type: {type(result)}")
        print(f"Result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
        
        # Display results
        print("\n" + "=" * 50)
        print("CORRECTION RESULTS:")
        print("=" * 50)
        
        corrected_text = result.get('corrected_text', 'No corrected text found')
        corrections = result.get('corrections', [])
        summary = result.get('summary', 'No summary found')
        
        print(f"Corrected Text: {corrected_text}")
        print(f"Number of corrections: {len(corrections)}")
        print(f"Summary: {summary}")
        
        if corrections:
            print("\nDetailed Corrections:")
            for i, correction in enumerate(corrections, 1):
                print(f"{i}. {correction.get('original', 'N/A')} → {correction.get('corrected', 'N/A')}")
                print(f"   Explanation: {correction.get('explanation', 'N/A')}")
                print()
        
        # Test explanation generation
        print("=" * 50)
        print("EXPLANATION GENERATION:")
        print("=" * 50)
        
        explanation = corrector.get_correction_explanation(corrections)
        print(explanation)
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_grammar_correction() 