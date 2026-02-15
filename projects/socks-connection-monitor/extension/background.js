/**
 * Extension background service worker
 * Fetches connection status and manages badge updates
 */

const API_BASE = 'http://localhost:5000/api';
const POLL_INTERVAL = 5000; // 5 seconds

let pollTimer = null;
let lastStatus = null;

// Initialize on installation
chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.set({
    config: {
      socks_host: 'localhost',
      socks_port: 1080,
      check_interval: 5,
      timeout: 5
    }
  });
  startPolling();
});

async function fetchStatus() {
  try {
    const response = await fetch(`${API_BASE}/status`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    });

    if (!response.ok) throw new Error(`API error: ${response.status}`);

    const data = await response.json();
    lastStatus = data;

    // Update badge
    updateBadge(data);

    // Broadcast to all open popups
    chrome.runtime.sendMessage({
      type: 'STATUS_UPDATE',
      data: data
    }).catch(() => {
      // No receivers, that's fine
    });

    return data;
  } catch (error) {
    console.error('Status fetch error:', error);
    updateBadge(null);
    return null;
  }
}

function updateBadge(status) {
  if (!status) {
    chrome.action.setBadgeBackgroundColor({ color: '#666' });
    chrome.action.setBadgeText({ text: '?' });
    return;
  }

  // Use status color from backend (includes VPN color)
  const color = status.status_color || '#666';
  const isVPN = status.vpn?.detected;
  const isConnected = status.proxy?.available;

  chrome.action.setBadgeBackgroundColor({ color: color });
  
  // Badge text shows connection type
  if (isVPN) {
    chrome.action.setBadgeText({ text: 'VPN' });
  } else if (isConnected) {
    chrome.action.setBadgeText({ text: '✓' });
  } else {
    chrome.action.setBadgeText({ text: '✗' });
  }
}

function startPolling() {
  // Initial fetch
  fetchStatus();

  // Set up polling
  if (pollTimer) clearInterval(pollTimer);

  pollTimer = setInterval(fetchStatus, POLL_INTERVAL);
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = null;
  }
}

// Listen for config changes from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === 'GET_STATUS') {
    sendResponse({ data: lastStatus });
  } else if (request.type === 'GET_CONFIG') {
    chrome.storage.local.get(['config'], (result) => {
      sendResponse({ config: result.config });
    });
    return true; // Keep channel open for async response
  } else if (request.type === 'UPDATE_CONFIG') {
    chrome.storage.local.set({ config: request.config }, () => {
      sendResponse({ success: true });
      // Refresh status after config update
      fetchStatus();
    });
    return true;
  } else if (request.type === 'MANUAL_REFRESH') {
    fetchStatus();
    sendResponse({ success: true });
  }
});

// Handle extension being disabled/enabled
chrome.runtime.onStartup.addListener(startPolling);
