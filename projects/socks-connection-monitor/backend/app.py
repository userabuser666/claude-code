"""
SOCKS Proxy Connection Monitor - Python Backend
Provides API endpoints for checking SOCKS proxy status, IP detection, and latency
from flask import Flask, jsonify, request # type: ignore
from flask_cors import CORS
import requests
import socket
import time
import threading
from typing import Dict, Any
import json
import psutil
import subprocess
from pathlib import Path

from proxy_manager import ProxyManager

app = Flask(__name__)
CORS(app)

# Initialize proxy manager
proxy_manager = ProxyManager('.')

# Configuration
CONFIG = {
    'socks_host': 'localhost',
    'socks_port': 1080,
    'check_interval': 5,
    'timeout': 5,
}

# VPN Provider Detection
VPN_PROVIDERS = {
    'expressvpn': {
        'name': 'ExpressVPN',
        'processes': ['ExpressVpn.exe', 'expressvpnd.exe'],
        'ports': [1195, 1196, 8443],  # Common ExpressVPN ports
        'registry_path': r'HKEY_LOCAL_MACHINE\SOFTWARE\ExpressVPN',
        'color': '#FF6B35'  # Orange for VPN
    },
    'nordvpn': {
        'name': 'NordVPN',
        'processes': ['NordVPN.exe', 'nordvpn.exe'],
        'ports': [443, 1194, 1195],  # Common NordVPN ports
        'registry_path': r'HKEY_LOCAL_MACHINE\SOFTWARE\NordVPN',
        'color': '#4169E1'  # Royal Blue for NordVPN
    },
    'unknown_vpn': {
        'name': 'Unknown VPN',
        'processes': ['vpn.exe', 'vpnclient.exe', 'openvpn.exe'],
        'ports': [],
        'color': '#9932CC'  # Dark Orchid for unknown VPN
    }
}

# Cache to reduce API calls
CACHE = {
    'last_ip_check': 0,
    'last_proxy_check': 0,
    'cached_data': {}
}

CACHE_DURATION = 3  # seconds


def is_socks_available() -> bool:
    """Check if SOCKS5 proxy is reachable"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(CONFIG['timeout'])
        result = sock.connect_ex((CONFIG['socks_host'], CONFIG['socks_port']))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"SOCKS check error: {e}")
        return False


def detect_running_processes() -> list:
    """Get list of running process names"""
    try:
        processes = [p.name().lower() for p in psutil.process_iter(['name'])]
        return processes
    except Exception as e:
        print(f"Process detection error: {e}")
        return []


def is_port_listening(port: int) -> bool:
    """Check if a port has an active connection"""
    try:
        connections = psutil.net_connections()
        for conn in connections:
            if conn.laddr.port == port and conn.status == 'LISTEN':
                return True
        return False
    except Exception as e:
        print(f"Port check error: {e}")
        return False


def detect_vpn() -> dict:
    """
    Detect if a VPN is active by checking:
    1. Running processes
    2. Listening ports
    3. Network adapters with VPN in name
    
    Returns dict with VPN info or None
    """
    running_processes = detect_running_processes()
    
    # Check each VPN provider
    for provider_id, provider_info in VPN_PROVIDERS.items():
        # Check for running processes
        for proc in provider_info['processes']:
            if proc.lower() in running_processes:
                print(f"VPN detected: {provider_info['name']} (process)")
                return {
                    'detected': True,
                    'provider': provider_id,
                    'name': provider_info['name'],
                    'color': provider_info['color'],
                    'detection_method': 'process'
                }
        
        # Check for listening ports (if provider-specific)
        if provider_info['ports']:
            for port in provider_info['ports']:
                if is_port_listening(port):
                    print(f"VPN detected: {provider_info['name']} (port {port})")
                    return {
                        'detected': True,
                        'provider': provider_id,
                        'name': provider_info['name'],
                        'color': provider_info['color'],
                        'detection_method': f'port_{port}'
                    }
    
    # Check for VPN network adapters (Windows)
    try:
        result = subprocess.run(
            ['ipconfig', '/all'],
            capture_output=True,
            text=True,
            timeout=5
        )
        output = result.stdout.lower()
        if 'tap' in output or 'tun' in output or 'vpn' in output:
            print("VPN detected: Unknown VPN (network adapter)")
            return {
                'detected': True,
                'provider': 'unknown_vpn',
                'name': 'Unknown VPN',
                'color': '#9932CC',
                'detection_method': 'network_adapter'
            }
    except Exception as e:
        print(f"VPN adapter check error: {e}")
    
    return {
        'detected': False,
        'provider': None,
        'name': None,
        'color': None,
        'detection_method': None
    }


