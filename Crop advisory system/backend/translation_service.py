"""
Enhanced Translation Service for Agricultural Terms
Uses Google Translate API with custom agricultural dictionary for accuracy
"""

try:
    from googletrans import Translator
    GOOGLETRANS_AVAILABLE = True
except ImportError:
    GOOGLETRANS_AVAILABLE = False
    print("Warning: googletrans not installed. Install with: pip install googletrans==4.0.0-rc1")

# Agricultural terms dictionary for accurate translation
AGRICULTURAL_TERMS = {
    "en_to_te": {
        # Crops
        "rice": "వరి",
        "wheat": "గోధుమ",
        "maize": "మొక్కజొన్న",
        "corn": "మొక్కజొన్న",
        "cotton": "పత్తి",
        "sugarcane": "చెరకు",
        "chickpea": "శనగలు",
        "kidney beans": "రాజ్మా",
        "pigeon peas": "కందులు",
        "mung bean": "పెసలు",
        "black gram": "మినుములు",
        "lentil": "కందిపప్పు",
        "banana": "అరటి",
        "mango": "మామిడి",
        "grapes": "ద్రాక్ష",
        "watermelon": "పుచ్చకాయ",
        "apple": "ఆపిల్",
        "orange": "నారింజ",
        "coconut": "కొబ్బరి",
        "coffee": "కాఫీ",
        
        # Nutrients
        "nitrogen": "నత్రజని",
        "phosphorus": "భాస్వరం",
        "potassium": "పొటాషియం",
        "fertilizer": "ఎరువు",
        "urea": "యూరియా",
        "NPK": "ఎన్‌పీకే",
        
        # Farming terms
        "soil": "నేల",
        "water": "నీరు",
        "rain": "వర్షం",
        "rainfall": "వర్షపాతం",
        "farmer": "రైతు",
        "crop": "పంట",
        "plant": "మొక్క",
        "field": "పొలం",
        "seed": "విత్తనం",
        "harvest": "కోత",
        "disease": "వ్యాధి",
        "pest": "చీడపురుగు",
        "irrigation": "నీటిపారుదల",
        "season": "కాలం",
        "temperature": "ఉష్ణోగ్రత",
        "humidity": "తేమ",
        "yield": "దిగుబడి",
        "advice": "సలహా",
        "recommendation": "సిఫార్సు",
        "analysis": "విశ్లేషణ",
        "prediction": "అంచనా",
        "weather": "వాతావరణం",
        "cultivation": "సాగు",
        "sowing": "విత్తడం",
        "planting": "నాటడం",
        "growth": "పెరుగుదల",
        "maturity": "పరిపక్వత",
        "organic": "సేంద్రీయ",
        "pesticide": "పురుగుమందు",
        "herbicide": "కలుపు మందు",
        "fungicide": "శిలీంధ్ర నాశిని"
    },
    "te_to_en": {}  # Will be auto-generated
}

# Auto-generate reverse dictionary
for en_word, te_word in AGRICULTURAL_TERMS["en_to_te"].items():
    AGRICULTURAL_TERMS["te_to_en"][te_word] = en_word


class TranslationService:
    """Enhanced translation service with agricultural term support"""
    
    def __init__(self):
        self.translator = None
        if GOOGLETRANS_AVAILABLE:
            try:
                self.translator = Translator()
            except Exception as e:
                print(f"Failed to initialize translator: {e}")
                self.translator = None
    
    def _replace_agricultural_terms(self, text, from_lang, to_lang):
        """Replace agricultural terms with accurate translations"""
        if from_lang == "en" and to_lang == "te":
            terms_dict = AGRICULTURAL_TERMS["en_to_te"]
        elif from_lang == "te" and to_lang == "en":
            terms_dict = AGRICULTURAL_TERMS["te_to_en"]
        else:
            return text
        
        # Sort by length (longest first) to avoid partial replacements
        sorted_terms = sorted(terms_dict.items(), key=lambda x: len(x[0]), reverse=True)
        
        result = text
        for original, translation in sorted_terms:
            # Case-insensitive replacement
            import re
            pattern = re.compile(re.escape(original), re.IGNORECASE)
            result = pattern.sub(translation, result)
        
        return result
    
    def translate(self, text, from_lang="en", to_lang="te"):
        """
        Translate text with agricultural term accuracy
        
        Args:
            text: Text to translate
            from_lang: Source language code (en, te, hi, ta)
            to_lang: Target language code (en, te, hi, ta)
            
        Returns:
            Translated text
        """
        if not text or not text.strip():
            return text
        
        if from_lang == to_lang:
            return text
        
        # First, replace known agricultural terms
        text_with_terms = self._replace_agricultural_terms(text, from_lang, to_lang)
        
        # If Google Translate is available, use it for remaining text
        if self.translator and GOOGLETRANS_AVAILABLE:
            try:
                # Map language codes
                lang_map = {
                    "en": "en",
                    "te": "te",
                    "hi": "hi",
                    "ta": "ta"
                }
                
                src_lang = lang_map.get(from_lang, "en")
                dest_lang = lang_map.get(to_lang, "te")
                
                # Translate
                result = self.translator.translate(
                    text_with_terms,
                    src=src_lang,
                    dest=dest_lang
                )
                
                return result.text
            except Exception as e:
                print(f"Translation error: {e}")
                # Fallback to term-replaced text
                return text_with_terms
        else:
            # Fallback to dictionary-based translation
            return text_with_terms


# Global translator instance
_translator_instance = None

def get_translator():
    """Get or create translator instance"""
    global _translator_instance
    if _translator_instance is None:
        _translator_instance = TranslationService()
    return _translator_instance


def translate_text(text, from_lang="en", to_lang="te"):
    """
    Convenience function for translation
    
    Args:
        text: Text to translate
        from_lang: Source language (en, te, hi, ta)
        to_lang: Target language (en, te, hi, ta)
        
    Returns:
        Translated text
    """
    translator = get_translator()
    return translator.translate(text, from_lang, to_lang)


# Test function
if __name__ == "__main__":
    print("Testing Translation Service...")
    
    test_texts = [
        "Rice cultivation requires proper irrigation and fertilizer",
        "Apply nitrogen fertilizer for better crop yield",
        "The farmer should monitor soil health regularly"
    ]
    
    for text in test_texts:
        print(f"\nOriginal (EN): {text}")
        translated = translate_text(text, "en", "te")
        print(f"Telugu: {translated}")
        back_translated = translate_text(translated, "te", "en")
        print(f"Back to EN: {back_translated}")
