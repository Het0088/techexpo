"""
Enhanced LSTM Training with Data Augmentation and Better Architecture
For improved real-world accuracy
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

# ============ GPU CONFIGURATION ============
print("="*60)
print("GPU Configuration")
print("="*60)

# Check for GPU
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        # Enable memory growth to prevent TF from allocating all GPU memory
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        
        # Force GPU usage
        tf.config.set_visible_devices(gpus[0], 'GPU')
        
        print(f"✅ GPU FOUND: {gpus[0].name}")
        print(f"   Using GPU for training")
        
        # Verify GPU is being used
        with tf.device('/GPU:0'):
            a = tf.constant([[1.0, 2.0], [3.0, 4.0]])
            b = tf.constant([[1.0, 1.0], [0.0, 1.0]])
            c = tf.matmul(a, b)
        print(f"✅ GPU test successful")
        
    except RuntimeError as e:
        print(f"⚠️  GPU setup failed: {e}")
        print("   Falling back to CPU")
else:
    print("❌ NO GPU DETECTED")
    print("   Training will use CPU (slower)")
    print("\n   To use GPU, ensure:")
    print("   1. NVIDIA GPU drivers installed")
    print("   2. CUDA toolkit installed")
    print("   3. tensorflow-gpu or tensorflow with GPU support")

print("="*60 + "\n")
# ============================================


# Enhanced Configuration
DATA_FILE = 'ml/dataset/isl_word_sequences.csv'
MODEL_PATH = 'ml/models'
SEQUENCE_LENGTH = 30
FEATURES_PER_FRAME = 84
EPOCHS = 100  # Increased from 50
BATCH_SIZE = 8   # Smaller batch for better learning
LEARNING_RATE = 0.0005  # Lower learning rate

def augment_sequence(sequence):
    """Apply data augmentation to sequence"""
    augmented = sequence.copy()
    
    # Random noise
    if np.random.rand() > 0.5:
        noise = np.random.normal(0, 0.02, sequence.shape)
        augmented = augmented + noise
    
    # Random scaling
    if np.random.rand() > 0.5:
        scale = np.random.uniform(0.9, 1.1)
        augmented = augmented * scale
    
    # Time shifting (shift frames slightly)
    if np.random.rand() > 0.5:
        shift = np.random.randint(-2, 3)
        augmented = np.roll(augmented, shift, axis=0)
    
    return augmented

def create_enhanced_model(num_classes):
    """Enhanced LSTM model with better architecture"""
    model = keras.Sequential([
        layers.Input(shape=(SEQUENCE_LENGTH, FEATURES_PER_FRAME)),
        
        # Bidirectional LSTM for better temporal understanding
        layers.Bidirectional(layers.LSTM(256, return_sequences=True)),
        layers.BatchNormalization(),
        layers.Dropout(0.4),
        
        layers.Bidirectional(layers.LSTM(128, return_sequences=True)),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        
        layers.Bidirectional(layers.LSTM(64)),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        
        # Dense layers with L2 regularization
        layers.Dense(128, activation='relu', kernel_regularizer=keras.regularizers.l2(0.01)),
        layers.Dropout(0.4),
        layers.Dense(64, activation='relu', kernel_regularizer=keras.regularizers.l2(0.01)),
        layers.Dropout(0.3),
        
        layers.Dense(num_classes, activation='softmax')
    ])
    
    return model

def main():
    print("="*60)
    print("Enhanced ISL Word Recognition Training")
    print("="*60)
    
    if not os.path.exists(DATA_FILE):
        print(f"\n❌ Data file not found: {DATA_FILE}")
        return
    
    print(f"\n📊 Loading data...")
    df = pd.read_csv(DATA_FILE)
    
    X = df.drop('label', axis=1).values
    y = df['label'].values
    
    # Encode labels
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    classes = label_encoder.classes_
    num_classes = len(classes)
    
    print(f"✅ Loaded {len(X)} sequences")
    print(f"   Classes: {num_classes}")
    
    # Reshape
    X = X.reshape(-1, SEQUENCE_LENGTH, FEATURES_PER_FRAME)
    
    # Split with stratification
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    print(f"\n📊 Split:")
    print(f"   Training: {len(X_train)}")
    print(f"   Testing: {len(X_test)}")
    
    # Data Augmentation
    print(f"\n🔄 Applying data augmentation...")
    X_train_aug = []
    y_train_aug = []
    
    # Original data
    X_train_aug.extend(X_train)
    y_train_aug.extend(y_train)
    
    # Augmented copies (3x augmentation)
    for _ in range(3):
        for seq, label in zip(X_train, y_train):
            aug_seq = augment_sequence(seq)
            X_train_aug.append(aug_seq)
            y_train_aug.append(label)
    
    X_train = np.array(X_train_aug)
    y_train = np.array(y_train_aug)
    
    print(f"✅ Training data after augmentation: {len(X_train)}")
    
    # Save class mapping
    os.makedirs(MODEL_PATH, exist_ok=True)
    class_mapping = {int(i): str(cls) for i, cls in enumerate(classes)}
    with open(f'{MODEL_PATH}/word_class_indices.json', 'w') as f:
        json.dump(class_mapping, f)
    
    # Create enhanced model
    print(f"\n🏗️  Building enhanced LSTM model...")
    model = create_enhanced_model(num_classes)
    
    # Custom optimizer with lower learning rate
    optimizer = keras.optimizers.Adam(learning_rate=LEARNING_RATE)
    
    model.compile(
        optimizer=optimizer,
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    print(model.summary())
    
    # Enhanced callbacks
    callbacks = [
        keras.callbacks.EarlyStopping(
            patience=15,  # Increased patience
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
            patience=7,
            min_lr=0.00001,
            verbose=1
        )
    ]
    
    # Train
    print(f"\n🚀 Starting enhanced training...")
    print(f"   Epochs: {EPOCHS}")
    print(f"   Batch size: {BATCH_SIZE}")
    print(f"   Learning rate: {LEARNING_RATE}\n")
    
    history = model.fit(
        X_train, y_train,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        validation_data=(X_test, y_test),
        callbacks=callbacks,
        verbose=1
    )
    
    # Evaluation
    print(f"\n{'='*60}")
    print("Final Evaluation...")
    loss, acc = model.evaluate(X_test, y_test)
    print(f"\n✅ Final Test Accuracy: {acc*100:.2f}%")
    print(f"{'='*60}")
    
    # Save
    model.save(f'{MODEL_PATH}/isl_words_final.h5')
    
    # Save history
    history_dict = {
        'accuracy': [float(x) for x in history.history['accuracy']],
        'val_accuracy': [float(x) for x in history.history['val_accuracy']],
        'loss': [float(x) for x in history.history['loss']],
        'val_loss': [float(x) for x in history.history['val_loss']]
    }
    
    with open(f'{MODEL_PATH}/word_training_history.json', 'w') as f:
        json.dump(history_dict, f)
    
    print(f"\n✅ Enhanced model saved!")
    print(f"   Best accuracy: {max(history.history['val_accuracy'])*100:.2f}%")

if __name__ == "__main__":
    main()
