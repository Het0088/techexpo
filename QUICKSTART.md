# Quick Start - ISL Recognition System

## 🚀 Start the Application

### Step 1: Start Backend Server

```bash
python app.py
```

**You should see:**
```
============================================================
🚀 ISL Recognition Server
============================================================

✅ Server starting at: http://localhost:5000

📊 Model Status:
   Alphabet Model: ✅ Loaded
   Classes: 35

============================================================
```

### Step 2: Open in Browser

Open your browser and go to:
```
http://localhost:5000
```

### Step 3: Test Alphabet Recognition

1. Click **"Try Live Demo"** button in hero section
2. Click **"Start Camera"** button
3. Make sure **"Alphabet (A-Z)"** mode is selected
4. Show your hand sign to the camera
5. You'll see:
   - **Predicted letter** in large text
   - **Confidence percentage** (e.g., "95.3% confidence")
   - **Top 3 predictions** with progress bars

---

## ✅ What Works Now

✓ **Real Alphabet Recognition** - Using your trained landmark model  
✓ **Confidence Scores** - Shows accuracy percentage  
✓ **Top 3 Predictions** - With visual progress bars  
✓ **Two-Hand Support** - Detects both hands for complex signs  
✓ **Text to Sign** - Breaks words into alphabet letters

---

## 🎯 Testing Tips

**For Best Results:**
- Good lighting (not too dark)
- Hand centered in camera view
- Clear hand gesture (not blurry)
- Try different letters (A, B, C, etc.)

**Expected Accuracy:**
- Single hand signs: 90-95%
- Two hand signs: 85-92%
- Similar letters (E vs I): May need multiple tries

---

## ⚠️ Troubleshooting

**"Model not loaded"**
- Make sure `ml/models/isl_landmark_2hand_best.h5` exists
- Re-run: `python ml/train_landmark_model_v2.py`

**"No hand detected"**
- Check camera permissions
- Move hand closer to camera
- Ensure good lighting

**Webcam not starting**
- Allow camera permissions in browser
- Try different browser (Chrome recommended)
- Check if another app is using camera

---

## 📊 Understanding Predictions

**Confidence Score:**
- `>90%` = Very confident
- `80-90%` = Good prediction
- `<80%` = Low confidence, try again

**Top 3 Predictions:**
Shows the model's uncertainty - if top 3 are very different, the model is unsure.

---

## 🔧 Next Steps

1. **Test all 26 letters** - See which work best
2. **Test numbers 1-9** - Model supports these too
3. **Try text-to-sign** - Enter text in right panel
4. **Download word dataset** - For sentence recognition

---

**Your ISL Recognition system is now LIVE and WORKING!** 🎉
