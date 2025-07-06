import openai
import os
import json
from typing import Dict, List

class GrammarCorrector:
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = "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"
        openai.api_key = api_key
        self.model = "gpt-3.5-turbo"

    def correct_text(self, original_text: str) -> Dict:
        prompt = f"""
You are an expert English teacher helping a dyslexic student. The following text was extracted from handwritten notes using OCR and may contain spelling, grammar, and word usage errors.

Please:
1. Correct ALL spelling, grammar, and word usage mistakes
2. For each correction, provide a simple explanation
3. Maintain the original meaning and context
4. Be especially careful with common dyslexic errors (reversed letters, phonetic spelling, etc.)

Format your response as JSON:
{{
    "corrected_text": "fully corrected text here",
    "corrections": [
        {{
            "original": "incorrect word/phrase",
            "corrected": "correct word/phrase", 
            "explanation": "simple explanation of the correction"
        }}
    ],
    "summary": "brief summary of main corrections made"
}}

Original text: "{original_text}"

Please respond with ONLY the JSON format above, no additional text.
"""
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=800
            )
            content = response.choices[0].message.content.strip()
            try:
                result = json.loads(content)
                return result
            except Exception:
                return {"corrected_text": original_text, "corrections": [], "summary": "Unable to parse OpenAI response"}
        except Exception as e:
            print(f"OpenAI error: {e}")
            return {"corrected_text": original_text, "corrections": [], "summary": "OpenAI error"}

    def get_correction_explanation(self, corrections: List[Dict]) -> str:
        if not corrections:
            return "No corrections were needed for this text."
        explanation = "Here are the corrections made:\n\n"
        for i, correction in enumerate(corrections, 1):
            explanation += f"{i}. **{correction['original']}** → **{correction['corrected']}**\n"
            explanation += f"   {correction['explanation']}\n\n"
        return explanation

# Example usage and testing
if __name__ == "__main__":
    # Test the grammar corrector
    api_key = os.getenv('OPENAI_API_KEY') or "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"
    corrector = GrammarCorrector(api_key)
    test_text = (
        "I sore buterflis in the garden. I did not under stand It was winter at home bet it was sumer at the garden. "
        "I notest it was time for school. So I ran awte so that I wood not be late. wen I got to school I told my frends abwte the garden."
    )
    result = corrector.correct_text(test_text)
    print("Original:", test_text)
    print("Corrected:", result.get('corrected_text', ''))
    print("Corrections:", result.get('corrections', []))
    print("Summary:", result.get('summary', ''))

    # --- Expected Output Example (for documentation) ---
    # Corrected Text:
    # I saw butterflies in the garden. I did not understand. It was winter at home, but it was summer at the garden.
    # I noticed it was time for school. So, I ran out so that I would not be late.
    # When I got to school, I told my friends about the garden. 
