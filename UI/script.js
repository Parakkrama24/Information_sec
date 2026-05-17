// API Base URL
const API_URL = 'http://localhost:5000/api';

// Navigation
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const targetId = link.getAttribute('href').substring(1);

        // Update active nav link
        document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
        link.classList.add('active');

        // Show target page
        document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));
        document.getElementById(targetId).classList.add('active');
    });
});

// Load folder structure
async function loadFolderStructure() {
    try {
        const response = await fetch(`${API_URL}/folder-structure`);
        const data = await response.json();

        const treeContainer = document.getElementById('folder-tree');
        treeContainer.innerHTML = formatFolderTree(data.structure);
    } catch (error) {
        console.error('Error loading folder structure:', error);
        document.getElementById('folder-tree').innerHTML =
            '<div class="log-placeholder">Error loading folder structure. Make sure the backend server is running.</div>';
    }
}

function formatFolderTree(structure, indent = 0) {
    let html = '';
    const indentStr = '  '.repeat(indent);

    for (const [key, value] of Object.entries(structure)) {
        if (typeof value === 'object' && value !== null) {
            html += `<div class="folder">${indentStr}📁 ${key}/</div>`;
            html += formatFolderTree(value, indent + 1);
        } else {
            const icon = getFileIcon(key);
            html += `<div class="file">${indentStr}${icon} ${key}</div>`;
        }
    }

    return html;
}

function getFileIcon(filename) {
    if (filename.endsWith('.py')) return '🐍';
    if (filename.endsWith('.pem')) return '🔐';
    if (filename.endsWith('.txt')) return '📝';
    if (filename.endsWith('.md')) return '📄';
    if (filename.endsWith('.html')) return '🌐';
    if (filename.endsWith('.css')) return '🎨';
    if (filename.endsWith('.js')) return '⚡';
    return '📄';
}

// Test Controls
document.getElementById('run-full-test-btn').addEventListener('click', async () => {
    try {
        clearAllLogs();
        addLog('server-logs', '[INFO] Running full system test...', 'log-info');
        addLog('vehicle-logs', '[INFO] Running full system test...', 'log-info');

        const response = await fetch(`${API_URL}/run-full-test`, { method: 'POST' });
        const data = await response.json();

        if (data.success) {
            // Display server logs
            if (data.server_logs) {
                data.server_logs.forEach(log => {
                    const logType = log.includes('[SUCCESS]') ? 'log-success' :
                                   log.includes('[ERROR]') ? 'log-error' : 'log-info';
                    addLog('server-logs', log, logType);
                });
            }

            // Display vehicle logs
            if (data.vehicle_logs) {
                data.vehicle_logs.forEach(log => {
                    const logType = log.includes('[SUCCESS]') ? 'log-success' :
                                   log.includes('[ERROR]') ? 'log-error' : 'log-info';
                    addLog('vehicle-logs', log, logType);
                });
            }

            // Display telemetry if available
            if (data.telemetry) {
                displayTelemetry(data.telemetry);
            }
        } else {
            addLog('server-logs', `[ERROR] ${data.message}`, 'log-error');
        }
    } catch (error) {
        addLog('server-logs', `[ERROR] Connection error: ${error.message}`, 'log-error');
    }
});

document.getElementById('clear-logs-btn').addEventListener('click', () => {
    clearAllLogs();
});

function addLog(containerId, message, logClass = '') {
    const container = document.getElementById(containerId);

    // Remove placeholder if exists
    const placeholder = container.querySelector('.log-placeholder');
    if (placeholder) {
        placeholder.remove();
    }

    const logEntry = document.createElement('div');
    logEntry.className = `log-entry ${logClass}`;
    logEntry.textContent = message;

    container.appendChild(logEntry);
    container.scrollTop = container.scrollHeight;
}

function clearAllLogs() {
    ['server-logs', 'vehicle-logs'].forEach(id => {
        const container = document.getElementById(id);
        container.innerHTML = '<div class="log-placeholder">Logs cleared.</div>';
    });

    const telemetryContainer = document.getElementById('telemetry-data');
    telemetryContainer.innerHTML = '<div class="log-placeholder">No telemetry received yet.</div>';
}

function displayTelemetry(data) {
    const container = document.getElementById('telemetry-data');
    container.innerHTML = `<pre class="telemetry-data">${JSON.stringify(data, null, 4)}</pre>`;
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadFolderStructure();
});

// Check backend connection
async function checkBackendConnection() {
    try {
        const response = await fetch(`${API_URL}/health`);
        if (!response.ok) {
            console.warn('Backend server not responding');
        }
    } catch (error) {
        console.warn('Backend server not available. Please start the backend server.');
    }
}

