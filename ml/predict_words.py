import cv2
import numpy as np
import mediapipe as mp
from tensorflow import keras
import json
from collections import deque, Counter

MODEL_PATH = 'ml/models/isl_words_velocity_best.h5'
CLASSES_PATH = 'ml/models/word_class_indices_velocity.json'

class WordPredictor:
    def __init__(self):
        print("Loading word recognition model...")
        self.model = keras.models.load_model(MODEL_PATH)
        
        with open(CLASSES_PATH, 'r') as f:
            self.class_indices = json.load(f)
        
        print(f"Loaded model with {len(self.class_indices)} word classes")
        
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        self.mp_drawing = mp.solutions.drawing_utils
        
        self.sequence_buffer = []
        self.sequence_length = 30
        self.prediction_history = deque(maxlen=5)
        self.previous_features = None
        
        self.confidence_threshold = 0.6
        self.movement_threshold = 0.015
    
    def normalize_hand(self, landmarks):
        base_x, base_y = landmarks[0][0], landmarks[0][1]
        landmarks[:, 0] -= base_x
        landmarks[:, 1] -= base_y
        
        max_value = np.max(np.abs(landmarks))
        if max_value > 0:
            landmarks /= max_value
        
        return landmarks
    
    def extract_features(self, image):
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)
        
        if not results.multi_hand_landmarks:
            return None, results
        
        hand_data = []
        for hand_landmarks in results.multi_hand_landmarks[:2]:
            landmarks = np.array([[lm.x, lm.y] for lm in hand_landmarks.landmark])
            normalized = self.normalize_hand(landmarks)
            hand_data.append(normalized.flatten())
        
        if len(hand_data) == 1:
            position_features = np.concatenate([hand_data[0], np.zeros(42)])
        else:
            position_features = np.concatenate([hand_data[0], hand_data[1]])
        
        if self.previous_features is None:
            velocity_features = np.zeros(84)
        else:
            velocity_features = position_features - self.previous_features
        
        self.previous_features = position_features.copy()
        
        combined_features = np.concatenate([position_features, velocity_features])
        
        return combined_features, results
    
    def calculate_movement(self, sequence):
        if len(sequence) < 2:
            return 0.0
        
        total_movement = 0.0
        for i in range(1, len(sequence)):
            diff = np.abs(sequence[i] - sequence[i-1])
            total_movement += np.sum(diff)
        
        avg_movement = total_movement / (len(sequence) - 1)
        return avg_movement
    
    def predict_word(self, features):
        if features is None:
            return None, 0.0, "No hand detected", 0.0
        
        self.sequence_buffer.append(features)
        
        if len(self.sequence_buffer) > self.sequence_length:
            self.sequence_buffer.pop(0)
        
        buffer_progress = (len(self.sequence_buffer) / self.sequence_length) * 100
        
        if len(self.sequence_buffer) < self.sequence_length:
            return None, 0.0, f"Capturing: {int(buffer_progress)}%", 0.0
        
        movement = self.calculate_movement(self.sequence_buffer)
        
        if movement < self.movement_threshold:
            return "No movement", 0.0, f"Movement too low", movement
        
        sequence = np.array(self.sequence_buffer).reshape(1, self.sequence_length, 168)
        predictions = self.model.predict(sequence, verbose=0)[0]
        
        top_idx = np.argmax(predictions)
        confidence = float(predictions[top_idx])
        predicted_word = self.class_indices.get(str(top_idx), "Unknown")
        
        self.prediction_history.append((predicted_word, confidence))
        
        if len(self.prediction_history) >= 3:
            high_conf_words = [w for w, c in self.prediction_history if c > 0.5]
            if high_conf_words:
                smoothed_word = Counter(high_conf_words).most_common(1)[0][0]
                avg_confidence = np.mean([c for w, c in self.prediction_history if w == smoothed_word])
                return smoothed_word, avg_confidence, "Prediction ready", movement
        
        if confidence < self.confidence_threshold:
            return "Low confidence", confidence, f"Conf: {confidence:.2f}", movement
        
        return predicted_word, confidence, "Prediction ready", movement
    
    def reset_sequence(self):
        self.sequence_buffer = []
        self.prediction_history.clear()
        self.previous_features = None
    
    def draw_landmarks(self, image, results):
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS
                )
        return image

def test_on_webcam():
    predictor = WordPredictor()
    
    print("\nRecognizable words:")
    for idx, word in sorted(predictor.class_indices.items(), key=lambda x: x[1]):
        print(f"  - {word}")
    
    print(f"\nMovement threshold: {predictor.movement_threshold}")
    print(f"Confidence threshold: {predictor.confidence_threshold}")
    print("\nStarting webcam...")
    print("Press 'r' to reset sequence")
    print("Press 'q' to quit")
    print("Press '+' to increase movement threshold")
    print("Press '-' to decrease movement threshold")
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
        
        frame = cv2.flip(frame, 1)
        
        features, results = predictor.extract_features(frame)
        frame = predictor.draw_landmarks(frame, results)
        
        word, confidence, status, movement = predictor.predict_word(features)
        
        buffer_size = len(predictor.sequence_buffer)
        progress = int((buffer_size / predictor.sequence_length) * 100)
        
        if buffer_size >= predictor.sequence_length:
            movement_color = (0, 255, 0) if movement >= predictor.movement_threshold else (0, 0, 255)
            cv2.putText(frame, f"Movement: {movement:.4f}", 
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, movement_color, 2)
        else:
            cv2.putText(frame, f"Buffer: {buffer_size}/{predictor.sequence_length} ({progress}%)", 
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        cv2.putText(frame, f"Threshold: {predictor.movement_threshold:.4f}", 
                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        if word and word not in ["No movement", "Low confidence"]:
            color = (0, 255, 0) if confidence > 0.6 else (0, 165, 255)
            cv2.putText(frame, f"Word: {word}", 
                        (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
            cv2.putText(frame, f"Confidence: {confidence*100:.1f}%", 
                        (10, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        else:
            cv2.putText(frame, status, 
                        (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        cv2.putText(frame, "r=reset | q=quit | +/- adjust threshold", 
                    (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        cv2.imshow('ISL Word Recognition with Velocity', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            predictor.reset_sequence()
            print("Sequence reset")
        elif key == ord('+') or key == ord('='):
            predictor.movement_threshold += 0.005
            print(f"Movement threshold: {predictor.movement_threshold:.4f}")
        elif key == ord('-') or key == ord('_'):
            predictor.movement_threshold = max(0.001, predictor.movement_threshold - 0.005)
            print(f"Movement threshold: {predictor.movement_threshold:.4f}")
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_on_webcam()
