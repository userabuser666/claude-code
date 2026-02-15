# SOCKS Connection Monitor

A browser extension + Python backend system that monitors your SOCKS5 proxy connection status in real-time without distracting you from your work.

## Features

- **Real-time Connection Monitoring**: Checks SOCKS proxy status every 5-6 seconds
- **Color-coded Status**: Green (connected), Red (disconnected), Yellow (warning)
- **Dual IP Display**: Shows both direct IP and IP through proxy
- **DNS Information**: Displays current DNS servers
- **Windows 7 Aesthetic**: Faithful recreation of classic Windows 7 UI
- **Minimal & Non-intrusive**: Compact popup that doesn't distract from browsing
- **Configurable Settings**: Adjust proxy host/port and check intervals

## Project Structure

```
socks-connection-monitor/
├── backend/
│   ├── app.py              # Flask API server
│   └── requirements.txt     # Python dependencies
└── extension/
    ├── manifest.json       # Extension manifest
    ├── background.js       # Background service worker
    ├── popup.html          # Popup UI
    ├── popup.js            # Popup logic
    └── styles.css          # Windows 7 styled CSS
```

## Setup & Installation

### Backend (Python)

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Run the Flask server:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

### Browser Extension

1. Open your browser's extension management page:
   - **Chrome/Edge**: `chrome://extensions` or `edge://extensions`
   - **Firefox**: `about:addons`

2. Enable "Developer Mode" (top right)

3. Click "Load unpacked" and select the `extension/` folder

4. The extension will appear in your toolbar with a status badge

## API Endpoints

### `GET /api/status`
Returns complete connection status including:
- SOCKS proxy availability
- Public IP (direct and via proxy)
- DNS servers
- Network latency

**Response:**
```json
{
  "proxy": {
    "available": true,
    "host": "localhost",
    "port": 1080,
    "status": "Connected"
  },
  "ip": {
    "direct": {
      "ip": "203.0.113.45",
      "latency": 45.23,
      "service": "api.ipify.org"
    },
    "via_proxy": {
      "ip": "198.51.100.89",
      "latency": 156.78,
      "service": "api.ipify.org"
    }
  },
  "dns": ["8.8.8.8", "8.8.4.4"],
  "connection_type": "Proxy"
}
```

### `GET /api/ping`
Health check endpoint

### `GET /api/config`
Get current backend configuration

### `POST /api/config`
Update backend configuration

**Request:**
```json
{
  "socks_host": "localhost",
  "socks_port": 1080,
  "check_interval": 5,
  "timeout": 5
}
```

## Usage

1. Click the extension icon in your toolbar
2. View your current connection status:
   - SOCKS proxy status (connected/disconnected)
   - Your public IPs
   - DNS servers
   - Network latency

3. Configure settings:
   - Set your SOCKS server host/port
   - Adjust polling interval (default: 5 seconds)

4. Monitor your connection in the background:
   - Status badge shows quick connection state
   - Popup updates in real-time
   - No performance impact on browser

## Configuration

### Backend Settings (`backend/app.py`)

Modify the `CONFIG` dict to change defaults:

```python
CONFIG = {
    'socks_host': 'localhost',      # SOCKS server address
    'socks_port': 1080,             # SOCKS server port
    'check_interval': 5,            # Check interval in seconds
    'timeout': 5,                   # Connection timeout
}
```

### Polling Interval

Adjust in extension popup or modify `POLL_INTERVAL` in `background.js`:

```javascript
const POLL_INTERVAL = 5000; // milliseconds
```

## Windows 7 Aesthetic Details

The UI recreates classic Windows 7 design with:
- Authentic gradient titlebar (Windows 7 Blue)
- Classic beveled borders and shadows
- 3D button effects
- System font (Segoe UI)
- Period-accurate color scheme
- Proper scrollbar styling

## System Impact

- **Desktop**: Negligible (1-2% CPU during polls, minimal memory)
- **Mobile**: Not recommended (battery drain from constant polling)

## Troubleshooting

### Backend not responding
- Ensure Flask is running: `python app.py`
- Check if SOCKS server is accessible
- Verify localhost:5000 is accessible from browser

### Extension shows "Disconnected"
- Check SOCKS proxy is running on configured host/port
- Verify firewall isn't blocking the connection
- Check backend logs for errors

### High latency readings
- Network condition dependent
- May indicate slow SOCKS server or high network congestion
- Adjust timeout settings if needed

## License

MIT
