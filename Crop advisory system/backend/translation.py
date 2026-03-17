"""
Translation Module - Enhanced with Google Translate API
Provides accurate translation for agricultural terms
"""

try:
    from translation_service import translate_text as translate_with_service
    USE_NEW_SERVICE = True
except ImportError:
    USE_NEW_SERVICE = False
    print("Using fallback dictionary-based translation")

import re

# Fallback dictionary for basic translation
TRANSLATION_DICT = {
    "en": {
        "rice": "rice",
        "wheat": "wheat",
        "maize": "maize",
        "cotton": "cotton",
        "sugarcane": "sugarcane",
        "fertilizer": "fertilizer",
        "nitrogen": "nitrogen",
        "phosphorus": "phosphorus",
        "potassium": "potassium",
        "soil": "soil",
        "water": "water",
        "rain": "rain",
        "farmer": "farmer",
        "crop": "crop",
        "plant": "plant",
        "field": "field",
        "seed": "seed",
        "harvest": "harvest",
        "disease": "disease",
        "pest": "pest",
        "irrigation": "irrigation",
        "season": "season",
        "temperature": "temperature",
        "humidity": "humidity",
        "yield": "yield",
        "advice": "advice",
        "recommendation": "recommendation"
    },
    "hi": {
        "rice": "चावल",
        "wheat": "गेहूं",
        "maize": "मक्का",
        "cotton": "कपास",
        "sugarcane": "गन्ना",
        "fertilizer": "उर्वरक",
        "nitrogen": "नाइट्रोजन",
        "phosphorus": "फास्फोरस",
        "potassium": "पोटेशियम",
        "soil": "मिट्टी",
        "water": "पानी",
        "rain": "बारिश",
        "farmer": "किसान",
        "crop": "फसल",
        "plant": "पौधा",
        "field": "खेत",
        "seed": "बीज",
        "harvest": "कटाई",
        "disease": "रोग",
        "pest": "कीट",
        "irrigation": "सिंचाई",
        "season": "मौसम",
        "temperature": "तापमान",
        "humidity": "आर्द्रता",
        "yield": "उपज",
        "advice": "सलाह",
        "recommendation": "सिफारिश"
    },
    "te": {
        "rice": "vāri",
        "wheat": "gōdhūma",
        "maize": "mokkajonna",
        "cotton": "pattī",
        "sugarcane": "ceruku",
        "fertilizer": "eruvu",
        "nitrogen": "nātrajana",
        "phosphorus": "bhāsvaramu",
        "potassium": "pōṣiyamu",
        "soil": "nēla",
        "water": "nīru",
        "rain": "varṣamu",
        "farmer": "kṛṣi",
        "crop": "pannṭa",
        "plant": "pōta",
        "field": "pōla",
        "seed": "bīja",
        "harvest": "kāṇṭlu",
        "disease": "rogu",
        "pest": "tegu",
        "irrigation": "nīṭiparudā",
        "season": "kālaṃ",
        "temperature": "uṣṇagrāta",
        "humidity": "tēma",
        "yield": "digbu",
        "advice": "sāha",
        "recommendation": "sipāriśu"
    },
    "ta": {
        "rice": "nēl",
        "wheat": "kōtumai",
        "maize": "cōḷam",
        "cotton": "pattī",
        "sugarcane": "karumpu",
        "fertilizer": "ur",
        "nitrogen": "naitraja",
        "phosphorus": "pāspuras",
        "potassium": "potaci",
        "soil": "maṇ",
        "water": "neṟu",
        "rain": "mazai",
        "farmer": "veṭṭiyaṉ",
        "crop": "payir",
        "plant": "tēvaṉ",
        "field": "vayal",
        "seed": "vīṭu",
        "harvest": "pani",
        "disease": "noiy",
        "pest": "pūcci",
        "irrigation": "nīrpācaṉam",
        "season": "pārvam",
        "temperature": "veppnilai",
        "humidity": "īrappaṭam",
        "yield": "vilaiccāl",
        "advice": "ālocanai",
        "recommendation": "pariṉaraippu"
    }
}

import re

def translate_text(text, from_lang, to_lang):
    """
    Translate text between languages with agricultural term accuracy
    
    Args:
        text: Text to translate
        from_lang: Source language (en, hi, te, ta)
        to_lang: Target language (en, hi, te, ta)
        
    Returns:
        Translated text
    """
    if not text or not text.strip():
        return text
    
    if from_lang == to_lang:
        return text
    
    # Try using the new translation service first
    if USE_NEW_SERVICE:
        try:
            return translate_with_service(text, from_lang, to_lang)
        except Exception as e:
            print(f"Translation service error: {e}, using fallback")
    
    # Try direct googletrans
    try:
        from googletrans import Translator
        translator = Translator()
        lang_map = {'en': 'en', 'hi': 'hi', 'te': 'te', 'ta': 'ta'}
        result = translator.translate(text, src=lang_map.get(from_lang, 'en'), dest=lang_map.get(to_lang, 'te'))
        return result.text
    except Exception as e:
        print(f"Google Translate error: {e}")
    
    # Fallback to dictionary-based translation
    translated = text

    if from_lang == "en":
        target_dict = TRANSLATION_DICT.get(to_lang, {})
        for eng_word, trans_word in target_dict.items():
            pattern = re.compile(re.escape(eng_word), re.IGNORECASE)
            translated = pattern.sub(trans_word, translated)
    elif to_lang == "en":
        source_dict = TRANSLATION_DICT.get(from_lang, {})
        for eng_word, trans_word in source_dict.items():
            pattern = re.compile(re.escape(trans_word), re.IGNORECASE)
            translated = pattern.sub(eng_word, translated)
    else:
        temp_translated = text
        source_dict = TRANSLATION_DICT.get(from_lang, {})
        for eng_word, trans_word in source_dict.items():
            pattern = re.compile(re.escape(trans_word), re.IGNORECASE)
            temp_translated = pattern.sub(eng_word, temp_translated)

        target_dict = TRANSLATION_DICT.get(to_lang, {})
        for eng_word, trans_word in target_dict.items():
            pattern = re.compile(re.escape(eng_word), re.IGNORECASE)
            translated = pattern.sub(trans_word, temp_translated)

    return translated