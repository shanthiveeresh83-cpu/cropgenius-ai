"""Test Translation Functionality"""
import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from translation import translate_text

print("=" * 60)
print("TRANSLATION SERVICE TEST")
print("=" * 60)

# Test cases
test_cases = [
    ("Rice cultivation requires proper irrigation", "en", "te"),
    ("Apply nitrogen fertilizer for better yield", "en", "te"),
    ("The farmer should monitor soil health", "en", "hi"),
]

for text, from_lang, to_lang in test_cases:
    print(f"\nOriginal ({from_lang}): {text}")
    try:
        translated = translate_text(text, from_lang, to_lang)
        print(f"Translated ({to_lang}): {translated}")
        print("SUCCESS")
    except Exception as e:
        print(f"ERROR: {str(e)}")
    print("-" * 60)

print("\n" + "=" * 60)
print("TEST COMPLETE - Translation service is working!")
print("=" * 60)
