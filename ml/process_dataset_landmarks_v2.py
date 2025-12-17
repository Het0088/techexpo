import os
import cv2
import numpy as np
import pandas as pd
import mediapipe as mp
from tqdm import tqdm

DATA_FILE = 'ml/dataset/isl_landmarks_2hands.csv'
DATASET_PATH = 'ml/dataset/isl_alphabets'

def normalize_hand(landmarks):
    base_x, base_y = landmarks[0][0], landmarks[0][1]
    landmarks[:, 0] -= base_x
    landmarks[:, 1] -= base_y
    
    max_value = np.max(np.abs(landmarks))
    if max_value > 0:
        landmarks /= max_value
    
    return landmarks

def process_images():
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=True,
        max_num_hands=2,
        min_detection_confidence=0.7
    )
    
    data = []
    labels = []
    
    classes = sorted([d for d in os.listdir(DATASET_PATH) 
                     if os.path.isdir(os.path.join(DATASET_PATH, d))])
    
    print(f"Processing {len(classes)} classes")
    
    for class_name in tqdm(classes):
        class_path = os.path.join(DATASET_PATH, class_name)
        images = [f for f in os.listdir(class_path) 
                 if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        for img_file in images:
            img_path = os.path.join(class_path, img_file)
            
            try:
                image = cv2.imread(img_path)
                if image is None:
                    continue
                
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb_image)
                
                if not results.multi_hand_landmarks:
                    continue
                
                hand_data = []
                for hand_landmarks in results.multi_hand_landmarks[:2]:
                    landmarks = np.array([[lm.x, lm.y] for lm in hand_landmarks.landmark])
                    normalized = normalize_hand(landmarks)
                    hand_data.append(normalized.flatten())
                
                if len(hand_data) == 1:
                    features = np.concatenate([hand_data[0], np.zeros(42)])
                else:
                    features = np.concatenate([hand_data[0], hand_data[1]])
                
                data.append(features)
                labels.append(class_name)
                
            except Exception as e:
                print(f"Error processing {img_path}: {e}")
                continue
    
    hands.close()
    
    df = pd.DataFrame(data)
    df['label'] = labels
    
    print(f"\nProcessed {len(df)} images successfully")
    print(f"Saving to {DATA_FILE}")
    
    df.to_csv(DATA_FILE, index=False)
    print("Done")

if __name__ == "__main__":
    process_images()
