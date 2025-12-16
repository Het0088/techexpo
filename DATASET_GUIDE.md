# ISL Dataset Download Guide

## 📥 Quick Download Instructions

### **Recommended: GitHub Dataset (150K images)**

**Direct Download:**
1. Click this link: [Download ISL Dataset](https://github.com/yatharth77/Indian-Sign-Language-Gesture-Recognition/archive/refs/heads/master.zip)
2. Extract the ZIP file
3. Inside, find the `Dataset/` folder
4. Copy all alphabet folders (A/ through Z/) to: `ml/dataset/isl_alphabets/`

**Alternative - Clone with Git:**
```bash
git clone https://github.com/yatharth77/Indian-Sign-Language-Gesture-Recognition.git
cd Indian-Sign-Language-Gesture-Recognition
# Copy Dataset folder to your project
```

---

### **Alternative: Kaggle Datasets**

**Option 1: ISL Dataset (12K images)**
- Link: https://www.kaggle.com/datasets/prathumarikeri/indian-sign-language-isl
- Click "Download" (requires free Kaggle account)
- Extract to `ml/dataset/isl_alphabets/`

**Option 2: ISL Alphabet Recognition**
- Link: https://www.kaggle.com/datasets/vaishnaviasonawane/indian-sign-language-dataset
- Download and extract

---

## 📁 Required Folder Structure

After downloading, your folder should look like this:

```
d:\Ideas\techexpo\ml\dataset\isl_alphabets\
├── A\
│   ├── image_001.jpg
│   ├── image_002.jpg
│   ├── image_003.jpg
│   └── ... (5000+ images)
├── B\
│   └── ... (5000+ images)
├── C\
│   └── ...
...
└── Z\
    └── ... (5000+ images)
```

---

## ✅ Supported Image Formats

- **JPG/JPEG** ✓ (recommended)
- **PNG** ✓
- **BMP** ✓
- Any size works (auto-resized to 144×144)

---

## 📊 Dataset Size Recommendations

| Quality | Images per Letter | Total Images | Expected Accuracy |
|---------|------------------|--------------|-------------------|
| Minimum | 500+ | 13,000+ | 70-80% |
| Good | 2,000+ | 52,000+ | 85-90% |
| Excellent | 5,000+ | 130,000+ | 95-98% |

---

## 🔧 Setup Helper Script

Run this to check your dataset structure:

```bash
python ml/download_dataset.py
```

This will:
- Show download instructions
- Create necessary directories
- Verify your dataset structure
- Count images per alphabet

---

## 🎯 Complete Setup Process

**Step 1: Create Directory**
```bash
mkdir ml\dataset\isl_alphabets
```

**Step 2: Download Dataset**
- Use GitHub link above (easiest)
- Or Kaggle (requires account)

**Step 3: Extract & Copy**
- Extract the ZIP file
- Copy all A-Z folders to `ml\dataset\isl_alphabets\`

**Step 4: Verify**
```bash
python ml/download_dataset.py
```

**Step 5: Train!**
```bash
python ml/train_alphabet.py
```

---

## 💡 Pro Tips

1. **More variety = Better accuracy**
   - Different hands
   - Different lighting
   - Different angles
   - Different backgrounds

2. **Clean data = Better results**
   - Remove corrupted images
   - Remove unclear images
   - Keep consistent sign positions

3. **Start small, scale up**
   - Start with 1000 images to test
   - Add more images if accuracy is low

---

## ❓ Troubleshooting

**"Cannot find dataset"**
- Make sure folder path is exactly: `ml/dataset/isl_alphabets/`
- Check that folders are named A, B, C... Z (uppercase)

**"Not enough images"**
- You need at least 500 images per letter
- Download a larger dataset from the links above

**"Images wrong format"**
- Convert to JPG using: https://www.iloveimg.com/convert-to-jpg
- Or keep as PNG (also works)

---

## 🔗 All Dataset Links

**GitHub:**
- https://github.com/yatharth77/Indian-Sign-Language-Gesture-Recognition

**Kaggle:**
- https://www.kaggle.com/datasets/prathumarikeri/indian-sign-language-isl
- https://www.kaggle.com/datasets/vaishnaviasonawane/indian-sign-language-dataset

**Research Datasets:**
- INCLUDE: https://zenodo.org/record/4010759
- ISL-CSLTR: https://www.kaggle.com/datasets/sujitmandal/islcsltr

---

## ✅ Quick Checklist

- [ ] Created `ml/dataset/isl_alphabets/` folder
- [ ] Downloaded ISL dataset ZIP file
- [ ] Extracted ZIP file
- [ ] Copied A-Z folders to project
- [ ] Verified structure with `python ml/download_dataset.py`
- [ ] Ready to train!

---

**Need help?** Just ask! 🚀
