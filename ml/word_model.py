"""
LSTM Model for ISL Word Recognition
Uses MediaPipe hand landmarks for dynamic gesture recognition
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models


def create_word_model(sequence_length=30, num_landmarks=21, num_coords=3, num_words=50):
    """
    Create LSTM model for ISL word recognition from hand landmark sequences
    
    Args:
        sequence_length: Number of frames per sequence
        num_landmarks: Number of hand landmarks (21 for MediaPipe)
        num_coords: Coordinates per landmark (x, y, z)
        num_words: Number of output word classes
    
    Returns:
        Compiled Keras model
    """
    input_features = num_landmarks * num_coords  # 21 * 3 = 63 features
    
    model = models.Sequential([
        # Input layer
        layers.Input(shape=(sequence_length, input_features)),
        
        # LSTM layers
        layers.LSTM(128, return_sequences=True, activation='tanh'),
        layers.Dropout(0.3),
        layers.BatchNormalization(),
        
        layers.LSTM(128, return_sequences=True, activation='tanh'),
        layers.Dropout(0.3),
        layers.BatchNormalization(),
        
        layers.LSTM(64, return_sequences=False, activation='tanh'),
        layers.Dropout(0.3),
        layers.BatchNormalization(),
        
        # Dense layers
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.4),
        layers.Dense(64, activation='relu'),
        layers.Dropout(0.4),
        
        # Output layer
        layers.Dense(num_words, activation='softmax')
    ])
    
    # Compile model
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model


def create_bidirectional_model(sequence_length=30, num_landmarks=21, num_coords=3, num_words=50):
    """
    Create Bidirectional LSTM model for better context understanding
    Alternative architecture for comparison
    """
    input_features = num_landmarks * num_coords
    
    model = models.Sequential([
        layers.Input(shape=(sequence_length, input_features)),
        
        # Bidirectional LSTM layers
        layers.Bidirectional(layers.LSTM(128, return_sequences=True)),
        layers.Dropout(0.3),
        layers.BatchNormalization(),
        
        layers.Bidirectional(layers.LSTM(64, return_sequences=False)),
        layers.Dropout(0.3),
        layers.BatchNormalization(),
        
        # Dense layers
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.4),
        layers.Dense(64, activation='relu'),
        layers.Dropout(0.4),
        
        # Output layer
        layers.Dense(num_words, activation='softmax')
    ])
    
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model


if __name__ == '__main__':
    # Test model creation
    print("Creating standard LSTM model...")
    model = create_word_model(num_words=50)
    model.summary()
    print(f"\nTotal parameters: {model.count_params():,}")
    
    print("\n" + "="*50)
    print("Creating Bidirectional LSTM model...")
    bi_model = create_bidirectional_model(num_words=50)
    bi_model.summary()
    print(f"\nTotal parameters: {bi_model.count_params():,}")
