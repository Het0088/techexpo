# Indian Sign Language Recognition System

A comprehensive web application with real ML-powered ISL recognition for tech expo demonstration, showcasing Indian Sign Language to a global audience.

## Features

- 🤖 **Alphabet Recognition**: Real-time CNN-based recognition of ISL alphabets (A-Z)
- 🖐️ **Word Recognition**: LSTM-based recognition of common ISL words using MediaPipe hand tracking
- 🎥 **Webcam Integration**: Live sign language detection through webcam
- 📝 **Text-to-Sign**: Convert text to ISL sign demonstrations
- 📚 **Learning Module**: Interactive ISL alphabet and word reference
- 🌍 **Global Awareness**: Educational content about ISL and the deaf community

## Tech Stack

- **ML Framework**: TensorFlow/Keras
- **Hand Tracking**: MediaPipe
- **Backend**: Flask
- **Frontend**: HTML, CSS, JavaScript
- **Computer Vision**: OpenCV

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Download Dataset

Download the ISL alphabet dataset from Kaggle or GitHub and place it in `ml/dataset/` directory.

### 3. Train Models

```bash
# Train alphabet recognition model
python ml/train_alphabet.py

# Train word recognition model (after collecting data)
python ml/train_words.py
```

### 4. Run the Application

```bash
# Start the Flask backend
python app.py

# In a separate terminal, serve the frontend
npx -y serve ./
```

## Project Structure

```
techexpo/
├── ml/                     # Machine learning models
│   ├── alphabet_model.py   # CNN for alphabet recognition
│   ├── word_model.py       # LSTM for word recognition
│   ├── train_alphabet.py   # Training script for alphabets
│   ├── train_words.py      # Training script for words
│   ├── predict.py          # Prediction service
│   ├── dataset/            # Training data (not included)
│   └── models/             # Trained models
├── css/                    # Stylesheets
├── js/                     # JavaScript files
├── assets/                 # Images and videos
├── app.py                  # Flask backend server
├── index.html              # Main web interface
└── requirements.txt        # Python dependencies
```

## Timeline

- **Days 1-3**: Alphabet recognition model
- **Days 4-6**: Word recognition model
- **Days 7-9**: Web frontend and integration
- **Day 10**: Polish and testing

## License

MIT License - Educational project for tech expo demonstration.
