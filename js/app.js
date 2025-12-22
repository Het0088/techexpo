const API_BASE_URL = 'http://localhost:5000/api';
let webcamStream = null;
let isWebcamActive = false;
let currentMode = 'alphabet';
let predictionInterval = null;
let currentLanguage = 'en'; // Default language: English
let voiceEnabled = false;
let speechSynthesis = window.speechSynthesis;
let availableVoices = [];
const webcam = document.getElementById('webcam');
const canvas = document.getElementById('canvas');
const videoOverlay = document.getElementById('videoOverlay');
const startWebcamBtn = document.getElementById('startWebcam');
const predictionResult = document.getElementById('predictionResult');
const confidenceBars = document.getElementById('confidenceBars');
const modeBtns = document.querySelectorAll('.mode-btn');
const textInput = document.getElementById('textInput');
const convertBtn = document.getElementById('convertBtn');
const signsOutput = document.getElementById('signsOutput');
const alphabetGrid = document.getElementById('alphabetGrid');
const languageSelect = document.getElementById('languageSelect');
const voiceToggle = document.getElementById('voiceToggle');
const suggestionsDropdown = document.getElementById('suggestionsDropdown');
const suggestionChips = document.querySelectorAll('.suggestion-chip');
const commonPhrases = [
    { word: 'hello', icon: '👋', category: 'greeting' },
    { word: 'hi', icon: '👋', category: 'greeting' },
    { word: 'thank you', icon: '🙏', category: 'courtesy' },
    { word: 'thanks', icon: '🙏', category: 'courtesy' },
    { word: 'please', icon: '🙂', category: 'courtesy' },
    { word: 'sorry', icon: '😔', category: 'courtesy' },
    { word: 'excuse me', icon: '🙋', category: 'courtesy' },
    { word: 'yes', icon: '✅', category: 'response' },
    { word: 'no', icon: '❌', category: 'response' },
    { word: 'okay', icon: '👌', category: 'response' },
    { word: 'help', icon: '🆘', category: 'emergency' },
    { word: 'help me', icon: '🆘', category: 'emergency' },
    { word: 'emergency', icon: '🚨', category: 'emergency' },
    { word: 'good morning', icon: '🌅', category: 'greeting' },
    { word: 'good afternoon', icon: '☀️', category: 'greeting' },
    { word: 'good evening', icon: '🌆', category: 'greeting' },
    { word: 'good night', icon: '🌙', category: 'greeting' },
    { word: 'goodbye', icon: '👋', category: 'greeting' },
    { word: 'how are you', icon: '😊', category: 'conversation' },
    { word: 'what is your name', icon: '👤', category: 'conversation' },
    { word: 'my name is', icon: '🏷️', category: 'conversation' },
    { word: 'nice to meet you', icon: '🤝', category: 'conversation' },
    { word: 'where', icon: '📍', category: 'question' },
    { word: 'when', icon: '⏰', category: 'question' },
    { word: 'why', icon: '❓', category: 'question' },
    { word: 'how', icon: '🤔', category: 'question' },
    { word: 'what', icon: '❓', category: 'question' },
    { word: 'who', icon: '👤', category: 'question' },
    { word: 'water', icon: '💧', category: 'needs' },
    { word: 'food', icon: '🍽️', category: 'needs' },
    { word: 'bathroom', icon: '🚻', category: 'needs' },
    { word: 'hospital', icon: '🏥', category: 'places' },
    { word: 'home', icon: '🏠', category: 'places' },
    { word: 'school', icon: '🏫', category: 'places' },
    { word: 'work', icon: '💼', category: 'places' },
    { word: 'happy', icon: '😊', category: 'emotions' },
    { word: 'sad', icon: '😢', category: 'emotions' },
    { word: 'angry', icon: '😠', category: 'emotions' },
    { word: 'tired', icon: '😴', category: 'emotions' },
    { word: 'love', icon: '❤️', category: 'emotions' },
    { word: 'family', icon: '👨‍👩‍👧‍👦', category: 'people' },
    { word: 'friend', icon: '👥', category: 'people' },
    { word: 'mother', icon: '👩', category: 'people' },
    { word: 'father', icon: '👨', category: 'people' },
    { word: 'brother', icon: '👦', category: 'people' },
    { word: 'sister', icon: '👧', category: 'people' },
];
const translations = {
    en: {
        languageChanged: 'Language changed to English',
        voiceEnabled: 'Voice assistance enabled',
        voiceDisabled: 'Voice assistance disabled',
        detected: 'Detected',
        confidence: 'confidence',
        waiting: 'Waiting for recognition...',
        buildingSequence: 'Building sequence...'
    },
    hi: {
        languageChanged: 'भाषा बदलकर हिंदी कर दी गई',
        voiceEnabled: 'आवाज सहायता सक्षम',
        voiceDisabled: 'आवाज सहायता अक्षम',
        detected: 'पहचाना गया',
        confidence: 'विश्वास',
        waiting: 'पहचान की प्रतीक्षा में...',
        buildingSequence: 'अनुक्रम बना रहे हैं...'
    },
    gu: {
        languageChanged: 'ભાષા ગુજરાતીમાં બદલી',
        voiceEnabled: 'અવાજ સહાય સક્ષમ',
        voiceDisabled: 'અવાજ સહાય અક્ષમ',
        detected: 'શોધાયેલ',
        confidence: 'વિશ્વાસ',
        waiting: 'ઓળખની રાહ જોઈ રહ્યા છીએ...',
        buildingSequence: 'ક્રમ બનાવી રહ્યા છીએ...'
    }
};
document.addEventListener('DOMContentLoaded', () => {
    initEventListeners();
    generateAlphabetGrid();
    checkAPIHealth();
    createSuggestionChips();
    initializePhraseLibrary();
    initializeGallery();
    loadVoices();
    if (speechSynthesis.onvoiceschanged !== undefined) {
        speechSynthesis.onvoiceschanged = loadVoices;
    }
});
/**
 * Load available voices
 */
