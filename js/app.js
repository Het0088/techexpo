const API_BASE_URL = 'http://localhost:5000/api';

let webcamStream = null;
let isWebcamActive = false;
let currentMode = 'alphabet';
let predictionInterval = null;

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

document.addEventListener('DOMContentLoaded', () => {
    initEventListeners();
    generateAlphabetGrid();
    checkAPIHealth();
});

function initEventListeners() {
    startWebcamBtn.addEventListener('click', startWebcam);

    modeBtns.forEach(btn => {
        btn.addEventListener('click', () => switchMode(btn.dataset.mode));
    });

    convertBtn.addEventListener('click', convertTextToSign);
    textInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') convertTextToSign();
    });

    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href').slice(1);
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    const menuToggle = document.querySelector('.menu-toggle');
    const navMenu = document.querySelector('.nav-menu');
    if (menuToggle && navMenu) {
        menuToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
        });
    }
}

async function checkAPIHealth() {
    try {
        const response = await fetch('http://localhost:5000/health');
        const health = await response.json();
        console.log('API Health:', health);
    } catch (error) {
        console.error('API not responding:', error);
        showNotification('Backend server not running. Start with: python app.py', 'error');
    }
}

async function startWebcam() {
    try {
        webcamStream = await navigator.mediaDevices.getUserMedia({ 
            video: { width: 640, height: 480 } 
        });
        
        webcam.srcObject = webcamStream;
        videoOverlay.style.display = 'none';
        isWebcamActive = true;
        
        startWebcamBtn.textContent = 'Stop Camera';
        startWebcamBtn.onclick = stopWebcam;
        
        startPredictionLoop();
        showNotification('Camera started', 'success');
    } catch (error) {
        console.error('Camera access failed:', error);
        showNotification('Camera access denied. Please allow camera permissions.', 'error');
    }
}

function stopWebcam() {
    if (webcamStream) {
        webcamStream.getTracks().forEach(track => track.stop());
        webcamStream = null;
        isWebcamActive = false;
    }
    
    if (predictionInterval) {
        clearInterval(predictionInterval);
        predictionInterval = null;
    }
    
    videoOverlay.style.display = 'flex';
    startWebcamBtn.textContent = 'Start Camera';
    startWebcamBtn.onclick = startWebcam;
    
    predictionResult.innerHTML = '<div class="result-label">Camera stopped</div>';
    confidenceBars.innerHTML = '';
    
    showNotification('Camera stopped', 'info');
}

function switchMode(mode) {
    currentMode = mode;
    
    modeBtns.forEach(btn => {
        if (btn.dataset.mode === mode) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    
    predictionResult.innerHTML = '<div class="result-label">Waiting for prediction...</div>';
    confidenceBars.innerHTML = '';
    
    if (mode === 'word') {
        resetWordSequence();
    }
    
    if (isWebcamActive) {
        startPredictionLoop();
    }
}

function startPredictionLoop() {
    if (predictionInterval) clearInterval(predictionInterval);
    
    const interval = currentMode === 'alphabet' ? 500 : 100;
    
    predictionInterval = setInterval(() => {
        if (isWebcamActive) {
            captureAndPredict();
        }
    }, interval);
}

async function captureAndPredict() {
    const context = canvas.getContext('2d');
    canvas.width = webcam.videoWidth;
    canvas.height = webcam.videoHeight;
    context.drawImage(webcam, 0, 0, canvas.width, canvas.height);
    
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

function displayAlphabetPrediction(result) {
    predictionResult.innerHTML = `
        <div class="result-letter">${result.letter}</div>
        <div class="result-confidence">${(result.confidence * 100).toFixed(1)}% confidence</div>
    `;

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

function displayWordPrediction(result) {
    if (result.ready) {
        predictionResult.innerHTML = `
            <div class="result-letter">${result.word}</div>
            <div class="result-confidence">${(result.confidence * 100).toFixed(1)}% confidence</div>
        `;
        confidenceBars.innerHTML = '';
    } else {
        const progress = result.progress || 0;
        predictionResult.innerHTML = `
            <div class="result-label">${result.message || 'Capturing gesture...'}</div>
            <div class="result-confidence">${progress}%</div>
        `;
    }
}

async function resetWordSequence() {
    try {
        await fetch(API_BASE_URL + '/reset', { method: 'POST' });
    } catch (error) {
        console.error('Failed to reset sequence:', error);
    }
}

async function convertTextToSign() {
    const text = textInput.value.trim();
    
    if (!text) {
        showNotification('Please enter some text', 'info');
        return;
    }

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

        displaySigns(result.signs);
    } catch (error) {
        console.error('Text to sign conversion failed:', error);
        signsOutput.innerHTML = '<div class="placeholder-text"><p>Conversion failed. Is the server running?</p></div>';
    }
}

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

function generateAlphabetGrid() {
    const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');
    
    alphabetGrid.innerHTML = letters.map(letter => `
        <div class="alphabet-card">
            <div class="alphabet-letter">${letter}</div>
            <div class="alphabet-image"></div>
        </div>
    `).join('');
}

function showNotification(message, type = 'info') {
    let notification = document.getElementById('notification');
    
    if (!notification) {
        notification = document.createElement('div');
        notification.id = 'notification';
        document.body.appendChild(notification);
    }
    
    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.style.display = 'block';
    
    setTimeout(() => {
        notification.style.display = 'none';
    }, 3000);
}
