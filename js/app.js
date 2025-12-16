/**
 * ISL Recognition - Frontend JavaScript
 * Handles webcam, API calls, and UI interactions
 */

// API Configuration
const API_BASE_URL = 'http://localhost:5000/api';

// State
let webcamStream = null;
let isWebcamActive = false;
let currentMode = 'alphabet'; // 'alphabet' or 'word'
let predictionInterval = null;

// DOM Elements
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

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initEventListeners();
    generateAlphabetGrid();
    checkAPIHealth();
});

/**
 * Initialize event listeners
 */
function initEventListeners() {
    // Webcam controls
    startWebcamBtn.addEventListener('click', startWebcam);

    // Mode switching
    modeBtns.forEach(btn => {
        btn.addEventListener('click', () => switchMode(btn.dataset.mode));
    });

    // Text to sign conversion
    convertBtn.addEventListener('click', convertTextToSign);
    textInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') convertTextToSign();
    });

    // Smooth scroll for navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const target = document.querySelector(link.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    // Mobile menu toggle
    const menuToggle = document.getElementById('menuToggle');
    if (menuToggle) {
        menuToggle.addEventListener('click', () => {
            const navMenu = document.querySelector('.nav-menu');
            navMenu.style.display = navMenu.style.display === 'flex' ? 'none' : 'flex';
        });
    }
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

        // Start prediction loop
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

    // Update button states
    modeBtns.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.mode === mode);
    });

    // Reset prediction display
    predictionResult.innerHTML = '<span class="result-label">Waiting for recognition...</span>';
    confidenceBars.innerHTML = '';

    // Reset word sequence buffer
    if (mode === 'word') {
        resetWordSequence();
    }

    console.log('Switched to mode:', mode);
}

/**
 * Start prediction loop
 */
function startPredictionLoop() {
    // Clear existing interval
    if (predictionInterval) {
        clearInterval(predictionInterval);
    }

    // Predict every 500ms for alphabet, 100ms for words (to build sequence)
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

    // Set canvas dimensions
    canvas.width = webcam.videoWidth;
    canvas.height = webcam.videoHeight;

    // Draw current frame to canvas
    const ctx = canvas.getContext('2d');
    ctx.drawImage(webcam, 0, 0);

    // Convert to base64
    const imageData = canvas.toDataURL('image/jpeg', 0.8);

    // Send to API
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

        // Display result
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
    // Main prediction
    predictionResult.innerHTML = `
        <div class="result-letter">${result.letter}</div>
        <div class="result-confidence">${(result.confidence * 100).toFixed(1)}% confidence</div>
    `;

    // Top predictions with confidence bars
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
            <div class="result-confidence">${(result.confidence * 100).toFixed(1)}% confidence</div>
        `;
    } else {
        predictionResult.innerHTML = `
            <span class="result-label">Building sequence...</span>
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
    const text = textInput.value.trim();

    if (!text) {
        showNotification('Please enter some text', 'info');
        return;
    }

    // Show loading
    signsOutput.innerHTML = '<div class="placeholder-text"><p>Loading signs...</p></div>';

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
            signsOutput.innerHTML = `<div class="placeholder-text"><p>Error: ${result.error}</p></div>`;
            return;
        }

        // Display signs
        displaySigns(result.signs);
    } catch (error) {
        console.error('Text to sign conversion failed:', error);
        signsOutput.innerHTML = '<div class="placeholder-text"><p>Conversion failed. Is the server running?</p></div>';
    }
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
            // Break down word into alphabet
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

    // Add click handlers
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
    // For now, just highlight it
    console.log('Selected letter:', letter);
    // Could implement a modal here for detailed view
}

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
    // Create notification element
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

    // Remove after 4 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}

// Add CSS animations
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

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    stopWebcam();
});

console.log('ISL Recognition Frontend - Ready! 🚀');