def get_public_ip(use_proxy: bool = False) -> Dict[str, Any]:
    """Get public IP and related info, optionally through SOCKS proxy"""
    try:
        if use_proxy and is_socks_available():
            # Use SOCKS5 proxy
            proxies = {
                'http': f'socks5://{CONFIG["socks_host"]}:{CONFIG["socks_port"]}',
                'https': f'socks5://{CONFIG["socks_host"]}:{CONFIG["socks_port"]}'
            }
        else:
            proxies = None

        # Use multiple IP detection services for reliability
        services = [
            'https://api.ipify.org?format=json',
            'https://ip.googleapis.com/identities/lookup?prettyPrint=false',
        ]

        start_time = time.time()
        for service in services:
            try:
                response = requests.get(
                    service,
                    proxies=proxies,
                    timeout=CONFIG['timeout'],
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                response.raise_for_status()
                latency = (time.time() - start_time) * 1000  # ms

                data = response.json() if service == services[0] else {}
                
                return {
                    'success': True,
                    'ip': data.get('ip') if isinstance(data, dict) else response.text.strip(),
                    'latency': round(latency, 2),
                    'service': service.split('/')[2],
                    'via_proxy': use_proxy and is_socks_available()
                }
            except Exception as e:
                continue

        return {
            'success': False,
            'error': 'Could not reach IP detection services',
            'via_proxy': use_proxy and is_socks_available()
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'via_proxy': use_proxy and is_socks_available()
        }


def get_dns_servers() -> list:
    """Get current DNS servers"""
    try:
        import subprocess
        # Windows
        result = subprocess.run(
            ['ipconfig', '/all'],
            capture_output=True,
            text=True,
            timeout=5
        )
        dns_servers = []
        for line in result.stdout.split('\n'):
            if 'DNS Servers' in line or 'DNS Server' in line:
                parts = line.split(':')
                if len(parts) > 1:
                    dns = parts[1].strip()
                    if dns and dns not in dns_servers:
                        dns_servers.append(dns)
        return dns_servers[:2]  # Return first 2
    except Exception as e:
        print(f"DNS check error: {e}")
        return []


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get complete connection status"""
    current_time = time.time()
    
    # Check cache
    if current_time - CACHE['last_proxy_check'] < CACHE_DURATION:
        return jsonify(CACHE['cached_data']), 200

    # Detect VPN
    vpn_info = detect_vpn()
    
    socks_available = is_socks_available()
    ip_without_proxy = get_public_ip(use_proxy=False)
    ip_with_proxy = get_public_ip(use_proxy=True) if socks_available else None

    dns_servers = get_dns_servers()

    # Determine connection type and color
    connection_type = 'Direct'
    status_color = '#666666'  # Default gray
    
    if vpn_info['detected']:
        connection_type = f"VPN - {vpn_info['name']}"
        status_color = vpn_info['color']
    elif socks_available:
        connection_type = 'SOCKS Proxy'
        status_color = '#00AA00'  # Green
    else:
        connection_type = 'Direct'
        status_color = '#DD0000'  # Red (disconnected)

    data = {
        'timestamp': current_time,
        'vpn': vpn_info,
        'proxy': {
            'available': socks_available,
            'host': CONFIG['socks_host'],
            'port': CONFIG['socks_port'],
            'status': 'Connected' if socks_available else 'Disconnected'
        },
        'ip': {
            'direct': ip_without_proxy,
            'via_proxy': ip_with_proxy if socks_available else None
        },
        'dns': dns_servers,
        'connection_type': connection_type,
        'status_color': status_color
    }

    # Update cache
    CACHE['last_proxy_check'] = current_time
    CACHE['cached_data'] = data

    return jsonify(data), 200


@app.route('/api/ping', methods=['GET'])
def ping():
    """Simple health check"""
    return jsonify({'status': 'ok', 'timestamp': time.time()}), 200


@app.route('/api/config', methods=['GET', 'POST'])
def config():
    """Get or update configuration"""
    global CONFIG

    if request.method == 'GET':
        return jsonify(CONFIG), 200

    if request.method == 'POST':
        data = request.get_json()
        if 'socks_host' in data:
            CONFIG['socks_host'] = data['socks_host']
        if 'socks_port' in data:
            CONFIG['socks_port'] = int(data['socks_port'])
        if 'check_interval' in data:
            CONFIG['check_interval'] = int(data['check_interval'])
        if 'timeout' in data:
            CONFIG['timeout'] = int(data['timeout'])

        return jsonify({'message': 'Config updated', 'config': CONFIG}), 200


# Proxy Management Endpoints

@app.route('/api/proxies', methods=['GET'])
def list_proxies():
    """Get all proxies"""
    return jsonify({
        'proxies': proxy_manager.list_proxies(),
        'active_proxy_id': proxy_manager.active_proxy_id
    }), 200


@app.route('/api/proxies/add', methods=['POST'])
def add_proxy():
    """Add a new proxy"""
    data = request.get_json()
    
    try:
        proxy = proxy_manager.add_proxy(
            host=data.get('host'),
            port=int(data.get('port')),
            name=data.get('name'),
            username=data.get('username'),
            password=data.get('password')
        )
        return jsonify({'success': True, 'proxy': proxy}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/proxies/remove/<proxy_id>', methods=['DELETE'])
def remove_proxy(proxy_id):
    """Remove a proxy"""
    success = proxy_manager.remove_proxy(proxy_id)
    return jsonify({'success': success}), 200 if success else 404


@app.route('/api/proxies/activate/<proxy_id>', methods=['POST'])
def activate_proxy(proxy_id):
    """Activate a proxy"""
    success = proxy_manager.set_active_proxy(proxy_id)
    if success:
        return jsonify({
            'success': True,
            'active_proxy_id': proxy_id,
            'proxy': proxy_manager.get_active_proxy()
        }), 200
    else:
        return jsonify({'success': False, 'error': 'Proxy not found'}), 404


@app.route('/api/proxies/active', methods=['GET'])
def get_active_proxy():
    """Get active proxy"""
    proxy = proxy_manager.get_active_proxy()
    return jsonify({
        'active_proxy': proxy,
        'active_proxy_id': proxy_manager.active_proxy_id
    }), 200


@app.route('/api/proxies/import', methods=['POST'])
def import_proxies():
    """Import proxies from various formats"""
    data = request.get_json()
    import_type = data.get('type', 'iproxyal')  # iproxyal, json, csv
    content = data.get('content', '')
    
    try:
        if import_type == 'json':
            result = proxy_manager.import_json(content)
        elif import_type == 'csv':
            result = proxy_manager.import_csv(content)
        else:  # Default to iproxyal format
            result = proxy_manager.import_iproxyal(content)
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'imported': 0
        }), 400


@app.route('/api/proxies/export', methods=['GET'])
def export_proxies():
    """Export proxies"""
    format_type = request.args.get('format', 'json')  # json or iproxyal
    
    if format_type == 'iproxyal':
        return proxy_manager.export_iproxyal_format(), 200, {'Content-Type': 'text/plain'}
    else:
        return proxy_manager.export_json(), 200, {'Content-Type': 'application/json'}


@app.route('/api/proxies/test/<proxy_id>', methods=['POST'])
def test_proxy(proxy_id):
    """Test if a proxy is reachable"""
    is_reachable = proxy_manager.test_proxy(proxy_id)
    return jsonify({
        'proxy_id': proxy_id,
        'reachable': is_reachable
    }), 200


@app.route('/api/proxies/curl/<proxy_id>', methods=['GET'])
def get_curl_command(proxy_id):
    """Get curl command for a proxy"""
    cmd = proxy_manager.get_proxy_curl_command(proxy_id)
    if cmd:
        return jsonify({'command': cmd}), 200
    else:
        return jsonify({'error': 'Proxy not found'}), 404


@app.route('/')
def index():
    """Simple health check page"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>SOCKS Monitor Backend</title>
        <style>
            body { font-family: Arial; margin: 20px; background: #f0f0f0; }
            .container { max-width: 500px; margin: 0 auto; background: white; padding: 20px; border-radius: 5px; }
            h1 { color: #0066cc; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>SOCKS Connection Monitor</h1>
            <p>Backend API is running on port 5000</p>
            <p><strong>API Endpoints:</strong></p>
            <ul>
                <li>GET /api/status - Full connection status</li>
                <li>GET /api/ping - Health check</li>
                <li>GET /api/config - Get config</li>
                <li>POST /api/config - Update config</li>
            </ul>
        </div>
    </body>
    </html>
    ''', 200


if __name__ == '__main__':
    print("Starting SOCKS Connection Monitor Backend...")
    print(f"SOCKS Proxy: {CONFIG['socks_host']}:{CONFIG['socks_port']}")
    print("Running on http://localhost:5000")
    app.run(host='localhost', port=5000, debug=True, threaded=True)