function loadVoices() {
    availableVoices = speechSynthesis.getVoices();
    console.log('Available voices loaded:', availableVoices.length);
}
/**
 * Get translation for current language
 */
function getTranslation(key) {
    return translations[currentLanguage][key] || translations['en'][key];
}
/**
 * Initialize event listeners
 */
function initEventListeners() {
    if (startWebcamBtn) {
        startWebcamBtn.addEventListener('click', startWebcam);
    }
    modeBtns.forEach(btn => {
        btn.addEventListener('click', () => switchMode(btn.dataset.mode));
    });
    if (languageSelect) {
        languageSelect.addEventListener('change', (e) => {
            currentLanguage = e.target.value;
            console.log('Language changed to:', currentLanguage);
            speak(getTranslation('languageChanged'));
        });
    }
    if (voiceToggle) {
        voiceToggle.addEventListener('click', toggleVoice);
    }
    if (convertBtn) {
        convertBtn.addEventListener('click', convertTextToSign);
    }
    if (textInput) {
        textInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') convertTextToSign();
        });
        textInput.addEventListener('input', handleTextInput);
        textInput.addEventListener('blur', () => {
            setTimeout(() => hideSuggestions(), 200);
        });
        textInput.addEventListener('focus', () => {
            if (textInput.value.trim()) {
                showSuggestions(textInput.value);
            }
        });
    }
    const menuToggle = document.getElementById('menuToggle');
    if (menuToggle) {
        menuToggle.addEventListener('click', () => {
            const navMenu = document.querySelector('.nav-menu');
            navMenu.style.display = navMenu.style.display === 'flex' ? 'none' : 'flex';
        });
    }
    initInvolvementNavigation();
}
/**
 * Enable click-through on involvement cards
 */
