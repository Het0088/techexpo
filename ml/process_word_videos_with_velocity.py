import os
import cv2
import numpy as np
import mediapipe as mp
import pandas as pd
from tqdm import tqdm

DATASET_PATH = 'ml/dataset/isl_words'
OUTPUT_FILE = 'ml/dataset/isl_word_sequences_with_velocity.csv'
SEQUENCE_LENGTH = 30
MIN_DETECTION_CONFIDENCE = 0.5

def normalize_hand(landmarks):
    base_x, base_y = landmarks[0][0], landmarks[0][1]
    landmarks[:, 0] -= base_x
    landmarks[:, 1] -= base_y
    
    max_value = np.max(np.abs(landmarks))
    if max_value > 0:
        landmarks /= max_value
    
    return landmarks

def calculate_velocity(current_landmarks, previous_landmarks):
    if previous_landmarks is None:
        return np.zeros_like(current_landmarks)
    
    velocity = current_landmarks - previous_landmarks
    return velocity

def process_video(video_path, target_frames=30):
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=MIN_DETECTION_CONFIDENCE
    )
    
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    frame_indices = np.linspace(0, total_frames-1, target_frames, dtype=int)
    
    sequence_positions = []
    sequence_velocities = []
    previous_frame_features = None
    
    for frame_idx in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        
        if not ret:
            break
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)
        
        hand_data = []
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks[:2]:
                landmarks = np.array([[lm.x, lm.y] for lm in hand_landmarks.landmark])
                normalized = normalize_hand(landmarks)
                hand_data.append(normalized.flatten())
        
        if len(hand_data) == 0:
            current_features = np.zeros(84)
        elif len(hand_data) == 1:
            current_features = np.concatenate([hand_data[0], np.zeros(42)])
        else:
            current_features = np.concatenate([hand_data[0], hand_data[1]])
        
        velocity_features = calculate_velocity(current_features, previous_frame_features)
        
        sequence_positions.append(current_features)
        sequence_velocities.append(velocity_features)
        
        previous_frame_features = current_features.copy()
    
    cap.release()
    hands.close()
    
    while len(sequence_positions) < target_frames:
        sequence_positions.append(np.zeros(84))
        sequence_velocities.append(np.zeros(84))
    
    sequence_positions = sequence_positions[:target_frames]
    sequence_velocities = sequence_velocities[:target_frames]
    
    combined_features = []
    for pos, vel in zip(sequence_positions, sequence_velocities):
        frame_features = np.concatenate([pos, vel])
        combined_features.append(frame_features)
    
    return np.array(combined_features).flatten()

def main():
    print("="*60)
    print("Processing ISL Word Videos with Movement Features")
    print("="*60)
    print(f"\nDataset path: {DATASET_PATH}")
    print("\nFeature extraction:")
    print("  - Position: 84 features per frame")
    print("  - Velocity: 84 features per frame")
    print("  - Total: 168 features per frame")
    print(f"  - Sequence: {SEQUENCE_LENGTH} frames")
    print(f"  - Final: {SEQUENCE_LENGTH * 168} = 5,040 features per video\n")
    
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
        
        video_files = [f for f in os.listdir(word_path) 
                      if f.lower().endswith(('.mp4', '.mov', '.avi'))]
        
        total_videos += len(video_files)
        
        for video_file in tqdm(video_files, desc=f"  {word_folder}", leave=False):
            video_path = os.path.join(word_path, video_file)
            
            try:
                sequence = process_video(video_path)
                
                if sequence is not None and len(sequence) == 5040:
                    data.append(sequence)
                    labels.append(word_folder)
                    successful += 1
            except Exception as e:
                print(f"\nError processing {video_file}: {e}")
    
    print(f"\n{'='*60}")
    print(f"Processing complete!")
    print(f"  Total videos: {total_videos}")
    print(f"  Successfully processed: {successful}")
    print(f"  Success rate: {successful/total_videos*100:.1f}%")
    
    if successful > 0:
        columns = []
        for frame_idx in range(SEQUENCE_LENGTH):
            for feature_type in ['pos', 'vel']:
                for hand_idx in range(2):
                    for point_idx in range(21):
                        columns.append(f'f{frame_idx}_{feature_type}_h{hand_idx}_x{point_idx}')
                        columns.append(f'f{frame_idx}_{feature_type}_h{hand_idx}_y{point_idx}')
        
        df = pd.DataFrame(data, columns=columns)
        df['label'] = labels
        
        print(f"\nSaving to {OUTPUT_FILE}...")
        df.to_csv(OUTPUT_FILE, index=False)
        print("Dataset saved successfully!")
        print(f"\nDataset shape: {df.shape}")
        print(f"Classes: {df['label'].nunique()}")
        print(f"\nClass distribution:")
        print(df['label'].value_counts())
    else:
        print("\nNo videos were successfully processed!")

if __name__ == "__main__":
    main()
