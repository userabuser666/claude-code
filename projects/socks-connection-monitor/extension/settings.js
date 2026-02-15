/**
 * Settings Page JavaScript
 */

const API_BASE = 'http://localhost:5000/api';

// State
let currentTheme = {
    colors: {
        direct: '#666666',
        socks: '#00AA00',
        expressvpn: '#FF6B35',
        nordvpn: '#4169E1',
        other_vpn: '#9932CC',
        disconnected: '#DD0000'
    },
    opacity: 100,
    fontSize: 13,
    popupSize: 'normal'
};

// Tab switching
document.querySelectorAll('.tab-button').forEach(btn => {
    btn.addEventListener('click', (e) => {
        const tabName = e.target.dataset.tab;
        
        // Hide all tabs
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelectorAll('.tab-button').forEach(b => {
            b.classList.remove('active');
        });
        
        // Show selected tab
        document.getElementById(`${tabName}-tab`).classList.add('active');
        e.target.classList.add('active');
    });
});

// Close button
document.getElementById('close').addEventListener('click', () => {
    window.close();
});

// ====================
// APPEARANCE TAB
// ====================

const opacitySlider = document.getElementById('opacity-slider');
const opacityValue = document.getElementById('opacity-value');

opacitySlider.addEventListener('input', (e) => {
    const value = e.target.value;
    opacityValue.textContent = value + '%';
    document.querySelector('.win7-window').style.opacity = value / 100;
    currentTheme.opacity = value;
});

const fontSizeSelect = document.getElementById('font-size');
fontSizeSelect.addEventListener('change', (e) => {
    const fontSize = e.target.value;
    document.documentElement.style.fontSize = fontSize + 'px';
    currentTheme.fontSize = fontSize;
});

const popupSizeSelect = document.getElementById('popup-size');
popupSizeSelect.addEventListener('change', (e) => {
    const sizes = {
        'compact': 400,
        'normal': 450,
        'expanded': 550,
        'large': 650
    };
    const width = sizes[e.target.value];
    document.body.style.width = width + 'px';
    currentTheme.popupSize = e.target.value;
});

const showTooltips = document.getElementById('show-tooltips');
const animationsEnabled = document.getElementById('animations-enabled');

showTooltips.addEventListener('change', (e) => {
    currentTheme.showTooltips = e.target.checked;
});

animationsEnabled.addEventListener('change', (e) => {
    if (!e.target.checked) {
        document.documentElement.style.setProperty('--animation-duration', '0ms');
    } else {
        document.documentElement.style.setProperty('--animation-duration', '150ms');
    }
    currentTheme.animationsEnabled = e.target.checked;
});

// ====================
// PROXIES TAB
// ====================

const importProxiesBtn = document.getElementById('import-proxies-btn');
const importSection = document.getElementById('import-section');
const addSingleProxyBtn = document.getElementById('add-single-proxy-btn');
const singleProxyForm = document.getElementById('single-proxy-form');

importProxiesBtn.addEventListener('click', () => {
    importSection.style.display = importSection.style.display === 'none' ? 'block' : 'none';
});

addSingleProxyBtn.addEventListener('click', () => {
    singleProxyForm.style.display = singleProxyForm.style.display === 'none' ? 'block' : 'none';
});

let importFormat = 'iproxyal';
document.querySelectorAll('.import-format-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        document.querySelectorAll('.import-format-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        importFormat = e.target.dataset.format;
    });
});