function initInvolvementNavigation() {
    const cards = document.querySelectorAll('.involvement-card');
    cards.forEach(card => {
        const primaryLink = card.dataset.link || card.querySelector('a.btn')?.getAttribute('href');
        if (!primaryLink || primaryLink === '#') return;
        card.style.cursor = 'pointer';
        card.addEventListener('click', (event) => {
            if (event.target.closest('a')) return; // allow built-in anchor behavior
            window.location.href = primaryLink;
        });
        const cta = card.querySelector('a.btn');
        if (cta && (!cta.getAttribute('href') || cta.getAttribute('href') === '#')) {
            cta.setAttribute('href', primaryLink);
        }
    });
}
/**
 * Check API health
 */
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE_URL.replace('/api', '')}/health`);
        const data = await response.json();
        console.log('API Health:', data);
        if (!data.alphabet_model_loaded && !data.word_model_loaded) {
            showNotification('⚠️ Models not loaded. Please train the models first.', 'warning');
        }
    } catch (error) {
        console.error('API not available:', error);
        showNotification('⚠️ Backend server not running. Start with: python app.py', 'error');
    }
}
/**
 * Start webcam
 */
async function startWebcam() {
    try {
        webcamStream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 640 },
                height: { ideal: 480 }
            }
        });
        webcam.srcObject = webcamStream;
        videoOverlay.style.display = 'none';
        isWebcamActive = true;
        startPredictionLoop();
        console.log('Webcam started successfully');
    } catch (error) {
        console.error('Error accessing webcam:', error);
        showNotification('❌ Could not access webcam. Please check permissions.', 'error');
    }
}
/**
 * Stop webcam
 */
function stopWebcam() {
    if (webcamStream) {
        webcamStream.getTracks().forEach(track => track.stop());
        webcamStream = null;
        isWebcamActive = false;
        videoOverlay.style.display = 'flex';
    }
    if (predictionInterval) {
        clearInterval(predictionInterval);
        predictionInterval = null;
    }
}
/**
 * Switch between alphabet and word mode
 */
function switchMode(mode) {
    currentMode = mode;
    modeBtns.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.mode === mode);
    });
    predictionResult.innerHTML = `<span class="result-label">${getTranslation('waiting')}</span>`;
    confidenceBars.innerHTML = '';
    if (mode === 'word') {
        resetWordSequence();
    }
    console.log('Switched to mode:', mode);
}
/**
 * Start prediction loop
 */
function startPredictionLoop() {
    if (predictionInterval) {
        clearInterval(predictionInterval);
    }
    const interval = currentMode === 'alphabet' ? 500 : 100;
    predictionInterval = setInterval(() => {
        if (isWebcamActive) {
            captureAndPredict();
        }
    }, interval);
}
/**
 * Capture frame and send for prediction
 */
async function captureAndPredict() {
    if (!webcam.videoWidth || !webcam.videoHeight) return;
    canvas.width = webcam.videoWidth;
    canvas.height = webcam.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(webcam, 0, 0);
    const imageData = canvas.toDataURL('image/jpeg', 0.8);
    try {
        const endpoint = currentMode === 'alphabet' ? '/predict/alphabet' : '/predict/word';
        const response = await fetch(API_BASE_URL + endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ image: imageData })
        });
        const result = await response.json();
        if (result.error) {
            console.error('Prediction error:', result.error);
            return;
        }
        if (currentMode === 'alphabet') {
            displayAlphabetPrediction(result);
        } else {
            displayWordPrediction(result);
        }
    } catch (error) {
        console.error('Prediction request failed:', error);
    }
}
/**
 * Display alphabet prediction
 */
function displayAlphabetPrediction(result) {
    predictionResult.innerHTML = `
        <div class="result-letter">${result.letter}</div>
        <div class="result-confidence">${(result.confidence * 100).toFixed(1)}% ${getTranslation('confidence')}</div>
    `;
    speak(`${getTranslation('detected')} ${result.letter}`);
    confidenceBars.innerHTML = result.top_predictions.map(pred => `
        <div class="confidence-bar">
            <div class="bar-label">${pred.letter}</div>
            <div class="bar-track">
                <div class="bar-fill" style="width: ${pred.confidence * 100}%"></div>
            </div>
            <div class="bar-value">${(pred.confidence * 100).toFixed(1)}%</div>
        </div>
    `).join('');
}
/**
 * Display word prediction
 */
function displayWordPrediction(result) {
    if (result.ready) {
        predictionResult.innerHTML = `
            <div class="result-letter">${result.word}</div>
            <div class="result-confidence">${(result.confidence * 100).toFixed(1)}% ${getTranslation('confidence')}</div>
        `;
        speak(`${getTranslation('detected')} ${result.word}`);
    } else {
        predictionResult.innerHTML = `
            <span class="result-label">${getTranslation('buildingSequence')}</span>
        `;
    }
}
/**
 * Reset word sequence buffer
 */
async function resetWordSequence() {
    try {
        await fetch(API_BASE_URL + '/reset', {
            method: 'POST'
        });
    } catch (error) {
        console.error('Failed to reset sequence:', error);
    }
}
/**
 * Convert text to sign language
 */
async function convertTextToSign() {
    const text = textInput.value.trim().toLowerCase();
    if (!text) {
        showNotification('Please enter some text', 'info');
        return;
    }
    signsOutput.innerHTML = '<div class="placeholder-text"><p>Converting to signs...</p></div>';
    const knownWords = {
        'hello': { type: 'word', word: 'Hello', image: 'images/words/hello.png', icon: '👋' },
        'hi': { type: 'word', word: 'Hi', image: 'images/words/hello.png', icon: '👋' },
        'thank you': { type: 'word', word: 'Thank You', image: 'images/words/thank-you.png', icon: '🙏' },
        'thanks': { type: 'word', word: 'Thanks', image: 'images/words/thank-you.png', icon: '🙏' },
        'please': { type: 'word', word: 'Please', image: 'images/words/please.png', icon: '🙂' },
        'sorry': { type: 'word', word: 'Sorry', image: 'images/words/sorry.png', icon: '😔' },
        'yes': { type: 'word', word: 'Yes', image: 'images/words/yes.png', icon: '✅' },
        'no': { type: 'word', word: 'No', image: 'images/words/no.png', icon: '❌' },
        'help': { type: 'word', word: 'Help', image: 'images/words/help.png', icon: '🆘' },
        'love': { type: 'word', word: 'Love', image: 'images/words/love.png', icon: '❤️' },
        'good': { type: 'word', word: 'Good', image: 'images/words/good.png', icon: '👍' },
        'bad': { type: 'word', word: 'Bad', image: 'images/words/bad.png', icon: '👎' },
        'happy': { type: 'word', word: 'Happy', image: 'images/words/happy.png', icon: '😊' },
        'sad': { type: 'word', word: 'Sad', image: 'images/words/sad.png', icon: '😢' }
    };
    if (knownWords[text]) {
        displaySignsFromLocal([knownWords[text]]);
        return;
    }
    try {
        const response = await fetch(API_BASE_URL + '/text-to-sign', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text })
        });
        const result = await response.json();
        if (result.error) {
            displaySignsFromLocal(convertToAlphabet(text));
            return;
        }
        displaySigns(result.signs);
    } catch (error) {
        console.error('Text to sign conversion failed, using alphabet fallback:', error);
        displaySignsFromLocal(convertToAlphabet(text));
    }
}
/**
 * Convert text to alphabet signs
 */
function convertToAlphabet(text) {
    const letters = text.replace(/[^a-zA-Z0-9\s]/g, '').toUpperCase().split('');
    return letters.map(char => {
        if (char === ' ') {
            return { type: 'space', word: 'Space' };
        } else if (/\d/.test(char)) {
            return { type: 'number', word: char, image: `images/numbers/${char}.png` };
        } else {
            return { type: 'letter', word: char, image: `images/alphabet/${char}.png` };
        }
    });
}
/**
 * Display signs from local data
 */
function displaySignsFromLocal(signs) {
    if (!signs || signs.length === 0) {
        signsOutput.innerHTML = '<div class="placeholder-text"><p>No signs to display</p></div>';
        return;
    }
    signsOutput.innerHTML = signs.map(sign => {
        if (sign.type === 'space') {
            return '<div class="sign-card space-card"><div class="space-indicator">[ Space ]</div></div>';
        }
        const fallbackSvg = (ch) => {
            const svg = `<?xml version="1.0" encoding="UTF-8"?><svg xmlns='http://www.w3.org/2000/svg' width='200' height='200'><rect width='200' height='200' rx='12' fill='%23f7f9fc'/><text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' font-family='Poppins, Arial, sans-serif' font-size='100' font-weight='800' fill='%231e3a8a'>${ch}</text></svg>`;
            return `data:image/svg+xml,${encodeURIComponent(svg)}`;
        };
        return `
            <div class="sign-card" data-word="${sign.word}">
                <div class="sign-image-wrapper">
                    <img src="${sign.image || fallbackSvg(sign.word)}" 
                         alt="Sign for ${sign.word}" 
                         class="sign-image"
                         onerror="this.src='${fallbackSvg(sign.word)}'">
                </div>
                <div class="sign-word">${sign.icon || ''} ${sign.word}</div>
            </div>
        `;
    }).join('');
}
/**
 * Display sign language signs
 */
