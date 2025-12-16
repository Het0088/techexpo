"""
Process ISL Word Videos to Landmark Sequences
Extracts hand landmarks from video dataset for word recognition training
"""

import os
import cv2
import numpy as np
import mediapipe as mp
import pandas as pd
from tqdm import tqdm

# Configuration
DATASET_PATH = 'ml/dataset/isl_words'
OUTPUT_FILE = 'ml/dataset/isl_word_sequences.csv'
SEQUENCE_LENGTH = 30  # Frames per video
MIN_DETECTION_CONFIDENCE = 0.5

def normalize_hand(landmarks):
    """Normalize hand landmarks"""
    base_x, base_y = landmarks[0][0], landmarks[0][1]
    landmarks[:, 0] -= base_x
    landmarks[:, 1] -= base_y
    
    max_value = np.max(np.abs(landmarks))
    if max_value > 0:
        landmarks /= max_value
    
    return landmarks

def process_video(video_path, target_frames=30):
    """Extract landmark sequence from video"""
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=MIN_DETECTION_CONFIDENCE
    )
    
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Sample frames evenly
    frame_indices = np.linspace(0, total_frames-1, target_frames, dtype=int)
    
    sequence = []
    
    for frame_idx in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        
        if not ret:
            break
        
        # Convert to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)
        
        # Extract landmarks
        hand_data = []
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks[:2]:
                landmarks = np.array([[lm.x, lm.y] for lm in hand_landmarks.landmark])
                normalized = normalize_hand(landmarks)
                hand_data.append(normalized.flatten())
        
        # Create 84 features (2 hands)
        if len(hand_data) == 0:
            frame_features = np.zeros(84)
        elif len(hand_data) == 1:
            frame_features = np.concatenate([hand_data[0], np.zeros(42)])
        else:
            frame_features = np.concatenate([hand_data[0], hand_data[1]])
        
        sequence.append(frame_features)
    
    cap.release()
    hands.close()
    
    # Pad or truncate to target length
    while len(sequence) < target_frames:
        sequence.append(np.zeros(84))
    
    sequence = sequence[:target_frames]
    
    # Flatten: 30 frames × 84 features = 2520 features
    return np.array(sequence).flatten()

def main():
    print("="*60)
    print("Processing ISL Word Videos")
    print("="*60)
    print(f"\nDataset path: {DATASET_PATH}")
    
    # Get word folders
    word_folders = [d for d in os.listdir(DATASET_PATH) if os.path.isdir(os.path.join(DATASET_PATH, d))]
    
    print(f"Found {len(word_folders)} word categories:\n")
    for folder in word_folders:
        print(f"  - {folder}")
    
    data = []
    labels = []
    
    total_videos = 0
    successful = 0
    
    for word_folder in tqdm(word_folders, desc="Processing words"):
        word_path = os.path.join(DATASET_PATH, word_folder)
        
        # Get all video files
        video_files = [f for f in os.listdir(word_path) 
                      if f.lower().endswith(('.mp4', '.mov', '.avi'))]
        
        total_videos += len(video_files)
        
        for video_file in tqdm(video_files, desc=f"  {word_folder}", leave=False):
            video_path = os.path.join(word_path, video_file)
            
            try:
                sequence = process_video(video_path)
                
                if sequence is not None and len(sequence) == 2520:  # 30*84
                    data.append(sequence)
                    labels.append(word_folder)
                    successful += 1
            except Exception as e:
                print(f"\n⚠️  Error processing {video_file}: {e}")
    
    print(f"\n{'='*60}")
    print(f"Processing complete!")
    print(f"  Total videos: {total_videos}")
    print(f"  Successfully processed: {successful}")
    print(f"  Success rate: {successful/total_videos*100:.1f}%")
    
    if successful > 0:
        # Create DataFrame
        # Columns: frame0_h0_x0, frame0_h0_y0, ... frame29_h1_y20, label
        columns = []
        for frame_idx in range(SEQUENCE_LENGTH):
            for hand_idx in range(2):
                for point_idx in range(21):
                    columns.append(f'f{frame_idx}_h{hand_idx}_x{point_idx}')
                    columns.append(f'f{frame_idx}_h{hand_idx}_y{point_idx}')
        
        df = pd.DataFrame(data, columns=columns)
        df['label'] = labels
        
        print(f"\nSaving to {OUTPUT_FILE}...")
        df.to_csv(OUTPUT_FILE, index=False)
        print("✅ Dataset saved successfully!")
        print(f"\nDataset shape: {df.shape}")
        print(f"Classes: {df['label'].nunique()}")
        print(f"\nClass distribution:")
        print(df['label'].value_counts())
    else:
        print("\n❌ No videos were successfully processed!")

if __name__ == "__main__":
    main()
