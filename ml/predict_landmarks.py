import cv2
import mediapipe as mp
import numpy as np
import tensorflow as tf
from tensorflow import keras
import json
import os

class LandmarkPredictor2Hand:
    def __init__(self):
        self.model = None
        self.class_indices = None
        
        try:
            self.model = keras.models.load_model('ml/models/isl_landmark_2hand_best.h5')
            with open('ml/models/landmark_2hand_class_indices.json', 'r') as f:
                self.class_indices = json.load(f)
            self.two_hand_mode = True
            print("✅ 2-Hand Landmark Model Loaded")
        except:
            try:
                self.model = keras.models.load_model('ml/models/isl_landmark_best.h5')
                with open('ml/models/landmark_class_indices.json', 'r') as f:
                    self.class_indices = json.load(f)
                self.two_hand_mode = False
                print("✅ 1-Hand Landmark Model Loaded")
            except Exception as e:
                print(f"❌ Error loading model: {e}")
                print("Run training script first")
            
        # Initialize MediaPipe - always detect 2 hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,  # Detect both hands
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils

    def normalize_hand(self, landmarks):
        """Normalize hand landmarks (21x2 array)"""
        base_x, base_y = landmarks[0][0], landmarks[0][1]
        landmarks[:, 0] -= base_x
        landmarks[:, 1] -= base_y
        
        max_value = np.max(np.abs(landmarks))
        if max_value > 0:
            landmarks /= max_value
        
        return landmarks

    def predict(self, frame):
        if not self.model:
            return None, frame
            
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)
        
        prediction_text = "No Hand"
        confidence_text = ""
        hands_detected = 0
        
        if results.multi_hand_landmarks:
            hands_detected = len(results.multi_hand_landmarks)
            
            # Draw all detected hands
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
            
            # Extract landmarks for prediction
            hand_data = []
            for hand_landmarks in results.multi_hand_landmarks[:2]:
                landmarks = np.array([[lm.x, lm.y] for lm in hand_landmarks.landmark])
                normalized = self.normalize_hand(landmarks)
                hand_data.append(normalized.flatten())
            
            # Prepare input based on model type
            if self.two_hand_mode:
                # 2-hand model expects 84 features
                if len(hand_data) == 1:
                    input_data = np.concatenate([hand_data[0], np.zeros(42)])
                else:
                    input_data = np.concatenate([hand_data[0], hand_data[1]])
                input_data = input_data.reshape(1, 84)
            else:
                # 1-hand model expects 42 features - use first hand only
                input_data = hand_data[0].reshape(1, 42)
            
            # Predict
            preds = self.model.predict(input_data, verbose=0)[0]
            top_idx = np.argmax(preds)
            conf = preds[top_idx]
            
            label = self.class_indices.get(str(top_idx), "?")
            
            prediction_text = f"Sign: {label}"
            confidence_text = f"({conf*100:.1f}%)"
            
            # Visual display
            h, w, c = frame.shape
            cv2.rectangle(frame, (0,0), (350, 100), (0,0,0), -1)
            cv2.putText(frame, prediction_text, (10, 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)
            cv2.putText(frame, confidence_text, (10, 75), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 1)
            
            # Show hand count
            mode_text = "2-HAND" if self.two_hand_mode else "1-HAND"
            cv2.putText(frame, f"{mode_text} | Hands: {hands_detected}", 
                       (w-250, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
                
        return prediction_text, frame

    def close(self):
        self.hands.close()

def main():
    predictor = LandmarkPredictor2Hand()
    cap = cv2.VideoCapture(0)
    
    print("="*60)
    print("🤚 ISL Recognition - 2-Hand Support")
    print("="*60)
    print("Controls:")
    print("  • Press 'q' to quit")
    print("="*60 + "\n")
    
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        frame = cv2.flip(frame, 1)
        _, frame = predictor.predict(frame)
        
        cv2.imshow("ISL Recognition - 2-Hand Support", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()
    predictor.close()

if __name__ == "__main__":
    main()