function displaySigns(signs) {
    if (!signs || signs.length === 0) {
        signsOutput.innerHTML = '<div class="placeholder-text"><p>No signs to display</p></div>';
        return;
    }
    signsOutput.innerHTML = signs.map(sign => {
        if (sign.type === 'image') {
            return `
                <div class="sign-card">
                    <img src="${sign.url}" alt="${sign.word}" onerror="this.src='assets/images/placeholder.jpg'">
                    <div class="sign-word">${sign.word}</div>
                </div>
            `;
        } else if (sign.type === 'video') {
            return `
                <div class="sign-card">
                    <video src="${sign.url}" autoplay loop muted></video>
                    <div class="sign-word">${sign.word}</div>
                </div>
            `;
        } else if (sign.type === 'alphabet') {
            return sign.letters.map(letter => `
                <div class="sign-card alphabet-sign">
                    <div class="alphabet-letter">${letter.toUpperCase()}</div>
                    <div class="sign-word">(${sign.word})</div>
                </div>
            `).join('');
        }
        return '';
    }).join('');
}
/**
 * Generate alphabet reference grid
 */
function generateAlphabetGrid() {
    if (!alphabetGrid) return;
    const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');
    alphabetGrid.innerHTML = alphabet.map(letter => `
        <div class="alphabet-card" data-letter="${letter}">
            <div class="alphabet-letter">${letter}</div>
            <img 
                src="assets/alphabet/${letter}.jpg" 
                alt="ISL sign for ${letter}"
                class="alphabet-image"
                onerror="this.style.display='none'"
            >
        </div>
    `).join('');
    document.querySelectorAll('.alphabet-card').forEach(card => {
        card.addEventListener('click', () => {
            const letter = card.dataset.letter;
            showLetterDetail(letter);
        });
    });
}
/**
 * Show letter detail (modal or expanded view)
 */
function showLetterDetail(letter) {
    console.log('Selected letter:', letter);
}
/**
 * Toggle voice assistance
 */
function toggleVoice(event) {
    if (event) event.preventDefault();
    console.log('Voice toggle clicked! Current state:', voiceEnabled);
    voiceEnabled = !voiceEnabled;
    if (voiceToggle) {
        if (voiceEnabled) {
            voiceToggle.classList.add('active');
        } else {
            voiceToggle.classList.remove('active');
        }
        const voiceText = voiceToggle.querySelector('.voice-text');
        const voiceIcon = voiceToggle.querySelector('.icon');
        if (voiceText) {
            voiceText.textContent = voiceEnabled ? 'Voice: ON' : 'Voice: OFF';
        }
        if (voiceIcon) {
            voiceIcon.textContent = voiceEnabled ? '🔊' : '🔇';
        }
    }
    console.log('Voice assistance now:', voiceEnabled ? 'ENABLED ✓' : 'DISABLED ✗');
    const message = voiceEnabled ? getTranslation('voiceEnabled') : getTranslation('voiceDisabled');
    if (voiceEnabled) {
        setTimeout(() => speak(message), 100);
    }
}
/**
 * Text-to-Speech function
 */
function speak(text) {
    if (!voiceEnabled || !text) {
        console.log('Speech skipped:', voiceEnabled ? 'no text' : 'voice disabled');
        return;
    }
    console.log('Speaking:', text);
    speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    const voiceLang = {
        'en': 'en-US',
        'hi': 'hi-IN',
        'gu': 'gu-IN'
    };
    utterance.lang = voiceLang[currentLanguage] || 'en-US';
    utterance.rate = 0.9;
    utterance.pitch = 1;
    utterance.volume = 1;
    if (availableVoices.length === 0) {
        availableVoices = speechSynthesis.getVoices();
    }
    const preferredVoice = availableVoices.find(voice =>
        voice.lang.includes(currentLanguage) || voice.lang.includes(voiceLang[currentLanguage])
    );
    if (preferredVoice) {
        utterance.voice = preferredVoice;
        console.log('Using voice:', preferredVoice.name);
    } else {
        console.log('No specific voice found, using default');
    }
    utterance.onerror = (event) => {
        console.error('Speech error:', event);
    };
    speechSynthesis.speak(utterance);
}
/**
 * Show notification
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: ${type === 'error' ? '#ef4444' : type === 'warning' ? '#f59e0b' : '#3b82f6'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    document.body.appendChild(notification);
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}
/**
 * Handle text input for suggestions
 */
function handleTextInput(e) {
    const value = e.target.value.toLowerCase().trim();
    if (value.length > 0) {
        showSuggestions(value);
    } else {
        hideSuggestions();
    }
}
/**
 * Show word suggestions based on input
 */
function showSuggestions(inputValue) {
    if (!suggestionsDropdown) return;
    const matchingPhrases = commonPhrases.filter(phrase =>
        phrase.word.toLowerCase().includes(inputValue.toLowerCase())
    );
    if (matchingPhrases.length === 0) {
        hideSuggestions();
        return;
    }
    suggestionsDropdown.innerHTML = '';
    matchingPhrases.slice(0, 8).forEach(phrase => {
        const item = document.createElement('div');
        item.className = 'suggestion-item';
        item.innerHTML = `
            <span class="suggestion-icon">${phrase.icon}</span>
            <span class="suggestion-text">${phrase.word}</span>
        `;
        item.addEventListener('click', () => selectSuggestion(phrase.word));
        suggestionsDropdown.appendChild(item);
    });
    suggestionsDropdown.classList.add('show');
}
/**
 * Hide suggestions dropdown
 */
function hideSuggestions() {
    if (suggestionsDropdown) {
        suggestionsDropdown.classList.remove('show');
    }
}
/**
 * Select a suggestion
 */
function selectSuggestion(word) {
    if (textInput) {
        textInput.value = word;
        hideSuggestions();
        textInput.focus();
    }
}
/**
 * Create quick suggestion chips
 */
