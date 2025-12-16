"""
English to ISL Converter using NLTK
Lighter alternative to spaCy
"""

def install_nltk_data():
    """Download required NLTK data (run once)"""
    import nltk
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('taggers/averaged_perceptron_tagger')
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('punkt')
        nltk.download('averaged_perceptron_tagger')
        nltk.download('wordnet')
        nltk.download('omw-1.4')

def english_to_isl_nltk(text):
    """Convert English to ISL using NLTK"""
    import nltk
    from nltk.stem import WordNetLemmatizer
    from nltk.corpus import wordnet
    
    # Initialize
    lemmatizer = WordNetLemmatizer()
    
    # Tokenize
    tokens = nltk.word_tokenize(text.lower())
    
    # POS tagging
    pos_tags = nltk.pos_tag(tokens)
    
    isl_words = []
    
    for word, pos in pos_tags:
        # Remove punctuation
        if not word.isalnum():
            continue
        
        # Convert POS tag to WordNet format
        if pos.startswith('V'):  # Verb
            wordnet_pos = wordnet.VERB
        elif pos.startswith('N'):  # Noun
            wordnet_pos = wordnet.NOUN
        elif pos.startswith('J'):  # Adjective
            wordnet_pos = wordnet.ADJ
        elif pos.startswith('R'):  # Adverb
            wordnet_pos = wordnet.ADV
        else:
            wordnet_pos = None
        
        # Skip ISL grammar words
        skip_words = {'am', 'is', 'are', 'was', 'were', 'be', 'being', 'been',
                     'a', 'an', 'the', 'will', 'would', 'should', 'could',
                     'have', 'has', 'had', 'do', 'does', 'did'}
        
        if word in skip_words:
            continue
        
        # Lemmatize (convert to base form)
        if wordnet_pos:
            lemma = lemmatizer.lemmatize(word, wordnet_pos)
        else:
            lemma = word
        
        # Only keep content words
        if pos.startswith(('N', 'V', 'J', 'R', 'PRP')):  # Noun, Verb, Adj, Adv, Pronoun
            isl_words.append(lemma)
    
    return isl_words

# Usage
if __name__ == "__main__":
    # Install data first (run once)
    install_nltk_data()
    
    # Test
    sentences = [
        "I am eating the apple",
        "She was going to school",
        "They are playing football"
    ]
    
    print("NLTK-Based ISL Conversion\n" + "="*50)
    for sentence in sentences:
        isl = english_to_isl_nltk(sentence)
        print(f"\nInput:     {sentence}")
        print(f"ISL Gloss: {' '.join(isl).upper()}")
