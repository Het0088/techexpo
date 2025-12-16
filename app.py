"""
Enhanced Flask Backend with Prediction Smoothing + NLP
For accurate predictions and English-to-ISL conversion
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import cv2
import numpy as np
import mediapipe as mp
import base64
import os
import json
from tensorflow import keras
from collections import deque, Counter

app = Flask(__name__, static_folder='.')
CORS(app)

# Model paths
ALPHABET_MODEL_PATH = 'ml/models/isl_landmark_2hand_best.h5'
ALPHABET_CLASS_PATH = 'ml/models/landmark_2hand_class_indices.json'
WORD_MODEL_PATH = 'ml/models/isl_words_best.h5'
WORD_CLASS_PATH = 'ml/models/word_class_indices.json'

class EnhancedISLPredictor:
    def __init__(self):
        self.alphabet_model = None
        self.word_model = None
        self.alphabet_classes = None
        self.word_classes = None
        self.sequence_buffer = []
        self.sequence_length = 30
        self.prediction_history = deque(maxlen=5)  # Smooth predictions
        
        # Load models
        try:
            if os.path.exists(ALPHABET_MODEL_PATH):
                self.alphabet_model = keras.models.load_model(ALPHABET_MODEL_PATH)
                print("✅ Alphabet model loaded")
            if os.path.exists(ALPHABET_CLASS_PATH):
                with open(ALPHABET_CLASS_PATH, 'r') as f:
                    self.alphabet_classes = json.load(f)
                print(f"✅ Alphabet classes: {len(self.alphabet_classes)}")
        except Exception as e:
            print(f"❌ Alphabet model error: {e}")
        
        try:
            if os.path.exists(WORD_MODEL_PATH):
                self.word_model = keras.models.load_model(WORD_MODEL_PATH)
                print("✅ Word model loaded")
            if os.path.exists(WORD_CLASS_PATH):
                with open(WORD_CLASS_PATH, 'r') as f:
                    self.word_classes = json.load(f)
                print(f"✅ Word classes: {len(self.word_classes)}")
        except Exception as e:
            print(f"❌ Word model error: {e}")
        
        # MediaPipe
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
    
    def normalize_hand(self, landmarks):
        """Normalize landmarks"""
        base_x, base_y = landmarks[0][0], landmarks[0][1]
        landmarks[:, 0] -= base_x
        landmarks[:, 1] -= base_y
        
        max_value = np.max(np.abs(landmarks))
        if max_value > 0:
            landmarks /= max_value
        
        return landmarks
    
    def extract_features(self, image):
        """Extract 84 features"""
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)
        
        if not results.multi_hand_landmarks:
            return None
        
        hand_data = []
        for hand_landmarks in results.multi_hand_landmarks[:2]:
            landmarks = np.array([[lm.x, lm.y] for lm in hand_landmarks.landmark])
            normalized = self.normalize_hand(landmarks)
            hand_data.append(normalized.flatten())
        
        if len(hand_data) == 1:
            features = np.concatenate([hand_data[0], np.zeros(42)])
        else:
            features = np.concatenate([hand_data[0], hand_data[1]])
        
        return features
    
    def predict_alphabet(self, image):
        """Predict alphabet with smoothing"""
        if self.alphabet_model is None:
            return {'error': 'Model not loaded'}
        
        features = self.extract_features(image)
        if features is None:
            return {'error': 'No hand detected'}
        
        input_data = features.reshape(1, 84)
        preds = self.alphabet_model.predict(input_data, verbose=0)[0]
        
        # Apply confidence threshold
        if preds.max() < 0.6:  # Below 60% confidence
            return {
                'letter': '?',
                'confidence': float(preds.max()),
                'message': 'Low confidence - hold steady',
                'top_predictions': []
            }
        
        top_3_idx = np.argsort(preds)[-3:][::-1]
        
        return {
            'letter': self.alphabet_classes.get(str(top_3_idx[0]), '?'),
            'confidence': float(preds[top_3_idx[0]]),
            'top_predictions': [
                {
                    'letter': self.alphabet_classes.get(str(idx), '?'),
                    'confidence': float(preds[idx])
                }
                for idx in top_3_idx
            ]
        }
    
    def predict_word(self, image):
        """Predict word with smoothing"""
        if self.word_model is None:
            return {'error': 'Word model not loaded', 'ready': False}
        
        features = self.extract_features(image)
        if features is None:
            return {
                'ready': False,
                'buffer_size': len(self.sequence_buffer),
                'message': 'No hand detected'
            }
        
        self.sequence_buffer.append(features)
        
        if len(self.sequence_buffer) > self.sequence_length:
            self.sequence_buffer.pop(0)
        
        if len(self.sequence_buffer) == self.sequence_length:
            sequence = np.array(self.sequence_buffer).reshape(1, 30, 84)
            preds = self.word_model.predict(sequence, verbose=0)[0]
            
            top_idx = np.argmax(preds)
            confidence = float(preds[top_idx])
            word = self.word_classes.get(str(top_idx), '?')
            
            # Add to history for smoothing
            self.prediction_history.append((word, confidence))
            
            # Smooth predictions - use most common word in last 5 predictions
            if len(self.prediction_history) >= 3:
                words = [w for w, c in self.prediction_history if c > 0.5]
                if words:
                    smoothed_word = Counter(words).most_common(1)[0][0]
                    avg_confidence = np.mean([c for w, c in self.prediction_history if w == smoothed_word])
                else:
                    smoothed_word = word
                    avg_confidence = confidence
            else:
                smoothed_word = word
                avg_confidence = confidence
            
            # Only return if confidence is reasonable
            if avg_confidence < 0.4:
                return {
                    'ready': True,
                    'word': '?',
                    'confidence': avg_confidence,
                    'message': 'Low confidence - sign more clearly',
                    'buffer_size': len(self.sequence_buffer)
                }
            
            return {
                'word': smoothed_word,
                'confidence': avg_confidence,
                'ready': True,
                'buffer_size': len(self.sequence_buffer)
            }
        else:
            progress = int((len(self.sequence_buffer) / self.sequence_length) * 100)
            return {
                'ready': False,
                'buffer_size': len(self.sequence_buffer),
                'progress': progress,
               'message': f'Capturing gesture... {progress}%'
            }
    
    def reset_sequence(self):
        self.sequence_buffer = []
        self.prediction_history.clear()

predictor = EnhancedISLPredictor()

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/predict/alphabet', methods=['POST'])
def predict_alphabet():
    try:
        data = request.get_json()
        if 'image' not in data:
            return jsonify({'error': 'No image'}), 400
        
        img_data = base64.b64decode(data['image'].split(',')[1] if ',' in data['image'] else data['image'])
        nparr = np.frombuffer(img_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return jsonify({'error': 'Invalid image'}), 400
        
        result = predictor.predict_alphabet(image)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict/word', methods=['POST'])
def predict_word():
    try:
        data = request.get_json()
        if 'image' not in data:
            return jsonify({'error': 'No image'}), 400
        
        img_data = base64.b64decode(data['image'].split(',')[1] if ',' in data['image'] else data['image'])
        nparr = np.frombuffer(img_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return jsonify({'error': 'Invalid image'}), 400
        
        result = predictor.predict_word(image)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reset', methods=['POST'])
def reset():
    predictor.reset_sequence()
    return jsonify({'status': 'success'})

def english_to_isl_gloss(text):
    """Convert English to ISL grammar using simple rules"""
    
    # Words ISL doesn't use
    remove_words = {
        # Helping verbs
        'am', 'is', 'are', 'was', 'were', 'be', 'being', 'been',
        'have', 'has', 'had', 'do', 'does', 'did',
        # Articles
        'a', 'an', 'the',
        # Modals
        'will', 'would', 'should', 'could', 'may', 'might',
        # Fillers
        'very', 'really', 'just', 'quite', 'so'
    }
    
    # Verb conversions (progressive → base form)
    verb_map = {
        'eating': 'eat', 'running': 'run', 'going': 'go', 'coming': 'come',
        'doing': 'do', 'making': 'make', 'taking': 'take', 'giving': 'give',
        'playing': 'play', 'working': 'work', 'studying': 'study',
        'learning': 'learn', 'teaching': 'teach', 'helping': 'help',
        'walking': 'walk', 'talking': 'talk', 'sleeping': 'sleep',
        'reading': 'read', 'writing': 'write', 'listening': 'listen'
    }
    
    # Process
    words = text.lower().split()
    isl_words = []
    
    for word in words:
        # Remove punctuation
        word = word.strip('.,!?;:')
        
        if not word:
            continue
        
        # Skip grammar words
        if word in remove_words:
            continue
        
        # Convert verb forms
        isl_words.append(verb_map.get(word, word))
    
    return isl_words if isl_words else text.lower().split()

@app.route('/api/text-to-sign', methods=['POST'])
def text_to_sign():
    """Convert English text to ISL signs with NLP"""
    try:
        data = request.get_json()
        english_text = data.get('text', '').strip()
        
        if not english_text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Convert English to ISL grammar
        isl_words = english_to_isl_gloss(english_text)
        
        signs = []
        for word in isl_words:
            signs.append({
                'word': word,
                'type': 'alphabet',
                'letters': list(word)
            })
        
        return jsonify({
            'original': english_text,
            'isl_gloss': ' '.join(isl_words).upper(),
            'signs': signs,
            'message': f'Converted: "{english_text}" → ISL: "{" ".join(isl_words).upper()}"'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/css/<path:path>')
def serve_css(path):
    return send_from_directory('css', path)

@app.route('/js/<path:path>')
def serve_js(path):
    return send_from_directory('js', path)

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'alphabet_model': predictor.alphabet_model is not None,
        'word_model': predictor.word_model is not None
    })

if __name__ == '__main__':
    print("="*60)
    print("🚀 Enhanced ISL Recognition Server")
    print("="*60)
    print(f"\nServer: http://localhost:5000")
    print(f"\n📊 Models:")
    print(f"   Alphabet: {'✅' if predictor.alphabet_model else '❌'}")
    print(f"   Words: {'✅' if predictor.word_model else '❌'}")
    
    if predictor.word_classes:
        print(f"\n📝 Words ({len(predictor.word_classes)}):")
        for word in sorted(predictor.word_classes.values())[:5]:
            print(f"   • {word}")
        if len(predictor.word_classes) > 5:
            print(f"   ... and {len(predictor.word_classes)-5} more")
    
    print("\n" + "="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
