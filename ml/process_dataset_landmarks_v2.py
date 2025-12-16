"""
Enhanced landmark extraction supporting BOTH hands.
Handles 1-handed and 2-handed signs by always outputting 84 features.
"""

import os
import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
from tqdm import tqdm

# Configuration
DATASET_PATH = 'ml/dataset/isl_alphabets'
OUTPUT_FILE = 'ml/dataset/isl_landmarks_2hands.csv'
MIN_DETECTION_CONFIDENCE = 0.5

def normalize_hand_landmarks(landmarks):
    """Normalize landmarks relative to wrist and scale-invariant"""
    # landmarks is array of shape (21, 2)
    base_x, base_y = landmarks[0][0], landmarks[0][1]
    landmarks[:, 0] -= base_x
    landmarks[:, 1] -= base_y
    
    max_value = np.max(np.abs(landmarks))
    if max_value > 0:
        landmarks /= max_value
    
    return landmarks

def process_dataset():
    # Initialize MediaPipe Hands - NOW WITH 2 HANDS!
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=True,
        max_num_hands=2,  # Detect BOTH hands
        min_detection_confidence=MIN_DETECTION_CONFIDENCE
    )

    data = []
    labels = []
    
    if not os.path.exists(DATASET_PATH):
        print(f"Error: Dataset path '{DATASET_PATH}' does not exist.")
        return

    classes = sorted([d for d in os.listdir(DATASET_PATH) if os.path.isdir(os.path.join(DATASET_PATH, d))])
    print(f"Found {len(classes)} classes: {classes}")
    print(f"Processing with 2-hand support...")

    valid_images = 0
    total_images = 0

    for class_name in tqdm(classes, desc="Processing Classes"):
        class_path = os.path.join(DATASET_PATH, class_name)
        image_files = [f for f in os.listdir(class_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        for img_file in image_files:
            total_images += 1
            img_path = os.path.join(class_path, img_file)
            image = cv2.imread(img_path)
            
            if image is None:
                continue

            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = hands.process(image_rgb)
            
            if results.multi_hand_landmarks:
                # Extract up to 2 hands
                hand_data = []
                
                for hand_landmarks in results.multi_hand_landmarks[:2]:  # Max 2 hands
                    landmarks = np.array([[lm.x, lm.y] for lm in hand_landmarks.landmark])
                    normalized = normalize_hand_landmarks(landmarks)
                    hand_data.append(normalized.flatten())  # 42 features per hand
                
                # Always create 84 features (2 hands worth)
                if len(hand_data) == 1:
                    # Only 1 hand detected - pad with zeros for second hand
                    row = np.concatenate([hand_data[0], np.zeros(42)])
                elif len(hand_data) == 2:
                    # Both hands detected
                    row = np.concatenate([hand_data[0], hand_data[1]])
                else:
                    continue  # No hands (shouldn't happen but safety check)
                
                data.append(row.tolist())
                labels.append(class_name)
                valid_images += 1

    hands.close()

    print(f"\nProcessing complete.")
    print(f"Total processed: {total_images}")
    print(f"Successfully extracted: {valid_images} ({valid_images/total_images*100:.1f}%)")
    
    if valid_images > 0:
        # Create DataFrame with 84 columns (2 hands × 21 landmarks × 2 coords)
        cols = []
        for hand_idx in range(2):
            for point_idx in range(21):
                cols.extend([f'h{hand_idx}_x{point_idx}', f'h{hand_idx}_y{point_idx}'])
        
        df = pd.DataFrame(data, columns=cols)
        df['label'] = labels
        
        print(f"Saving to {OUTPUT_FILE}...")
        df.to_csv(OUTPUT_FILE, index=False)
        print("✅ Done! Dataset now supports 2-handed signs.")
    else:
        print("❌ No valid hands detected.")

if __name__ == "__main__":
    process_dataset()
