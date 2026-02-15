# SOCKS Connection Monitor - Advanced Features Guide

## New Features Overview

This enhanced version includes comprehensive proxy management, appearance customization, and multi-proxy support.

## Appearance Customization

### Window Opacity/Transparency
- Adjust window transparency from 50% to 100%
- Perfect for keeping tabs visible while monitoring connection

### Font Size
- Small (12px) - Compact view
- Normal (13px) - Default, balanced
- Large (14px) - Easier to read
- Extra Large (15px) - Maximum visibility

### Popup Size
- **Compact** (400px) - Minimal footprint
- **Normal** (450px) - Default, recommended
- **Expanded** (550px) - More detail visibility
- **Large** (650px) - Maximum information display

### Visual Effects
- Toggle smooth animations
- Enable/disable hover tooltips
- All styled as classic Windows 7 interface

---

## Multi-Proxy Management

### Import Proxy Lists

The system supports importing proxies from multiple formats:

#### 1. **iProxyal Format** (Recommended for iProxyal service)

Simple paste-and-go format:
```
host1:port1
host2:port2
host3:port3:username:password
host4:port4:username:password
```

**From iProxyal:**
1. Go to your iProxyal dashboard
2. Copy the proxy list
3. Settings → SOCKS Proxies → Import
4. Select "iProxyal" format
5. Paste and click Import

#### 2. **JSON Format**

For programmatic imports:
```json
[
  {
    "host": "proxy1.example.com",
    "port": 1080,
    "name": "US Proxy 1",
    "username": "user",
    "password": "pass"
  },
  {
    "host": "proxy2.example.com",
    "port": 1080,
    "name": "EU Proxy 1"
  }
]
```

#### 3. **CSV Format**

Standard spreadsheet format:
```
host,port,name,username,password
proxy1.com,1080,US-1,user1,pass1
proxy2.com,1080,EU-1,user2,pass2
proxy3.com,1080,Generic,,
```

### Proxy Management Interface

Once imported, you can:

1. **View All Proxies**
   - Proxy name/address
   - Active status indicator
   - Last used timestamp

2. **Activate a Proxy**
   - Click "Use" button on any proxy
   - App immediately switches to that proxy
   - Status updates in real-time

3. **Test Connection**
   - Click "Test" to check if proxy is reachable
   - Shows success/failure status
   - Helpful for identifying dead proxies

4. **Remove Proxies**
   - Click "Remove" to delete a proxy
   - Confirms before deletion

5. **Export Proxies**
   - Export all proxies as iProxyal format
   - Automatically copied to clipboard
   - Easy backup and sharing

### Add Single Proxy

Don't want to import? Add one at a time:

1. Settings → SOCKS Proxies
2. Click "Add Single Proxy"
3. Enter:
   - **Host**: proxy server address
   - **Port**: proxy port number
   - **Name**: friendly name (optional)
   - **Username**: if auth required (optional)
   - **Password**: if auth required (optional)

---

## Color Theme Customization

Customize colors for each connection type:

### Available Connection Types

1. **Direct Connection** (default gray)
   - No proxy or VPN active
   - Direct internet connection

2. **SOCKS Proxy** (default green)
   - Active SOCKS5 proxy connection
   - Shows in status bar and badge

3. **ExpressVPN** (default orange)
   - ExpressVPN client connected
   - Distinct from SOCKS proxy

4. **NordVPN** (default royal blue)
   - NordVPN client connected
   - Brand-specific color

5. **Other VPN** (default dark orchid)
   - Unknown VPN detected
   - Fallback color for unrecognized VPNs

6. **Disconnected** (default red)
   - Connection failed or unavailable
   - Warning/error indicator

### How to Customize Colors

1. Settings → Color Theme
2. Click color box next to connection type
3. Choose your color
4. Color updates in real-time
5. Click "Reset to Default" to restore original colors

Colors are applied to:
- Status bar indicators
- Browser extension badge
- Text labels
- Connection type displays

---

## General Settings

### Connection Check Interval

- **Default**: 5 seconds
- **Range**: 1-60 seconds
- **Recommendation**:
  - 3-5 seconds for active monitoring
  - 10-15 seconds for battery conscious
  - 30+ seconds for background monitoring only

### Connection Timeout

- **Default**: 5 seconds
- **Range**: 1-30 seconds
- Time to wait before marking connection as failed

### Auto-refresh Status

- Enable/disable automatic status updates
- Useful if you want manual control

### Connection Change Notifications

- Pop-up notification when connection type changes
- Helps catch unexpected disconnections
- Can be disabled if distracting

### Minimize to System Tray

- Minimizes to taskbar tray instead of taskbar
- Windows only feature
- Reduces clutter

