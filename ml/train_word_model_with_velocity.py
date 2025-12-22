import pandas as pd
import numpy as np
import os
import json

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
except ImportError:
    import keras
    from keras import layers
    
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

DATA_FILE = 'ml/dataset/isl_word_sequences_with_velocity.csv'
MODEL_PATH = 'ml/models'
EPOCHS = 100
BATCH_SIZE = 8

gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        print(f"GPU found: {gpus[0].name}")
    except RuntimeError as e:
        print(e)
else:
    print("No GPU detected, using CPU")

def augment_sequence(sequence, noise_factor=0.01, scale_factor=0.1):
    augmented = sequence.copy()
    
    noise = np.random.normal(0, noise_factor, sequence.shape)
    augmented += noise
    
    scale = 1 + np.random.uniform(-scale_factor, scale_factor)
    augmented *= scale
    
    return augmented

def create_velocity_aware_model(sequence_length, features_per_frame, num_classes):
    model = keras.Sequential([
        layers.Input(shape=(sequence_length, features_per_frame)),
        
        layers.Bidirectional(layers.LSTM(256, return_sequences=True)),
        layers.BatchNormalization(),
        layers.Dropout(0.4),
        
        layers.Bidirectional(layers.LSTM(128, return_sequences=True)),
        layers.BatchNormalization(),
        layers.Dropout(0.4),
        
        layers.Bidirectional(layers.LSTM(64)),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        
        layers.Dense(128, activation='relu', kernel_regularizer=keras.regularizers.l2(0.001)),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        
        layers.Dense(num_classes, activation='softmax')
    ])
    return model

print("="*60)
print("Training Movement-Aware ISL Word Recognition Model")
print("="*60)

print("\nLoading data...")
df = pd.read_csv(DATA_FILE)

X = df.drop('label', axis=1).values
y = df['label'].values

label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)
classes = label_encoder.classes_
num_classes = len(classes)

print(f"\nDataset info:")
print(f"  Samples: {len(X)}")
print(f"  Classes: {num_classes}")
print(f"  Features per sample: {X.shape[1]}")
print(f"  Sequence length: 30 frames")
print(f"  Features per frame: 168 (84 position + 84 velocity)")

X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)

print(f"\nSplit:")
print(f"  Training: {len(X_train)}")
print(f"  Testing: {len(X_test)}")

print("\nApplying data augmentation...")
X_train_augmented = []
y_train_augmented = []

for i in range(len(X_train)):
    original = X_train[i].reshape(30, 168)
    
    X_train_augmented.append(original.flatten())
    y_train_augmented.append(y_train[i])
    
    for _ in range(2):
        augmented = augment_sequence(original)
        X_train_augmented.append(augmented.flatten())
        y_train_augmented.append(y_train[i])

X_train_augmented = np.array(X_train_augmented)
y_train_augmented = np.array(y_train_augmented)

print(f"  Original training samples: {len(X_train)}")
print(f"  Augmented training samples: {len(X_train_augmented)}")

X_train_seq = X_train_augmented.reshape(-1, 30, 168)
X_test_seq = X_test.reshape(-1, 30, 168)

os.makedirs(MODEL_PATH, exist_ok=True)

class_mapping = {int(i): str(cls) for i, cls in enumerate(classes)}
with open(f'{MODEL_PATH}/word_class_indices_velocity.json', 'w') as f:
    json.dump(class_mapping, f)

print("\nBuilding movement-aware model...")
model = create_velocity_aware_model(30, 168, num_classes)

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.0005),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

print("\nModel architecture:")
model.summary()

callbacks = [
    keras.callbacks.EarlyStopping(
        patience=15,
        restore_best_weights=True,
        verbose=1
    ),
    keras.callbacks.ModelCheckpoint(
        f'{MODEL_PATH}/isl_words_velocity_best.h5',
        save_best_only=True,
        verbose=1
    ),
    keras.callbacks.ReduceLROnPlateau(
        factor=0.5,
        patience=8,
        min_lr=0.00001,
        verbose=1
    )
]

print("\nStarting training...")
history = model.fit(
    X_train_seq, y_train_augmented,
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    validation_data=(X_test_seq, y_test),
    callbacks=callbacks,
    verbose=1
)

print("\nEvaluating model...")
loss, acc = model.evaluate(X_test_seq, y_test)
print(f"\nFinal Test Accuracy: {acc*100:.2f}%")

model.save(f'{MODEL_PATH}/isl_words_velocity_final.h5')

history_dict = {
    'accuracy': [float(x) for x in history.history['accuracy']],
    'val_accuracy': [float(x) for x in history.history['val_accuracy']],
    'loss': [float(x) for x in history.history['loss']],
    'val_loss': [float(x) for x in history.history['val_loss']]
}

with open(f'{MODEL_PATH}/training_history_velocity.json', 'w') as f:
    json.dump(history_dict, f)

print("\n" + "="*60)
print("Training complete!")
print(f"Model saved to {MODEL_PATH}")
print(f"  Best model: isl_words_velocity_best.h5")
print(f"  Class mapping: word_class_indices_velocity.json")
print("="*60)