checkBackendConnection();

// ==================== Protocol Diagram Animation ====================

const stepExplanations = [
    {
        step: 0,
        text: "Click 'Start Animation' to begin the protocol demonstration. This shows how a vehicle securely authenticates and transmits telemetry to the edge server."
    },
    {
        step: 1,
        text: "<strong>Step 1: TCP Connection</strong><br>The vehicle establishes a TCP socket connection to the Edge Server on port 65432. This creates a bidirectional communication channel."
    },
    {
        step: 2,
        text: "<strong>Step 2: Challenge Sent</strong><br>The Edge Server generates a random 32-byte cryptographic nonce (challenge) and sends it to the vehicle. This nonce prevents replay attacks."
    },
    {
        step: 3,
        text: "<strong>Step 3: Sign Challenge</strong><br>The vehicle signs the challenge using its RSA-2048 private key with PSS padding and SHA-256. This proves the vehicle possesses the authentic private key."
    },
    {
        step: 4,
        text: "<strong>Step 4: Send Signature</strong><br>The vehicle transmits the digital signature (256 bytes) back to the server. This signature can only be produced by someone with access to the vehicle's private key."
    },
    {
        step: 5,
        text: "<strong>Step 5: Verify Signature</strong><br>The Edge Server verifies the signature using the vehicle's RSA public key. If verification succeeds, the vehicle is authenticated. This confirms the vehicle's identity."
    },
    {
        step: 6,
        text: "<strong>Step 6: Generate AES Session Key</strong><br>The vehicle generates a random 256-bit AES key for this session. It then encrypts this key using the server's RSA public key with OAEP padding to ensure only the server can decrypt it."
    },
    {
        step: 7,
        text: "<strong>Step 7: Send Encrypted Session Key</strong><br>The encrypted AES session key (256 bytes) is transmitted to the server. Even if intercepted, only the server can decrypt it using its private key."
    },
    {
        step: 8,
        text: "<strong>Step 8: Decrypt Session Key</strong><br>The Edge Server decrypts the session key using its RSA-2048 private key. Both parties now share a secret AES key that no one else knows."
    },
    {
        step: 9,
        text: "<strong>Step 9: Encrypt Telemetry</strong><br>The vehicle encrypts its telemetry data (position, velocity, QoS, privacy demand) using AES-256-GCM and signs it with RSA for non-repudiation."
    },
    {
        step: 10,
        text: "<strong>Step 10: Secure Data Transfer</strong><br>The encrypted and signed telemetry is transmitted. The server decrypts with the session key and verifies the signature. <strong style='color: #10b981;'>✓ Communication Complete!</strong>"
    }
];

let currentStep = 0;
let animationInterval = null;
let isAnimating = false;

// Protocol Diagram Controls
if (document.getElementById('start-animation-btn')) {
    document.getElementById('start-animation-btn').addEventListener('click', startAnimation);
    document.getElementById('reset-animation-btn').addEventListener('click', resetAnimation);
    document.getElementById('step-next-btn').addEventListener('click', nextStep);
}

function startAnimation() {
    if (isAnimating) return;

    isAnimating = true;
    resetAnimation();

    document.getElementById('start-animation-btn').disabled = true;
    document.getElementById('step-next-btn').disabled = true;

    animationInterval = setInterval(() => {
        if (currentStep < 10) {
            currentStep++;
            showStep(currentStep);
        } else {
            stopAnimation();
        }
    }, 2000); // 2 seconds per step
}

function stopAnimation() {
    if (animationInterval) {
        clearInterval(animationInterval);
        animationInterval = null;
    }
    isAnimating = false;
    document.getElementById('start-animation-btn').disabled = false;
    document.getElementById('step-next-btn').disabled = false;
}

function resetAnimation() {
    stopAnimation();
    currentStep = 0;

    // Hide all steps
    for (let i = 1; i <= 10; i++) {
        const step = document.getElementById(`step${i}`);
        if (step) {
            step.setAttribute('opacity', '0');
        }
    }

    // Reset explanation
    updateExplanation(0);
}

function nextStep() {
    if (currentStep < 10) {
        currentStep++;
        showStep(currentStep);
    }
}

function showStep(stepNumber) {
    const stepElement = document.getElementById(`step${stepNumber}`);
    if (stepElement) {
        stepElement.setAttribute('opacity', '1');
        stepElement.classList.add('step-active');
    }

    updateExplanation(stepNumber);
}

function updateExplanation(stepNumber) {
    const explanation = stepExplanations.find(e => e.step === stepNumber);
    if (explanation) {
        document.getElementById('step-text').innerHTML = explanation.text;
    }
}