---

## API Integration

All proxy management is handled through REST endpoints:

### List Proxies
```
GET /api/proxies
Response: { proxies: [...], active_proxy_id: "..." }
```

### Add Proxy
```
POST /api/proxies/add
Body: { host, port, name, username, password }
```

### Activate Proxy
```
POST /api/proxies/activate/<proxy_id>
```

### Remove Proxy
```
DELETE /api/proxies/remove/<proxy_id>
```

### Import Proxies
```
POST /api/proxies/import
Body: { type: "iproxyal|json|csv", content: "..." }
```

### Export Proxies
```
GET /api/proxies/export?format=iproxyal|json
```

### Test Proxy
```
POST /api/proxies/test/<proxy_id>
Response: { proxy_id, reachable: true|false }
```

---

## Workflow Example: iProxyal Integration

### Step 1: Get Your Proxies from iProxyal

1. Log into iProxyal dashboard
2. Go to "My Proxies" or "Proxy List"
3. Select all proxies or desired region
4. Copy the proxy list (should be in `host:port:user:pass` format)

### Step 2: Import into Connection Monitor

1. Click extension icon → ⚙️ Settings
2. Go to "SOCKS Proxies" tab
3. Click "📥 Import"
4. Ensure "iProxyal" format is selected
5. Paste your copied proxy list
6. Click "✓ Import"
7. System shows "Imported X proxies"

### Step 3: Use Your Proxies

1. Settings → SOCKS Proxies
2. View your imported proxies in the list
3. Click "Use" on the proxy you want
4. Status bar shows which proxy is active
5. Badge color changes to green (SOCKS proxy active)
6. All traffic routes through selected proxy

### Step 4: Test & Rotate

1. Click "Test" to verify proxy connectivity
2. Switch proxies anytime by clicking "Use"
3. Monitor latency and connection quality
4. Remove dead proxies with "Remove" button

---

## Tips & Best Practices

### For iProxyal Users

1. **Organize by Region**
   - Name proxies by region: "US-1", "EU-2", etc.
   - Makes rotation easier

2. **Regular Testing**
   - Test proxies periodically
   - Remove non-responsive ones
   - Keep list fresh

3. **Bulk Operations**
   - Import all proxies at once
   - Don't need to add individually
   - Can export later for backup

4. **Export Regularly**
   - Keep backup copy of proxy list
   - Easy restoration if issues occur

### For Performance

1. **Check Interval**
   - Shorter intervals = more accurate but higher CPU
   - Longer intervals = lower resource usage

2. **Transparency**
   - Higher opacity = faster rendering
   - 100% is fastest, 50% requires more GPU

3. **Animations**
   - Disable if experiencing lag
   - Especially on older systems

### For Security

1. **Use Authentication**
   - Always enable username/password if available
   - Prevents unauthorized proxy access

2. **Test New Proxies**
   - Click "Test" before heavy use
   - Verify connectivity first

3. **Remove Unused**
   - Delete old/unused proxies
   - Keeps list manageable and clean

---

## Troubleshooting

### Proxy Won't Connect

1. Click "Test" to check reachability
2. Verify host and port are correct
3. Check if proxy requires username/password
4. Ensure proxy service is running (iProxyal, etc.)

### Import Not Working

1. Check format is correct (iProxyal, JSON, or CSV)
2. Verify no extra whitespace or special characters
3. Try importing just one proxy manually
4. Check backend is running

### Colors Not Showing

1. Save settings after changing colors
2. Refresh browser or restart extension
3. Check browser console for errors (F12)

### Performance Issues

1. Increase check interval (5-15 seconds)
2. Disable animations if not needed
3. Reduce popup window size
4. Increase window opacity (less transparency = faster)

---

## Storage

- **Location**: Chrome local storage (if browser-based)
- **File-based**: `proxies.json` in backend directory
- **Automatic backup**: Export proxies regularly
- **Persistent**: Settings saved across sessions

---

## File Structure

```
extension/
├── settings.html      # Settings UI
├── settings.css       # Settings styling
├── settings.js        # Settings logic
├── popup.html         # Main popup
├── popup.js           # Popup logic
├── background.js      # Service worker
├── styles.css         # Popup styling
└── manifest.json      # Extension config

backend/
├── app.py             # Main Flask app
├── proxy_manager.py   # Proxy management
├── proxies.json       # Stored proxies
└── requirements.txt   # Dependencies
```

---

## Next Steps

1. **Import your iProxyal proxies** using the guide above
2. **Customize appearance** to your preference
3. **Set color theme** matching your workflow
4. **Test proxies** to ensure connectivity
5. **Monitor status** in real-time while browsing

Enjoy your advanced proxy management system!
