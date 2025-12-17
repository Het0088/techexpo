"""
Test spaCy installation and ISL conversion
"""

try:
    import spacy
    print("✅ spaCy imported successfully")
    
    # Load model
    print("Loading en_core_web_sm model...")
    nlp = spacy.load("en_core_web_sm")
    print("✅ Model loaded successfully!\n")
    
    # Test ISL conversion
    def english_to_isl_spacy(text):
        doc = nlp(text)
        isl_words = []
        
        for token in doc:
            if token.pos_ in ['NOUN', 'VERB', 'ADJ', 'PRON', 'ADV', 'PROPN', 'NUM']:
                word = token.lemma_ if token.pos_ == 'VERB' else token.text
                if word.isalnum():
                    isl_words.append(word.lower())
        
        return isl_words
    
    # Test sentences
    test_sentences = [
        "I am sorry",
        "He is eating the apple",
        "She was going to school",
        "They are playing football"
    ]
    
    print("="*60)
    print("spaCy ISL Conversion Test")
    print("="*60)
    
    for sentence in test_sentences:
        isl = english_to_isl_spacy(sentence)
        print(f"\nInput:     {sentence}")
        print(f"ISL Gloss: {' '.join(isl).upper()}")
    
    print("\n" + "="*60)
    print("✅ spaCy is working perfectly!")
    print("="*60)

except ImportError:
    print("❌ spaCy not installed")
    print("Run: pip install spacy")
    
except OSError:
    print("❌ Model not found")
    print("\nInstall with:")
    print("pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl")
    
except Exception as e:
    print(f"❌ Error: {e}")
