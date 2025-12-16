"""
Enhanced Rule-Based ISL Converter
Comprehensive without external NLP libraries
"""

class EnhancedISLConverter:
    def __init__(self):
        # Grammar words to remove
        self.remove_words = {
            # Helping verbs
            'am', 'is', 'are', 'was', 'were', 'be', 'being', 'been',
            'have', 'has', 'had', 'do', 'does', 'did',
            # Articles
            'a', 'an', 'the',
            # Modals
            'will', 'would', 'should', 'could', 'may', 'might', 'must',
            'shall', 'can',
            # Fillers
            'very', 'really', 'just', 'quite', 'so', 'too', 'also'
        }
        
        # Comprehensive verb conversions
        self.verb_map = {
            # Present continuous → base
            'eating': 'eat', 'drinking': 'drink', 'sleeping': 'sleep',
            'running': 'run', 'walking': 'walk', 'talking': 'talk',
            'going': 'go', 'coming': 'come', 'doing': 'do',
            'making': 'make', 'taking': 'take', 'giving': 'give',
            'playing': 'play', 'working': 'work', 'studying': 'study',
            'learning': 'learn', 'teaching': 'teach', 'helping': 'help',
            'reading': 'read', 'writing': 'write', 'listening': 'listen',
            'watching': 'watch', 'looking': 'look', 'seeing': 'see',
            'thinking': 'think', 'knowing': 'know', 'understanding': 'understand',
            'speaking': 'speak', 'saying': 'say', 'telling': 'tell',
            'asking': 'ask', 'answering': 'answer', 'calling': 'call',
            'living': 'live', 'staying': 'stay', 'leaving': 'leave',
            'arriving': 'arrive', 'starting': 'start', 'stopping': 'stop',
            'buying': 'buy', 'selling': 'sell', 'paying': 'pay',
            'getting': 'get', 'bringing': 'bring', 'sending': 'send',
            'opening': 'open', 'closing': 'close', 'breaking': 'break',
            'cooking': 'cook', 'cleaning': 'clean', 'washing': 'wash',
            
            # Past tense → base
            'ate': 'eat', 'drank': 'drink', 'slept': 'sleep',
            'ran': 'run', 'walked': 'walk', 'talked': 'talk',
            'went': 'go', 'came': 'come', 'did': 'do',
            'made': 'make', 'took': 'take', 'gave': 'give',
            'played': 'play', 'worked': 'work', 'studied': 'study',
            'learned': 'learn', 'taught': 'teach', 'helped': 'help',
            'read': 'read', 'wrote': 'write', 'listened': 'listen',
            'watched': 'watch', 'looked': 'look', 'saw': 'see',
            'thought': 'think', 'knew': 'know', 'understood': 'understand',
            'spoke': 'speak', 'said': 'say', 'told': 'tell',
            'asked': 'ask', 'answered': 'answer', 'called': 'call',
            'lived': 'live', 'stayed': 'stay', 'left': 'leave',
            'arrived': 'arrive', 'started': 'start', 'stopped': 'stop',
            'bought': 'buy', 'sold': 'sell', 'paid': 'pay',
            'got': 'get', 'brought': 'bring', 'sent': 'send',
        }
        
        # Common contractions
        self.contractions = {
            "i'm": "i am", "i've": "i have", "i'll": "i will",
            "you're": "you are", "you've": "you have", "you'll": "you will",
            "he's": "he is", "he'll": "he will",
            "she's": "she is", "she'll": "she will",
            "it's": "it is", "it'll": "it will",
            "we're": "we are", "we've": "we have", "we'll": "we will",
            "they're": "they are", "they've": "they have", "they'll": "they will",
            "isn't": "is not", "aren't": "are not", "wasn't": "was not",
            "weren't": "were not", "haven't": "have not", "hasn't": "has not",
            "hadn't": "had not", "won't": "will not", "wouldn't": "would not",
            "don't": "do not", "doesn't": "does not", "didn't": "did not",
            "can't": "can not", "couldn't": "could not",
            "shouldn't": "should not", "mightn't": "might not",
        }
    
    def expand_contractions(self, text):
        """Expand contractions (I'm → I am)"""
        for contraction, expansion in self.contractions.items():
            text = text.replace(contraction, expansion)
        return text
    
    def convert(self, text):
        """Convert English to ISL grammar"""
        # Lowercase and expand contractions
        text = text.lower()
        text = self.expand_contractions(text)
        
        # Tokenize
        words = text.split()
        isl_words = []
        
        for word in words:
            # Remove punctuation
            word = word.strip('.,!?;:\'"')
            
            if not word:
                continue
            
            # Skip grammar words
            if word in self.remove_words:
                continue
            
            # Convert verbs to base form
            word = self.verb_map.get(word, word)
            
            isl_words.append(word)
        
        return isl_words

# Usage
if __name__ == "__main__":
    converter = EnhancedISLConverter()
    
    test_sentences = [
        "I'm eating the apple",
        "She was going to school",
        "They're playing football",
        "I have been working very hard",
        "He doesn't like coffee",
        "We went to the market yesterday"
    ]
    
    print("Enhanced Rule-Based ISL Conversion\n" + "="*60)
    for sentence in test_sentences:
        isl = converter.convert(sentence)
        print(f"\nInput:     {sentence}")
        print(f"ISL Gloss: {' '.join(isl).upper()}")