// Import proxies
document.getElementById('import-confirm-btn').addEventListener('click', async () => {
    const content = document.getElementById('proxy-paste-area').value;
    if (!content) {
        showImportMessage('Please paste proxy data', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/proxies/import`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                type: importFormat,
                content: content
            })
        });

        const result = await response.json();
        if (result.success) {
            showImportMessage(`✓ Imported ${result.imported} proxy/proxies`, 'success');
            document.getElementById('proxy-paste-area').value = '';
            loadProxyList();
            setTimeout(() => {
                importSection.style.display = 'none';
            }, 1500);
        } else {
            showImportMessage(`Error: ${result.error}`, 'error');
        }
    } catch (error) {
        showImportMessage(`Error: ${error.message}`, 'error');
    }
});

document.getElementById('import-cancel-btn').addEventListener('click', () => {
    importSection.style.display = 'none';
    document.getElementById('proxy-paste-area').value = '';
});

// Add single proxy
document.getElementById('add-proxy-confirm-btn').addEventListener('click', async () => {
    const host = document.getElementById('proxy-host').value;
    const port = document.getElementById('proxy-port').value;
    const name = document.getElementById('proxy-name').value;
    const username = document.getElementById('proxy-username').value;
    const password = document.getElementById('proxy-password').value;

    if (!host || !port) {
        alert('Host and port are required');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/proxies/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                host, port: parseInt(port), name, username, password
            })
        });

        if (response.ok) {
            showImportMessage('✓ Proxy added successfully', 'success');
            document.getElementById('proxy-host').value = '';
            document.getElementById('proxy-port').value = '';
            document.getElementById('proxy-name').value = '';
            document.getElementById('proxy-username').value = '';
            document.getElementById('proxy-password').value = '';
            loadProxyList();
            setTimeout(() => {
                singleProxyForm.style.display = 'none';
            }, 1500);
        }
    } catch (error) {
        showImportMessage(`Error: ${error.message}`, 'error');
    }
});

document.getElementById('add-proxy-cancel-btn').addEventListener('click', () => {
    singleProxyForm.style.display = 'none';
});

// Export proxies
document.getElementById('export-proxies-btn').addEventListener('click', async () => {
    try {
        const response = await fetch(`${API_BASE}/proxies/export?format=iproxyal`);
        const text = await response.text();
        
        // Copy to clipboard
        navigator.clipboard.writeText(text).then(() => {
            showImportMessage('✓ Exported proxies copied to clipboard', 'success');
        });
    } catch (error) {
        showImportMessage(`Error: ${error.message}`, 'error');
    }
});

// Load and display proxy list
async function loadProxyList() {
    try {
        const response = await fetch(`${API_BASE}/proxies`);
        const data = await response.json();
        const proxies = data.proxies;
        const activeId = data.active_proxy_id;

        const container = document.getElementById('proxies-container');
        if (proxies.length === 0) {
            container.innerHTML = '<div class="proxy-item-empty">No proxies configured. Click "Import" to add proxies.</div>';
            return;
        }

        container.innerHTML = proxies.map(proxy => `
            <div class="proxy-item ${proxy.id === activeId ? 'active' : ''}">
                <div class="proxy-item-name">${proxy.name}</div>
                <div class="proxy-item-address">${proxy.host}:${proxy.port}</div>
                <div class="proxy-item-status">
                    <span class="proxy-status-${proxy.active ? 'ok' : 'error'}">
                        ${proxy.active ? '● Active' : '○ Inactive'}
                    </span>
                </div>
                <div class="proxy-actions">
                    <button class="proxy-action-btn" onclick="activateProxy('${proxy.id}')">Use</button>
                    <button class="proxy-action-btn" onclick="testProxyConnection('${proxy.id}')">Test</button>
                    <button class="proxy-action-btn" onclick="removeProxy('${proxy.id}')">Remove</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading proxies:', error);
    }
}

async function activateProxy(proxyId) {
    try {
        const response = await fetch(`${API_BASE}/proxies/activate/${proxyId}`, { method: 'POST' });
        if (response.ok) {
            loadProxyList();
            showImportMessage('✓ Proxy activated', 'success');
        }
    } catch (error) {
        showImportMessage(`Error: ${error.message}`, 'error');
    }
}

async function testProxyConnection(proxyId) {
    try {
        const response = await fetch(`${API_BASE}/proxies/test/${proxyId}`, { method: 'POST' });
        const result = await response.json();
        if (result.reachable) {
            showImportMessage('✓ Proxy is reachable', 'success');
        } else {
            showImportMessage('✗ Proxy is not reachable', 'error');
        }
    } catch (error) {
        showImportMessage(`Error: ${error.message}`, 'error');
    }
}

async function removeProxy(proxyId) {
    if (!confirm('Remove this proxy?')) return;
    
    try {
        const response = await fetch(`${API_BASE}/proxies/remove/${proxyId}`, { method: 'DELETE' });
        if (response.ok) {
            loadProxyList();
            showImportMessage('✓ Proxy removed', 'success');
        }
    } catch (error) {
        showImportMessage(`Error: ${error.message}`, 'error');
    }
}

function showImportMessage(text, type) {
    const msg = document.getElementById('import-message');
    msg.textContent = text;
    msg.className = `message ${type}`;
    setTimeout(() => {
        msg.className = 'message';
    }, 3000);
}

// ====================
// COLOR THEME TAB
// ====================

const colorInputs = {
    'direct': document.getElementById('color-direct'),
    'socks': document.getElementById('color-socks'),
    'expressvpn': document.getElementById('color-expressvpn'),
    'nordvpn': document.getElementById('color-nordvpn'),
    'other_vpn': document.getElementById('color-other-vpn'),
    'disconnected': document.getElementById('color-disconnected')
};

// Set initial color values
for (const [key, input] of Object.entries(colorInputs)) {
    input.value = currentTheme.colors[key];
    input.addEventListener('change', (e) => {
        currentTheme.colors[key] = e.target.value;
        document.getElementById(`color-${key}-value`).textContent = e.target.value;
    });
}

document.getElementById('reset-colors-btn').addEventListener('click', () => {
    const defaults = {
        direct: '#666666',
        socks: '#00AA00',
        expressvpn: '#FF6B35',
        nordvpn: '#4169E1',
        other_vpn: '#9932CC',
        disconnected: '#DD0000'
    };
    
    for (const [key, value] of Object.entries(defaults)) {
        colorInputs[key].value = value;
        currentTheme.colors[key] = value;
        document.getElementById(`color-${key}-value`).textContent = value;
    }
    showSettingsMessage('✓ Colors reset to default', 'success');
});

// ====================
// GENERAL TAB
// ====================

const checkIntervalSlider = document.getElementById('check-interval-slider');
const checkIntervalValue = document.getElementById('check-interval-value');

checkIntervalSlider.addEventListener('input', (e) => {
    const value = e.target.value;
    checkIntervalValue.textContent = value + 's';
});

const autoRefresh = document.getElementById('auto-refresh');
const showNotifications = document.getElementById('show-notifications');
const minimizeToTray = document.getElementById('minimize-to-tray');

// Save settings
document.getElementById('save-all-btn').addEventListener('click', async () => {
    const settings = {
        theme: currentTheme,
        checkInterval: parseInt(checkIntervalSlider.value),
        timeout: parseInt(document.getElementById('timeout-input').value),
        autoRefresh: autoRefresh.checked,
        showNotifications: showNotifications.checked,
        minimizeToTray: minimizeToTray.checked
    };

    try {
        chrome.storage.sync.set({ appSettings: settings }, () => {
            showSettingsMessage('✓ All settings saved successfully', 'success');
        });
    } catch (error) {
        showSettingsMessage(`Error: ${error.message}`, 'error');
    }
});

document.getElementById('reset-all-btn').addEventListener('click', () => {
    if (!confirm('Reset all settings to default?')) return;
    
    opacitySlider.value = 100;
    opacityValue.textContent = '100%';
    fontSizeSelect.value = 13;
    popupSizeSelect.value = 'normal';
    checkIntervalSlider.value = 5;
    checkIntervalValue.textContent = '5s';
    document.getElementById('timeout-input').value = 5;
    autoRefresh.checked = true;
    showNotifications.checked = true;
    minimizeToTray.checked = true;
    
    showSettingsMessage('✓ Settings reset to default', 'success');
});

function showSettingsMessage(text, type) {
    const msg = document.getElementById('settings-message');
    msg.textContent = text;
    msg.className = `message ${type}`;
    setTimeout(() => {
        msg.className = 'message';
    }, 3000);
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadProxyList();
});
