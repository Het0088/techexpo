# spaCy Installation Fix for Windows

## ❌ Problem:
`python -m spacy download en_core_web_sm` gets stuck/times out on Windows

## ✅ Solution:

### Method 1: Direct pip install (FASTEST)

```bash
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl
```

**This:**
- Downloads from GitHub (faster)
- Bypasses spaCy's download system
- Works on Windows
- Takes 1-2 minutes

---

### Method 2: Manual download + install

1. **Download manually:**
   - Go to: https://github.com/explosion/spacy-models/releases/tag/en_core_web_sm-3.7.1
   - Download: `en_core_web_sm-3.7.1-py3-none-any.whl`

2. **Install locally:**
   ```bash
   pip install path/to/en_core_web_sm-3.7.1-py3-none-any.whl
   ```

---

### Method 3: Use it without local install (for deployment)

**On server (Linux), it works fine:**
```bash
python -m spacy download en_core_web_sm
# Works in 30 seconds on Render/Railway!
```

**So you can:**
- Keep NLTK/rules locally for development
- Use spaCy on production server only

---

## 🧪 Test spaCy after install:

```bash
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('✅ spaCy working!')"
```

---

## 🎯 Recommended Approach:

**For Local Development (Windows):**
```bash
# Install spaCy model via direct pip
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl

# Verify
python test_spacy.py
```

**For Production (Linux server):**
```txt
# In requirements.txt
spacy==3.7.2

# In app startup or Procfile
python -m spacy download en_core_web_sm
```

**Works perfectly on Render.com FREE tier!** ✅
