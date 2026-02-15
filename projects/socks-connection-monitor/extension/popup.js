/**
 * Extension popup logic
 */

// Format timestamp
function formatTime(timestamp) {
    if (!timestamp) return 'never';
    const date = new Date(timestamp * 1000);
    return date.toLocaleTimeString();
}

// Update UI with status data
function displayStatus(status) {
    if (!status) {
        showMessage('Unable to connect to backend', 'error');
        return;
    }

    // VPN status
    const vpnDetected = status.vpn?.detected;
    const vpnElement = document.getElementById('vpn-status');
    if (vpnDetected) {
        vpnElement.textContent = `● ${status.vpn.name}`;
        vpnElement.className = 'status-connected';
        vpnElement.style.color = status.vpn.color || '#008000';
    } else {
        vpnElement.textContent = '● Not Connected';
        vpnElement.className = 'status-disconnected';
    }

    // Proxy status
    const proxyAvailable = status.proxy?.available;
    const proxyElement = document.getElementById('proxy-status');
    if (proxyAvailable) {
        proxyElement.textContent = '● Connected';
        proxyElement.className = 'status-connected';
    } else {
        proxyElement.textContent = '● Disconnected';
        proxyElement.className = 'status-disconnected';
    }

    // Proxy address
    document.getElementById('proxy-address').textContent = 
        `${status.proxy?.host}:${status.proxy?.port}`;

    // Connection type
    document.getElementById('connection-type').textContent = 
        status.connection_type || 'Direct';

    // Direct IP
    const directIP = status.ip?.direct;
    if (directIP?.success) {
        document.getElementById('ip-direct').textContent = directIP.ip;
        document.getElementById('ip-direct-latency').textContent = 
            `(${directIP.latency}ms)`;
    } else {
        document.getElementById('ip-direct').textContent = 'Error';
        document.getElementById('ip-direct-latency').textContent = '';
    }

    // Proxy IP
    const proxyIP = status.ip?.via_proxy;
    if (proxyIP && proxyIP.success) {
        document.getElementById('ip-proxy').textContent = proxyIP.ip;
        document.getElementById('ip-proxy-latency').textContent = 
            `(${proxyIP.latency}ms)`;
    } else if (proxyAvailable) {
        document.getElementById('ip-proxy').textContent = 'N/A';
        document.getElementById('ip-proxy-latency').textContent = '';
    } else {
        document.getElementById('ip-proxy').textContent = '—';
        document.getElementById('ip-proxy-latency').textContent = '';
    }

    // DNS servers
    const dnsServers = status.dns || [];
    const dnsElement = document.getElementById('dns-servers');
    if (dnsServers.length > 0) {
        dnsElement.innerHTML = dnsServers
            .map(dns => `<div>${dns}</div>`)
            .join('');
    } else {
        dnsElement.textContent = 'No DNS servers found';
    }

    // Last update
    document.getElementById('last-update').textContent = 
        `Last update: ${formatTime(status.timestamp)}`;
}

// Load config into form
function loadConfig() {
    chrome.runtime.sendMessage({ type: 'GET_CONFIG' }, (response) => {
        if (response && response.config) {
            const config = response.config;
            document.getElementById('socks-host').value = config.socks_host || 'localhost';
            document.getElementById('socks-port').value = config.socks_port || 1080;
            document.getElementById('check-interval').value = config.check_interval || 5;
        }
    });
}

// Refresh status
function refreshStatus() {
    chrome.runtime.sendMessage({ type: 'MANUAL_REFRESH' }, () => {
        // Get latest status from background
        chrome.runtime.sendMessage({ type: 'GET_STATUS' }, (response) => {
            if (response && response.data) {
                displayStatus(response.data);
            }
        });
    });
}

// Save config
function saveConfig() {
    const config = {
        socks_host: document.getElementById('socks-host').value,
        socks_port: parseInt(document.getElementById('socks-port').value),
        check_interval: parseInt(document.getElementById('check-interval').value),
        timeout: 5
    };

    chrome.runtime.sendMessage(
        { type: 'UPDATE_CONFIG', config: config },
        (response) => {
            if (response && response.success) {
                showMessage('Settings saved successfully', 'success');
                setTimeout(() => refreshStatus(), 500);
            }
        }
    );
}

// Show message
function showMessage(text, type) {
    const msgEl = document.getElementById('message');
    msgEl.textContent = text;
    msgEl.className = `message ${type}`;
    setTimeout(() => {
        msgEl.className = 'message';
    }, 3000);
}

// Event listeners
document.getElementById('refresh-btn').addEventListener('click', refreshStatus);
document.getElementById('save-btn').addEventListener('click', saveConfig);
document.getElementById('cancel-btn').addEventListener('click', () => {
    loadConfig();
});

document.getElementById('settings-btn').addEventListener('click', () => {
    chrome.runtime.openOptionsPage();
});

document.getElementById('minimize').addEventListener('click', () => {
    window.close();
});

document.getElementById('close').addEventListener('click', () => {
    window.close();
});

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    loadConfig();

    // Get initial status
    chrome.runtime.sendMessage({ type: 'GET_STATUS' }, (response) => {
        if (response && response.data) {
            displayStatus(response.data);
        } else {
            showMessage('Loading connection status...', 'error');
        }
    });

    // Listen for updates from background
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
        if (request.type === 'STATUS_UPDATE') {
            displayStatus(request.data);
        }
    });
});
