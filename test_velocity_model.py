import numpy as np
from tensorflow import keras
import json

MODEL_PATH = 'ml/models/isl_words_velocity_best.h5'
CLASSES_PATH = 'ml/models/word_class_indices_velocity.json'

print("Testing Velocity Model")
print("="*60)

print("\n1. Loading model...")
try:
    model = keras.models.load_model(MODEL_PATH)
    print(f"   Model loaded: {MODEL_PATH}")
except Exception as e:
    print(f"   ERROR loading model: {e}")
    exit(1)

print("\n2. Loading class mapping...")
try:
    with open(CLASSES_PATH, 'r') as f:
        classes = json.load(f)
    print(f"   Classes loaded: {len(classes)} words")
    print(f"   Words: {list(classes.values())}")
except Exception as e:
    print(f"   ERROR loading classes: {e}")
    exit(1)

print("\n3. Checking model architecture...")
print(f"   Input shape: {model.input_shape}")
print(f"   Output shape: {model.output_shape}")
print(f"   Expected input: (None, 30, 168)")
print(f"   Expected output: (None, {len(classes)})")

if model.input_shape != (None, 30, 168):
    print("\n   WARNING: Input shape mismatch!")
    print(f"   Expected: (None, 30, 168)")
    print(f"   Got: {model.input_shape}")
else:
    print("\n   Input shape correct!")

print("\n4. Testing prediction with random data...")
test_sequence = np.random.rand(1, 30, 168)
try:
    predictions = model.predict(test_sequence, verbose=0)
    print(f"   Prediction successful!")
    print(f"   Output shape: {predictions.shape}")
    print(f"   Sum of probabilities: {predictions.sum():.4f}")
    
    top_idx = np.argmax(predictions[0])
    top_prob = predictions[0][top_idx]
    predicted_word = classes.get(str(top_idx), "Unknown")
    
    print(f"\n   Top prediction: {predicted_word}")
    print(f"   Confidence: {top_prob*100:.2f}%")
    
    print(f"\n   Top 3 predictions:")
    top_3_idx = np.argsort(predictions[0])[-3:][::-1]
    for idx in top_3_idx:
        word = classes.get(str(idx), "Unknown")
        prob = predictions[0][idx]
        print(f"      {word}: {prob*100:.2f}%")
        
except Exception as e:
    print(f"   ERROR during prediction: {e}")
    exit(1)

print("\n5. Testing with multiple sequences...")
test_batch = np.random.rand(5, 30, 168)
try:
    batch_predictions = model.predict(test_batch, verbose=0)
    print(f"   Batch prediction successful!")
    print(f"   Batch shape: {batch_predictions.shape}")
    print(f"   Predicted words:")
    for i, pred in enumerate(batch_predictions):
        top_idx = np.argmax(pred)
        word = classes.get(str(top_idx), "Unknown")
        conf = pred[top_idx]
        print(f"      Sequence {i+1}: {word} ({conf*100:.2f}%)")
except Exception as e:
    print(f"   ERROR during batch prediction: {e}")
    exit(1)

print("\n" + "="*60)
print("Model Test Complete - Everything Working!")
print("="*60)
print("\nModel is ready to use. Features per frame:")
print("  - Position: 84 features")
print("  - Velocity: 84 features")
print("  - Total: 168 features per frame")
print("  - Sequence: 30 frames × 168 = 5,040 features")