function createSuggestionChips() {
    const chipsContainer = document.getElementById('suggestionChips');
    if (!chipsContainer) return;
    const popularPhrases = [
        { word: 'hello', icon: '👋' },
        { word: 'thank you', icon: '🙏' },
        { word: 'help', icon: '🆘' },
        { word: 'yes', icon: '✅' },
        { word: 'no', icon: '❌' },
        { word: 'please', icon: '🙂' },
        { word: 'sorry', icon: '😔' },
        { word: 'how are you', icon: '😊' }
    ];
    popularPhrases.forEach(phrase => {
        const chip = document.createElement('span');
        chip.className = 'suggestion-chip';
        chip.innerHTML = `${phrase.icon} ${phrase.word}`;
        chip.addEventListener('click', () => {
            if (textInput) {
                textInput.value = phrase.word;
                textInput.focus();
                convertTextToSign();
            }
        });
        chipsContainer.appendChild(chip);
    });
}
/**
 * Initialize Phrase Library
 */
function initializePhraseLibrary() {
    const phrasesGrid = document.getElementById('phrasesGrid');
    const phraseModal = document.getElementById('phraseModal');
    const modalClose = document.getElementById('modalClose');
    const categoryBtns = document.querySelectorAll('.category-btn');
    if (!phrasesGrid) return;
    const phraseLibrary = [
        {
            word: 'hello',
            icon: '👋',
            category: 'greeting',
            meaning: 'A greeting used when meeting someone',
            usage: 'Wave your hand with palm facing forward'
        },
        {
            word: 'thank you',
            icon: '🙏',
            category: 'courtesy',
            meaning: 'Expression of gratitude',
            usage: 'Touch your chin with your fingers and move hand forward'
        },
        {
            word: 'help',
            icon: '🆘',
            category: 'emergency',
            meaning: 'Request for assistance',
            usage: 'Raise your hand and shake it'
        },
        {
            word: 'yes',
            icon: '✅',
            category: 'daily',
            meaning: 'Affirmative response',
            usage: 'Nod your head or make a fist and move up and down'
        },
        {
            word: 'no',
            icon: '❌',
            category: 'daily',
            meaning: 'Negative response',
            usage: 'Shake your head or wave hand from side to side'
        },
        {
            word: 'please',
            icon: '🙂',
            category: 'courtesy',
            meaning: 'Polite request',
            usage: 'Place hand on chest and move in circular motion'
        },
        {
            word: 'sorry',
            icon: '😔',
            category: 'courtesy',
            meaning: 'Expression of apology',
            usage: 'Make a fist and rub in circular motion on chest'
        },
        {
            word: 'good morning',
            icon: '🌅',
            category: 'greeting',
            meaning: 'Morning greeting',
            usage: 'Sign "good" then "morning"'
        },
        {
            word: 'how are you',
            icon: '😊',
            category: 'greeting',
            meaning: 'Inquiry about wellbeing',
            usage: 'Point to person, then sign "good" with questioning expression'
        },
        {
            word: 'happy',
            icon: '😊',
            category: 'emotions',
            meaning: 'Feeling of joy',
            usage: 'Pat chest upward repeatedly with both hands'
        },
        {
            word: 'sad',
            icon: '😢',
            category: 'emotions',
            meaning: 'Feeling of sorrow',
            usage: 'Draw hands down face showing emotion'
        },
        {
            word: 'love',
            icon: '❤️',
            category: 'emotions',
            meaning: 'Deep affection',
            usage: 'Cross arms over chest'
        },
        {
            word: 'water',
            icon: '💧',
            category: 'daily',
            meaning: 'H2O liquid for drinking',
            usage: 'Make W shape and tap on chin'
        },
        {
            word: 'food',
            icon: '🍽️',
            category: 'daily',
            meaning: 'Edible items',
            usage: 'Bring hand to mouth repeatedly'
        },
        {
            word: 'home',
            icon: '🏠',
            category: 'daily',
            meaning: 'Place of residence',
            usage: 'Make roof shape with hands'
        }
    ];
    let currentCategory = 'all';
    function displayPhrases(category = 'all') {
        const filtered = category === 'all'
            ? phraseLibrary
            : phraseLibrary.filter(p => p.category === category);
        phrasesGrid.innerHTML = filtered.map(phrase => `
            <div class="phrase-card" data-phrase='${JSON.stringify(phrase)}'>
                <div class="phrase-icon">${phrase.icon}</div>
                <div class="phrase-content">
                    <div class="phrase-text">${phrase.word}</div>
                    <div class="phrase-category">${phrase.category}</div>
                </div>
            </div>
        `).join('');
        document.querySelectorAll('.phrase-card').forEach(card => {
            card.addEventListener('click', () => {
                const phraseData = JSON.parse(card.dataset.phrase);
                showPhraseModal(phraseData);
            });
        });
    }
    function showPhraseModal(phrase) {
        if (!phraseModal) return;
        document.getElementById('modalPhrase').textContent = phrase.word;
        document.getElementById('modalIcon').textContent = phrase.icon;
        document.getElementById('modalMeaning').textContent = phrase.meaning;
        document.getElementById('modalUsage').textContent = phrase.usage;
        phraseModal.classList.add('show');
    }
    if (modalClose) {
        modalClose.addEventListener('click', () => {
            phraseModal.classList.remove('show');
        });
    }
    if (phraseModal) {
        phraseModal.addEventListener('click', (e) => {
            if (e.target === phraseModal) {
                phraseModal.classList.remove('show');
            }
        });
    }
    categoryBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            categoryBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentCategory = btn.dataset.category;
            displayPhrases(currentCategory);
        });
    });
    displayPhrases();
}
/**
 * Initialize Gallery
 */
