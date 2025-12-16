"""
Train model on 2-hand landmark dataset (84 features).
"""

import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import json
import os

# Configuration
DATA_FILE = 'ml/dataset/isl_landmarks_2hands.csv'
MODEL_PATH = 'ml/models'
EPOCHS = 50
BATCH_SIZE = 32

def train_landmark_model():
    if not os.path.exists(DATA_FILE):
        print(f"❌ Error: {DATA_FILE} not found.")
        print("Run process_dataset_landmarks_v2.py first.")
        return

    print("Loading 2-hand landmark data...")
    df = pd.read_csv(DATA_FILE, dtype={'label': str})  # Force label to be string
    
    X = df.drop('label', axis=1).values
    y = df['label'].values.astype(str)  # Ensure all labels are strings
    
    print(f"Input shape: {X.shape} (84 features = 2 hands × 21 points × 2 coords)")
    
    # Encode labels
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    classes = label_encoder.classes_
    num_classes = len(classes)
    
    print(f"Loaded {len(X)} samples, {num_classes} classes.")
    
    # Save class mapping
    os.makedirs(MODEL_PATH, exist_ok=True)
    class_mapping = {int(i): cls for i, cls in enumerate(classes)}
    with open(f'{MODEL_PATH}/landmark_2hand_class_indices.json', 'w') as f:
        json.dump(class_mapping, f)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    # Model for 84 input features
    model = keras.Sequential([
        keras.layers.Input(shape=(84,)),
        keras.layers.Dense(128, activation='relu'),
        keras.layers.Dropout(0.3),
        keras.layers.Dense(64, activation='relu'),
        keras.layers.Dropout(0.2),
        keras.layers.Dense(num_classes, activation='softmax')
    ])
    
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    print("\n🚀 Starting training...")
    history = model.fit(
        X_train, y_train,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        validation_data=(X_test, y_test),
        callbacks=[
            keras.callbacks.EarlyStopping(patience=7, restore_best_weights=True),
            keras.callbacks.ModelCheckpoint(
                f'{MODEL_PATH}/isl_landmark_2hand_best.h5', 
                save_best_only=True,
                verbose=1
            )
        ],
        verbose=1
    )
    
    # Final evaluation
    loss, acc = model.evaluate(X_test, y_test)
    print(f"\n✅ Final Test Accuracy: {acc*100:.2f}%")
    
    model.save(f'{MODEL_PATH}/isl_landmark_2hand_final.h5')
    print("✅ Model saved! Ready for 2-handed prediction.")

if __name__ == "__main__":
    train_landmark_model()
