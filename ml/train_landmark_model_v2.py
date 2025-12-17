import pandas as pd
import numpy as np
import os
import json
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

DATA_FILE = 'ml/dataset/isl_landmarks_2hands.csv'
MODEL_PATH = 'ml/models'
EPOCHS = 150
BATCH_SIZE = 32

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

def create_model(input_dim, num_classes):
    model = keras.Sequential([
        layers.Input(shape=(input_dim,)),
        layers.Dense(512, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.4),
        layers.Dense(256, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.4),
        layers.Dense(128, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        layers.Dense(num_classes, activation='softmax')
    ])
    return model

print("Loading data...")
df = pd.read_csv(DATA_FILE, dtype={'label': str})

X = df.drop('label', axis=1).values
y = df['label'].values.astype(str)

label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)
classes = label_encoder.classes_
num_classes = len(classes)

print(f"Loaded {len(X)} samples")
print(f"Classes: {num_classes}")

X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)

print(f"Training samples: {len(X_train)}")
print(f"Testing samples: {len(X_test)}")

os.makedirs(MODEL_PATH, exist_ok=True)

class_mapping = {int(i): str(cls) for i, cls in enumerate(classes)}
with open(f'{MODEL_PATH}/landmark_2hand_class_indices.json', 'w') as f:
    json.dump(class_mapping, f)

print("Building model...")
model = create_model(X.shape[1], num_classes)

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

callbacks = [
    keras.callbacks.EarlyStopping(
        patience=20,
        restore_best_weights=True,
        verbose=1
    ),
    keras.callbacks.ModelCheckpoint(
        f'{MODEL_PATH}/isl_landmark_2hand_best.h5',
        save_best_only=True,
        verbose=1
    ),
    keras.callbacks.ReduceLROnPlateau(
        factor=0.5,
        patience=10,
        min_lr=0.00001,
        verbose=1
    )
]

print("Starting training...")
history = model.fit(
    X_train, y_train,
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    validation_data=(X_test, y_test),
    callbacks=callbacks,
    verbose=1
)

print("Evaluating model...")
loss, acc = model.evaluate(X_test, y_test)
print(f"\nFinal Test Accuracy: {acc*100:.2f}%")

model.save(f'{MODEL_PATH}/isl_landmark_2hand_final.h5')

history_dict = {
    'accuracy': [float(x) for x in history.history['accuracy']],
    'val_accuracy': [float(x) for x in history.history['val_accuracy']],
    'loss': [float(x) for x in history.history['loss']],
    'val_loss': [float(x) for x in history.history['val_loss']]
}

with open(f'{MODEL_PATH}/training_history.json', 'w') as f:
    json.dump(history_dict, f)

print("\nTraining complete")
print(f"Model saved to {MODEL_PATH}")