function initializeGallery() {
    const galleryTabs = document.querySelectorAll('.gallery-tab');
    const galleryPanels = document.querySelectorAll('.gallery-panel');
    if (galleryTabs.length === 0 || galleryPanels.length === 0) {
        return; // Gallery not on this page
    }
    const alphabetGallery = document.getElementById('alphabetGallery');
    if (alphabetGallery) {
        const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');
        const alphabetImageBase = 'images/alphabet';
        const alphabetInfo = {
            'A': 'Closed fist with thumb up',
            'B': 'Flat hand, fingers together',
            'C': 'Curved hand forming C shape',
            'D': 'Index finger up, other fingers touch thumb',
            'E': 'All fingers curled, thumb across',
            'F': 'Index and thumb form circle',
            'G': 'Index and thumb point sideways',
            'H': 'Index and middle fingers extended sideways',
            'I': 'Pinky finger up, fist closed',
            'J': 'Draw J shape with pinky',
            'K': 'Index up, middle out, thumb between',
            'L': 'L shape with thumb and index',
            'M': 'Thumb under three fingers',
            'N': 'Thumb under two fingers',
            'O': 'All fingers form O shape',
            'P': 'K handshape pointing down',
            'Q': 'Point down with index and thumb',
            'R': 'Cross index over middle finger',
            'S': 'Closed fist, thumb across',
            'T': 'Thumb between index and middle',
            'U': 'Index and middle fingers up together',
            'V': 'Index and middle fingers apart',
            'W': 'Three fingers up in W shape',
            'X': 'Hook index finger',
            'Y': 'Thumb and pinky extended',
            'Z': 'Draw Z shape with index finger'
        };
        alphabetGallery.innerHTML = alphabet.map(letter => `
            <div class="gallery-card" data-letter="${letter}" data-description="${alphabetInfo[letter]}" data-image="${alphabetImageBase}/${letter}.png">
                <div class="gallery-sign-img">
                    <div class="sign-placeholder">${letter}</div>
                </div>
                <div class="gallery-label">Letter ${letter}</div>
                <div class="sign-description">${alphabetInfo[letter]}</div>
            </div>
        `).join('');
    }
    const numbersGallery = document.getElementById('numbersGallery');
    if (numbersGallery) {
        const numbersInfo = [
            { num: '0', desc: 'Make O shape with hand', tip: 'Circle with thumb and fingers' },
            { num: '1', desc: 'Point index finger up', tip: 'Other fingers closed' },
            { num: '2', desc: 'Index and middle fingers up', tip: 'V for victory shape' },
            { num: '3', desc: 'Thumb, index, middle up', tip: 'Three fingers extended' },
            { num: '4', desc: 'Four fingers up, no thumb', tip: 'Palm facing forward' },
            { num: '5', desc: 'All five fingers spread', tip: 'Open hand, palm out' },
            { num: '6', desc: 'Three fingers up, thumb touches pinky', tip: 'Modified 3 position' },
            { num: '7', desc: 'Thumb, index, middle, ring up', tip: 'Four fingers, pinky down' },
            { num: '8', desc: 'Middle, ring, pinky touch thumb', tip: 'Index finger up' },
            { num: '9', desc: 'Touch thumb to index', tip: 'Make small circle' }
        ];
        numbersGallery.innerHTML = numbersInfo.map(item => `
            <div class="gallery-card" data-letter="${item.num}" data-description="${item.desc}" data-image="images/numbers/${item.num}.png">
                <div class="gallery-sign-img">
                    <div class="sign-placeholder">${item.num}</div>
                </div>
                <div class="gallery-label">Number ${item.num}</div>
                <div class="sign-description">${item.desc}</div>
                <div class="sign-tip">💡 ${item.tip}</div>
            </div>
        `).join('');
    }
    const gestureModal = document.getElementById('gestureModal');
    const gestureImg = document.getElementById('gestureImg');
    const gestureTitle = document.getElementById('gestureTitle');
    const gestureDesc = document.getElementById('gestureDesc');
    const gestureLetter = document.getElementById('gestureLetter');
    const gestureFallback = document.getElementById('gestureFallback');
    const gestureClose = document.getElementById('gestureModalClose');
    const hideGestureModal = () => {
        if (gestureModal) {
            gestureModal.classList.remove('show');
        }
    };
    if (gestureClose) {
        gestureClose.addEventListener('click', hideGestureModal);
    }
    if (gestureModal) {
        gestureModal.addEventListener('click', (e) => {
            if (e.target === gestureModal) hideGestureModal();
        });
    }
    if (alphabetGallery && gestureModal) {
        alphabetGallery.addEventListener('click', (e) => {
            const card = e.target.closest('.gallery-card');
            if (!card) return;
            const letter = (card.dataset.letter || card.querySelector('.sign-placeholder')?.textContent || '').trim();
            if (!letter) return;
            const description = (card.dataset.description || card.querySelector('.sign-description')?.textContent || '').trim();
            const imageSrc = card.dataset.image || `images/alphabet/${letter}.png`;
            const fallbackSvg = (ch) => {
                const svg = `<?xml version="1.0" encoding="UTF-8"?><svg xmlns='http://www.w3.org/2000/svg' width='400' height='400'><rect width='400' height='400' rx='24' fill='%23f7f9fc'/><text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' font-family='Poppins, Arial, sans-serif' font-size='200' font-weight='800' fill='%231e3a8a'>${ch}</text></svg>`;
                return `data:image/svg+xml,${encodeURIComponent(svg)}`;
            };
            if (gestureTitle) gestureTitle.textContent = `Letter ${letter}`;
            if (gestureDesc) gestureDesc.textContent = description;
            if (gestureLetter) {
                gestureLetter.textContent = letter;
                gestureLetter.style.display = 'block';
            }
            if (gestureImg) {
                gestureImg.style.display = 'block';
                gestureImg.onload = () => {
                    gestureImg.style.display = 'block';
                    if (gestureLetter) gestureLetter.style.display = 'none';
                    if (gestureFallback) gestureFallback.style.display = 'none';
                };
                gestureImg.onerror = () => {
                    const svgUrl = fallbackSvg(letter);
                    if (gestureImg.src !== svgUrl) {
                        gestureImg.src = svgUrl;
                        return;
                    }
                    gestureImg.style.display = 'none';
                    if (gestureLetter) gestureLetter.style.display = 'block';
                    if (gestureFallback) gestureFallback.style.display = 'block';
                };
                if (gestureFallback) gestureFallback.style.display = 'none';
                gestureImg.src = imageSrc || fallbackSvg(letter);
                gestureImg.alt = `Gesture for letter ${letter}`;
            }
            gestureModal.classList.add('show');
        });
    }
    if (numbersGallery && gestureModal) {
        numbersGallery.addEventListener('click', (e) => {
            const card = e.target.closest('.gallery-card');
            if (!card) return;
            const number = (card.dataset.letter || card.querySelector('.sign-placeholder')?.textContent || '').trim();
            if (!number) return;
            const description = (card.dataset.description || card.querySelector('.sign-description')?.textContent || '').trim();
            const imageSrc = card.dataset.image || `images/numbers/${number}.png`;
            const fallbackSvg = (ch) => {
                const svg = `<?xml version="1.0" encoding="UTF-8"?><svg xmlns='http://www.w3.org/2000/svg' width='400' height='400'><rect width='400' height='400' rx='24' fill='%23f7f9fc'/><text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' font-family='Poppins, Arial, sans-serif' font-size='200' font-weight='800' fill='%231e3a8a'>${ch}</text></svg>`;
                return `data:image/svg+xml,${encodeURIComponent(svg)}`;
            };
            if (gestureTitle) gestureTitle.textContent = `Number ${number}`;
            if (gestureDesc) gestureDesc.textContent = description;
            if (gestureLetter) {
                gestureLetter.textContent = number;
                gestureLetter.style.display = 'block';
            }
            if (gestureImg) {
                gestureImg.style.display = 'block';
                gestureImg.onload = () => {
                    gestureImg.style.display = 'block';
                    if (gestureLetter) gestureLetter.style.display = 'none';
                    if (gestureFallback) gestureFallback.style.display = 'none';
                };
                gestureImg.onerror = () => {
                    const svgUrl = fallbackSvg(number);
                    if (gestureImg.src !== svgUrl) {
                        gestureImg.src = svgUrl;
                        return;
                    }
                    gestureImg.style.display = 'none';
                    if (gestureLetter) gestureLetter.style.display = 'block';
                    if (gestureFallback) gestureFallback.style.display = 'block';
                };
                if (gestureFallback) gestureFallback.style.display = 'none';
                gestureImg.src = imageSrc || fallbackSvg(number);
                gestureImg.alt = `Gesture for number ${number}`;
            }
            gestureModal.classList.add('show');
        });
    }
    const commonGallery = document.getElementById('commonGallery');
    if (commonGallery) {
        const commonWords = [
            { word: 'Hello', icon: '👋', desc: 'Wave hand side to side', usage: 'Greeting someone' },
            { word: 'Thank You', icon: '🙏', desc: 'Touch chin, move hand forward', usage: 'Showing gratitude' },
            { word: 'Love', icon: '❤️', desc: 'Cross arms over chest', usage: 'Expressing affection' },
            { word: 'Yes', icon: '✅', desc: 'Nod fist up and down', usage: 'Affirmative response' },
            { word: 'No', icon: '❌', desc: 'Shake head side to side', usage: 'Negative response' },
            { word: 'Help', icon: '🆘', desc: 'Fist on flat palm, lift up', usage: 'Requesting assistance' },
            { word: 'Please', icon: '🙂', desc: 'Circular motion on chest', usage: 'Making polite request' },
            { word: 'Sorry', icon: '😔', desc: 'Circular motion on chest', usage: 'Apologizing' },
            { word: 'Good', icon: '👍', desc: 'Thumbs up gesture', usage: 'Showing approval' },
            { word: 'Bad', icon: '👎', desc: 'Thumbs down gesture', usage: 'Showing disapproval' },
            { word: 'Happy', icon: '😊', desc: 'Brush chest upward twice', usage: 'Expressing joy' },
            { word: 'Sad', icon: '😢', desc: 'Hands down face, pull down', usage: 'Expressing sorrow' },
            { word: 'Eat', icon: '🍽️', desc: 'Bring hand to mouth', usage: 'Related to food' },
            { word: 'Drink', icon: '🥤', desc: 'Tilt hand to mouth like cup', usage: 'Related to beverages' },
            { word: 'Sleep', icon: '😴', desc: 'Rest head on hand', usage: 'Rest or bedtime' },
            { word: 'Learn', icon: '📚', desc: 'Grab from book to head', usage: 'Studying or education' }
        ];
        commonGallery.innerHTML = commonWords.map(item => `
            <div class="gallery-card" data-letter="${item.word}" data-description="${item.desc}" data-image="images/words/${item.word.toLowerCase().replace(/\s+/g, '-')}.png">
                <div class="gallery-sign-img">
                    <div class="sign-placeholder">${item.icon}</div>
                </div>
                <div class="gallery-label">${item.word}</div>
                <div class="sign-description">${item.desc}</div>
                <div class="sign-usage">📌 ${item.usage}</div>
            </div>
        `).join('');
    }
    if (commonGallery && gestureModal) {
        commonGallery.addEventListener('click', (e) => {
            const card = e.target.closest('.gallery-card');
            if (!card) return;
            const word = (card.dataset.letter || card.querySelector('.gallery-label')?.textContent || '').trim();
            if (!word) return;
            const description = (card.dataset.description || card.querySelector('.sign-description')?.textContent || '').trim();
            const imageSrc = card.dataset.image || `images/words/${word.toLowerCase().replace(/\s+/g, '-')}.png`;
            const fallbackSvg = (text) => {
                const fontSize = text.length > 5 ? '120' : '150';
                const svg = `<?xml version="1.0" encoding="UTF-8"?><svg xmlns='http://www.w3.org/2000/svg' width='400' height='400'><rect width='400' height='400' rx='24' fill='%23f7f9fc'/><text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' font-family='Poppins, Arial, sans-serif' font-size='${fontSize}' font-weight='700' fill='%231e3a8a'>${text}</text></svg>`;
                return `data:image/svg+xml,${encodeURIComponent(svg)}`;
            };
            if (gestureTitle) gestureTitle.textContent = word;
            if (gestureDesc) gestureDesc.textContent = description;
            if (gestureLetter) {
                gestureLetter.textContent = card.querySelector('.sign-placeholder')?.textContent || word;
                gestureLetter.style.display = 'block';
            }
            if (gestureImg) {
                gestureImg.style.display = 'block';
                gestureImg.onload = () => {
                    gestureImg.style.display = 'block';
                    if (gestureLetter) gestureLetter.style.display = 'none';
                    if (gestureFallback) gestureFallback.style.display = 'none';
                };
                gestureImg.onerror = () => {
                    const svgUrl = fallbackSvg(word);
                    if (gestureImg.src !== svgUrl) {
                        gestureImg.src = svgUrl;
                        return;
                    }
                    gestureImg.style.display = 'none';
                    if (gestureLetter) gestureLetter.style.display = 'block';
                    if (gestureFallback) gestureFallback.style.display = 'block';
                };
                if (gestureFallback) gestureFallback.style.display = 'none';
                gestureImg.src = imageSrc || fallbackSvg(word);
                gestureImg.alt = `Gesture for ${word}`;
            }
            gestureModal.classList.add('show');
        });
    }
    if (galleryTabs.length > 0) {
        galleryTabs.forEach(tab => {
            tab.addEventListener('click', function (e) {
                e.preventDefault();
                const targetTab = this.getAttribute('data-tab');
                console.log('Gallery tab clicked:', targetTab); // Debug log
                galleryTabs.forEach(t => t.classList.remove('active'));
                this.classList.add('active');
                galleryPanels.forEach(panel => {
                    panel.classList.remove('active');
                    if (panel.id === `gallery-${targetTab}`) {
                        panel.classList.add('active');
                        console.log('Showing panel:', panel.id); // Debug log
                    }
                });
            });
        });
        console.log('Gallery initialized with', galleryTabs.length, 'tabs'); // Debug log
    }
}
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    .result-letter {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #7c3aed, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .result-confidence {
        font-size: 1rem;
        color: rgba(255, 255, 255, 0.7);
        margin-top: 0.5rem;
    }
    .alphabet-sign {
        background: linear-gradient(135deg, rgba(124, 58, 237, 0.2), rgba(59, 130, 246, 0.2));
    }
