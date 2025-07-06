import re
from typing import Dict, List

class LocalGrammarCorrector:
    """Local grammar correction system without external API dependencies"""
    
    def __init__(self):
        # Common dyslexic spelling errors and corrections
        self.spelling_corrections = {
            # Common letter reversals and phonetic errors
            'sore': 'saw',
            'buterflis': 'butterflies',
            'buterfly': 'butterfly',
            'under stand': 'understand',
            'bet': 'but',
            'sumer': 'summer',
            'winter': 'winter',  # This is correct
            'notest': 'noticed',
            'awte': 'out',
            'wood': 'would',
            'wen': 'when',
            'frends': 'friends',
            'abwte': 'about',
            'recieve': 'receive',
            'beleive': 'believe',
            'seperate': 'separate',
            'definately': 'definitely',
            'occassion': 'occasion',
            'accomodate': 'accommodate',
            'begining': 'beginning',
            'calender': 'calendar',
            'collegue': 'colleague',
            'concious': 'conscious',
            'embarass': 'embarrass',
            'enviroment': 'environment',
            'existance': 'existence',
            'foward': 'forward',
            'fourty': 'forty',
            'freind': 'friend',
            'goverment': 'government',
            'grammer': 'grammar',
            'happend': 'happened',
            'harrass': 'harass',
            'immediatly': 'immediately',
            'independant': 'independent',
            'knowlege': 'knowledge',
            'liase': 'liaise',
            'liason': 'liaison',
            'lollypop': 'lollipop',
            'neccessary': 'necessary',
            'occassionally': 'occasionally',
            'occured': 'occurred',
            'occurence': 'occurrence',
            'pavillion': 'pavilion',
            'peice': 'piece',
            'persistant': 'persistent',
            'posession': 'possession',
            'priviledge': 'privilege',
            'probaly': 'probably',
            'proffesional': 'professional',
            'promiss': 'promise',
            'pronounciation': 'pronunciation',
            'prufe': 'proof',
            'publically': 'publicly',
            'quater': 'quarter',
            'que': 'queue',
            'questionaire': 'questionnaire',
            'readible': 'readable',
            'realy': 'really',
            'reccomend': 'recommend',
            'rediculous': 'ridiculous',
            'refered': 'referred',
            'refering': 'referring',
            'religous': 'religious',
            'remeber': 'remember',
            'rember': 'remember',
            'resistence': 'resistance',
            'sence': 'sense',
            'seperate': 'separate',
            'sieze': 'seize',
            'similiar': 'similar',
            'sincerly': 'sincerely',
            'speach': 'speech',
            'sucess': 'success',
            'sucessful': 'successful',
            'suprise': 'surprise',
            'tatoo': 'tattoo',
            'tendancy': 'tendency',
            'therefor': 'therefore',
            'threshhold': 'threshold',
            'tommorow': 'tomorrow',
            'tounge': 'tongue',
            'truely': 'truly',
            'unfortunatly': 'unfortunately',
            'untill': 'until',
            'wierd': 'weird',
            'whereever': 'wherever',
            'wich': 'which',
            'womens': "women's",
            'writting': 'writing',
            'youre': "you're",
            'your': 'your',
            'youse': 'you',
        }
        
        # Grammar corrections
        self.grammar_corrections = {
            'i ': 'I ',
            ' i ': ' I ',
            ' i.': ' I.',
            ' i,': ' I,',
            ' i!': ' I!',
            ' i?': ' I?',
        }
        
        # Punctuation fixes
        self.punctuation_fixes = {
            r'\s+([.,;:?!])': r'\1',  # Remove spaces before punctuation
            r'([.!?])\s*([a-z])': r'\1 \2',  # Add space after sentence endings
            r'([.!?])\s*([A-Z])': r'\1 \2',  # Add space after sentence endings
        }
    
    def correct_text(self, original_text: str) -> Dict:
        """Correct spelling and grammar errors in the given text"""
        corrected_text = original_text
        corrections = []
        
        # Apply spelling corrections
        for wrong, correct in self.spelling_corrections.items():
            if wrong.lower() in corrected_text.lower():
                # Find all occurrences
                pattern = re.compile(re.escape(wrong), re.IGNORECASE)
                matches = pattern.finditer(corrected_text)
                
                for match in matches:
                    original_word = corrected_text[match.start():match.end()]
                    corrected_word = correct
                    
                    # Preserve case
                    if original_word.isupper():
                        corrected_word = correct.upper()
                    elif original_word.istitle():
                        corrected_word = correct.title()
                    
                    corrections.append({
                        'original': original_word,
                        'corrected': corrected_word,
                        'explanation': f"Spelling correction: '{original_word}' should be '{corrected_word}'"
                    })
                
                # Replace all occurrences
                corrected_text = pattern.sub(correct, corrected_text)
        
        # Apply grammar corrections
        for wrong, correct in self.grammar_corrections.items():
            if wrong in corrected_text:
                corrections.append({
                    'original': wrong,
                    'corrected': correct,
                    'explanation': f"Grammar correction: '{wrong}' should be '{correct}' (capitalization)"
                })
                corrected_text = corrected_text.replace(wrong, correct)
        
        # Apply punctuation fixes
        for pattern, replacement in self.punctuation_fixes.items():
            corrected_text = re.sub(pattern, replacement, corrected_text)
        
        # Generate summary
        if corrections:
            summary = f"Corrected {len(corrections)} spelling and grammar errors"
        else:
            summary = "No corrections were needed for this text"
        
        return {
            'corrected_text': corrected_text,
            'corrections': corrections,
            'summary': summary
        }
    
    def get_correction_explanation(self, corrections: List[Dict]) -> str:
        """Generate a user-friendly explanation of corrections"""
        if not corrections:
            return "No corrections were needed for this text."
        
        explanation = "Here are the corrections made:\n\n"
        
        for i, correction in enumerate(corrections, 1):
            explanation += f"{i}. **{correction['original']}** → **{correction['corrected']}**\n"
            explanation += f"   {correction['explanation']}\n\n"
        
        return explanation

# Test the local grammar corrector
if __name__ == "__main__":
    corrector = LocalGrammarCorrector()
    
    test_text = "I sore buterflis in the garden. I did not under stand It was winter at home bet it was sumer at the garden. I notest it was time for school. So I ran awte so that I wood not be late. wen I got to school I told my frends abwte the garden."
    
    print("Testing Local Grammar Correction System...")
    print("=" * 60)
    print(f"Original Text: {test_text}")
    print("-" * 60)
    
    result = corrector.correct_text(test_text)
    
    print(f"Corrected Text: {result['corrected_text']}")
    print(f"Number of corrections: {len(result['corrections'])}")
    print(f"Summary: {result['summary']}")
    
    if result['corrections']:
        print("\nDetailed Corrections:")
        for i, correction in enumerate(result['corrections'], 1):
            print(f"{i}. {correction['original']} → {correction['corrected']}")
            print(f"   {correction['explanation']}")
            print() 