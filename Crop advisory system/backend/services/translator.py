"""
Comprehensive Translation Service for Crop Advisory System
Supports full text translation using Google Translate API
"""

from googletrans import Translator
import logging

logger = logging.getLogger(__name__)

class TranslationService:
    """Service for translating text between multiple languages"""
    
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'hi': 'Hindi',
        'te': 'Telugu',
        'ta': 'Tamil',
        'kn': 'Kannada',
        'ml': 'Malayalam',
        'mr': 'Marathi',
        'bn': 'Bengali',
        'gu': 'Gujarati',
        'pa': 'Punjabi'
    }
    
    def __init__(self):
        self.translator = Translator()
        logger.info("Translation service initialized")
    
    def translate(self, text, target_lang='en', source_lang='auto'):
        """
        Translate text to target language
        
        Args:
            text: Text to translate
            target_lang: Target language code (en, hi, te, ta, etc.)
            source_lang: Source language code (auto for auto-detect)
            
        Returns:
            Translated text
        """
        if not text or not text.strip():
            return text
        
        if target_lang not in self.SUPPORTED_LANGUAGES:
            logger.warning(f"Unsupported target language: {target_lang}, defaulting to English")
            target_lang = 'en'
        
        try:
            result = self.translator.translate(text, dest=target_lang, src=source_lang)
            return result.text
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return text  # Return original text if translation fails
    
    def detect_language(self, text):
        """Detect the language of given text"""
        try:
            result = self.translator.detect(text)
            return result.lang
        except Exception as e:
            logger.error(f"Language detection error: {str(e)}")
            return 'en'
    
    def translate_dict(self, data_dict, target_lang='en'):
        """
        Translate all string values in a dictionary
        
        Args:
            data_dict: Dictionary with string values
            target_lang: Target language code
            
        Returns:
            Dictionary with translated values
        """
        if not isinstance(data_dict, dict):
            return data_dict
        
        translated = {}
        for key, value in data_dict.items():
            if isinstance(value, str):
                translated[key] = self.translate(value, target_lang)
            elif isinstance(value, dict):
                translated[key] = self.translate_dict(value, target_lang)
            elif isinstance(value, list):
                translated[key] = [
                    self.translate(item, target_lang) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                translated[key] = value
        
        return translated

# Global translator instance
_translator = None

def get_translator():
    """Get or create translator instance"""
    global _translator
    if _translator is None:
        _translator = TranslationService()
    return _translator

def translate_text(text, target_lang='en', source_lang='auto'):
    """Convenience function for translation"""
    translator = get_translator()
    return translator.translate(text, target_lang, source_lang)