`;
document.head.appendChild(style);
document.querySelectorAll('.gallery-tab').forEach(tab => {
    tab.addEventListener('click', () => {
        document.querySelectorAll('.gallery-tab').forEach(t => {
            t.style.background = 'white';
            t.style.color = 'var(--navy)';
            t.style.borderColor = 'var(--light-gray)';
        });
        document.querySelectorAll('.gallery-panel').forEach(panel => {
            panel.style.display = 'none';
        });
        tab.style.background = 'var(--primary-blue)';
        tab.style.color = 'white';
        tab.style.borderColor = 'var(--primary-blue)';
        const tabId = tab.getAttribute('data-tab');
        const target = document.getElementById(tabId);
        if (target) {
            target.style.display = 'grid';
        }
    });
});
document.getElementById('menuToggle')?.addEventListener('click', function () {
    const navMenu = document.querySelector('.nav-menu');
    navMenu.style.display = navMenu.style.display === 'flex' ? 'none' : 'flex';
});
function showSection(sectionId) {
    console.log('Switching to section:', sectionId);
    const homeSections = ['home', 'demo', 'explore'];
    document.querySelectorAll('section[id]').forEach(section => {
        section.classList.remove('active-section');
        section.style.display = 'none';
    });
    if (sectionId === 'home') {
        homeSections.forEach(id => {
            const section = document.getElementById(id);
            if (section) {
                section.classList.add('active-section');
                section.style.display = 'block';
            }
        });
    } else {
        const targetSection = document.getElementById(sectionId);
        if (targetSection) {
            targetSection.classList.add('active-section');
            targetSection.style.display = 'block';
        }
    }
    const scrollTarget = sectionId === 'home' ? document.body : document.getElementById(sectionId);
    if (scrollTarget) {
        scrollTarget.scrollIntoView({ behavior: 'instant', block: 'start' });
    }
    console.log('Showing section:', sectionId);
    if (sectionId === 'home' || sectionId === 'about') {
        document.body.classList.add('show-footer');
    } else {
        document.body.classList.remove('show-footer');
    }
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    const activeLink = document.querySelector(`a[href="#${sectionId}"]`);
    if (activeLink) {
        activeLink.classList.add('active');
    }
}
function getHashSectionId() {
    const hash = window.location.hash.replace('#', '').trim();
    if (hash && document.getElementById(hash)) {
        return hash;
    }
    return null;
}
function initNavigation() {
    console.log('Setting up navigation...');
    document.querySelectorAll('a[href^="#"]').forEach(link => {
        link.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href && href.startsWith('#') && href.length > 1) {
                e.preventDefault();
                const sectionId = href.substring(1);
                window.location.hash = sectionId;
                showSection(sectionId);
            }
        });
    });
    const initialSection = getHashSectionId() || 'home';
    console.log('Activating initial section:', initialSection);
    showSection(initialSection);
}
window.addEventListener('hashchange', () => {
    const sectionId = getHashSectionId() || 'home';
    showSection(sectionId);
});
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initNavigation);
} else {
    initNavigation();
}
window.addEventListener('beforeunload', () => {
    stopWebcam();
});
console.log('ISL Recognition Frontend - Ready! 🚀'); console.log('Version: 2.0 - Navigation Active');
