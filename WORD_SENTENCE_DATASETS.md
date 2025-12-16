# ISL Word & Sentence Datasets - Download Guide

## 🎯 Goal: Train on Words & Sentences Directly

Skip alphabets, focus on **real conversation**!

---

## 📥 Option 1: INCLUDE Dataset (Recommended for Words)

**What it is:**
- 263 ISL words across 15 categories
- 4,287 videos
- 0.27 million frames
- Professional signers

**Download:**
```bash
# Direct download link
https://zenodo.org/record/4010759/files/INCLUDE.zip

# Or visit: https://zenodo.org/record/4010759
```

**Size:** ~8 GB

**Categories included:**
- Greetings, Family, Food, Colors, Numbers, Animals, Pronouns, etc.

**Format:** Video files (.mp4) organized by word

**Setup:**
1. Download ZIP from link above
2. Extract to `ml/dataset/isl_words/`
3. Run `python ml/train_words_from_dataset.py`

---

## 📥 Option 2: ISLTranslate (Best for Sentences)

**What it is:**
- 30,000 ISL-English sentence pairs
- Continuous sign language videos
- Largest ISL translation dataset
- Real sentence-level recognition

**Download:**
```bash
# Visit Hugging Face
https://huggingface.co/datasets/Exploration-Lab/iSign

# Download using Python
from huggingface_hub import hf_hub_download
hf_hub_download(repo_id="Exploration-Lab/iSign", 
                filename="ISLTranslate.csv", 
                repo_type="dataset")
```

**Size:** ~20 GB

**Setup:**
1. Create free Hugging Face account
2. Download dataset
3. Extract to `ml/dataset/isl_sentences/`

---

## 📥 Option 3: ISL-CSLTR (Alternative for Sentences)

**What it is:**
- 700 fully annotated videos
- 100 spoken sentences
- 7 different signers
- Sentence-level labels

**Download:**
```bash
# Kaggle dataset
https://www.kaggle.com/datasets/sujitmandal/islcsltr
```

**Size:** ~5 GB

---

## 📥 Option 4: Custom Word Collection (Quick Start)

**For 10-day timeline:**

Download pre-recorded ISL videos from YouTube/online sources:

**Top 50 ISL Words List:**
1. Greetings: Hello, Goodbye, Good Morning, Good Night, Welcome
2. Polite: Please, Thank You, Sorry, Excuse Me
3. Family: Mother, Father, Brother, Sister, Family
4. Questions: What, Where, When, Who, How, Why
5. Common Verbs: Go, Come, Eat, Drink, Sleep, Help, Want, Need
6. Essentials: Yes, No, OK, Good, Bad, More, Less
7. Daily: Today, Tomorrow, Yesterday, Now, Later
8. Pronouns: I, You, He, She, We, They, Me
9. Basic Needs: Food, Water, Bathroom, Medicine
10. Emergency: Help, Emergency, Doctor, Hospital

**Where to find:**
- YouTube: Search "ISL [word] sign"
- ISL Dictionary: https://indiansignlanguage.org/
- Record your own (follow ISL standards)

---

## 🚀 Quick Start Path (Recommended for 10 Days)

### **Path A: Word-Based (Easier)**

**Days 1-2:** Download INCLUDE dataset (263 words)
**Days 3-6:** Train word recognition model
**Days 7-8:** Build word-to-sentence logic
**Days 9-10:** Test and polish

**Complexity:** Medium
**Outcome:** Recognize 50-100 words, form sentences from words

### **Path B: Sentence-Based (Ambitious)**

**Days 1-3:** Download ISLTranslate (30K sentences)
**Days 4-8:** Train sequence-to-sequence model
**Days 9-10:** Test and optimize

**Complexity:** High
**Outcome:** True sentence recognition (like translation)

### **Path C: Hybrid (Best)**

**Days 1-2:** Download both INCLUDE + sample from ISLTranslate
**Days 3-6:** Train on 50 common words
**Days 7-8:** Add 20-30 common sentences
**Days 9-10:** Integration and testing

**Complexity:** Medium-High
**Outcome:** Words + common sentences, best demo!

---

## 💾 Dataset Structure

### For Words (INCLUDE):
```
ml/dataset/isl_words/
├── hello/
│   ├── video001.mp4
│   ├── video002.mp4
│   └── ...
├── thank_you/
│   └── ...
└── goodbye/
    └── ...
```

### For Sentences (ISLTranslate):
```
ml/dataset/isl_sentences/
├── ISLTranslate.csv  (video_id, english_text)
├── videos/
│   ├── sent_001.mp4
│   ├── sent_002.mp4
│   └── ...
└── features/  (pre-extracted landmarks)
```

---

## ⚡ Processing Pipeline

**For Words:**
1. Video → MediaPipe hand landmarks
2. Landmarks → LSTM model
3. Output: Word label + confidence
4. Latency: ~200-300ms per word

**For Sentences:**
1. Video sequence → MediaPipe landmarks
2. Landmarks → Seq2Seq model (Transformer/LSTM)
3. Output: English sentence
4. Latency: ~500ms-1s per sentence

---

## 🎯 Recommended: Start with INCLUDE (Words)

**Why:**
- ✅ Easier to train
- ✅ Smaller dataset (manageable in 10 days)
- ✅ Still achieves sentence recognition (word concatenation)
- ✅ Better latency (<0.5s per word)
- ✅ More reliable for demo

**Download now:**
1. Go to: https://zenodo.org/record/4010759
2. Click "Download" (8 GB)
3. Extract to `ml/dataset/isl_words/`

---

## 📝 Next Steps

1. **Choose your path** (A, B, or C above)
2. **Download dataset** (links above)
3. **Run setup script**: `python ml/setup_word_training.py`
4. **Start training**: `python ml/train_words_from_dataset.py`

---

**Ready to download? Which path do you want to take?** 🚀
