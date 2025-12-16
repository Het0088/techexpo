"""
Train LSTM Model on ISL Word Sequences
For temporal word recognition from landmark sequences
"""

import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import json
import os

# Configuration
DATA_FILE = 'ml/dataset/isl_word_sequences.csv'
MODEL_PATH = 'ml/models'
SEQUENCE_LENGTH = 30
FEATURES_PER_FRAME = 84
EPOCHS = 50
BATCH_SIZE = 16

def create_lstm_model(num_classes):
    """Create LSTM model for word recognition"""
    model = keras.Sequential([
        layers.Input(shape=(SEQUENCE_LENGTH, FEATURES_PER_FRAME)),
        
        # LSTM layers
        layers.LSTM(128, return_sequences=True),
        layers.Dropout(0.3),
        layers.LSTM(64),
        layers.Dropout(0.2),
        
        # Dense layers
        layers.Dense(64, activation='relu'),
        layers.Dropout(0.2),
        layers.Dense(num_classes, activation='softmax')
    ])
    
    return model

def main():
    print("="*60)
    print("Training ISL Word Recognition Model")
    print("="*60)
    
    if not os.path.exists(DATA_FILE):
        print(f"\n❌ Data file not found: {DATA_FILE}")
        print("Run process_word_videos.py first!")
        return
    
    print(f"\n📊 Loading data from {DATA_FILE}...")
    df = pd.read_csv(DATA_FILE)
    
    print(f"✅ Loaded {len(df)} sequences")
    print(f"   Classes: {df['label'].nunique()}")
    
    # Separate features and labels
    X = df.drop('label', axis=1).values
    y = df['label'].values
    
    # Encode labels
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    classes = label_encoder.classes_
    num_classes = len(classes)
    
    print(f"\n📋 Word classes:")
    for i, word in enumerate(classes):
        count = np.sum(y_encoded == i)
        print(f"   {i}: {word:30s} ({count} samples)")
    
    # Reshape for LSTM: (samples, timesteps, features)
    X = X.reshape(-1, SEQUENCE_LENGTH, FEATURES_PER_FRAME)
    
    print(f"\n🔄 Input shape: {X.shape}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    print(f"\n📊 Data split:")
    print(f"   Training: {len(X_train)} samples")
    print(f"   Testing: {len(X_test)} samples")
    
    # Save class mapping
    os.makedirs(MODEL_PATH, exist_ok=True)
    class_mapping = {int(i): str(cls) for i, cls in enumerate(classes)}
    with open(f'{MODEL_PATH}/word_class_indices.json', 'w') as f:
        json.dump(class_mapping, f)
    print(f"\n✅ Saved class mapping")
    
    # Create model
    print(f"\n🏗️  Building LSTM model...")
    model = create_lstm_model(num_classes)
    
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    print(model.summary())
    
    # Callbacks
    callbacks = [
        keras.callbacks.EarlyStopping(
            patience=10,
            restore_best_weights=True,
            verbose=1
        ),
        keras.callbacks.ModelCheckpoint(
            f'{MODEL_PATH}/isl_words_best.h5',
            save_best_only=True,
            verbose=1
        ),
        keras.callbacks.ReduceLROnPlateau(
            factor=0.5,
            patience=5,
            verbose=1
        )
    ]
    
    # Train
    print(f"\n🚀 Starting training...")
    print(f"   Epochs: {EPOCHS}")
    print(f"   Batch size: {BATCH_SIZE}\n")
    
    history = model.fit(
        X_train, y_train,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        validation_data=(X_test, y_test),
        callbacks=callbacks,
        verbose=1
    )
    
    # Final evaluation
    print(f"\n{'='*60}")
    print("Evaluating model...")
    loss, acc = model.evaluate(X_test, y_test)
    print(f"\n✅ Final Test Accuracy: {acc*100:.2f}%")
    print(f"{'='*60}")
    
    # Save final model
    model.save(f'{MODEL_PATH}/isl_words_final.h5')
    
    # Save training history
    history_dict = {
        'accuracy': [float(x) for x in history.history['accuracy']],
        'val_accuracy': [float(x) for x in history.history['val_accuracy']],
        'loss': [float(x) for x in history.history['loss']],
        'val_loss': [float(x) for x in history.history['val_loss']]
    }
    
    with open(f'{MODEL_PATH}/word_training_history.json', 'w') as f:
        json.dump(history_dict, f)
    
    print(f"\n✅ Models saved:")
    print(f"   - {MODEL_PATH}/isl_words_best.h5")
    print(f"   - {MODEL_PATH}/isl_words_final.h5")
    print(f"   - {MODEL_PATH}/word_class_indices.json")
    print(f"   - {MODEL_PATH}/word_training_history.json")
    
    print(f"\n🎉 Training complete! Run app.py to test word recognition.")

if __name__ == "__main__":
    main()
