"""
Multi-Proxy Management Module
Handles SOCKS5 proxy list management, import/export, and proxy rotation
"""

import json
import os
from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime

PROXIES_FILE = 'proxies.json'


class ProxyManager:
    """Manages multiple SOCKS5 proxies and configurations"""

    def __init__(self, data_dir: str = '.'):
        self.data_dir = Path(data_dir)
        self.proxies_file = self.data_dir / PROXIES_FILE
        self.proxies: List[Dict[str, Any]] = []
        self.active_proxy_id = None
        self.load_proxies()

    def load_proxies(self):
        """Load proxies from file"""
        if self.proxies_file.exists():
            try:
                with open(self.proxies_file, 'r') as f:
                    data = json.load(f)
                    self.proxies = data.get('proxies', [])
                    self.active_proxy_id = data.get('active_proxy_id')
            except Exception as e:
                print(f"Error loading proxies: {e}")
                self.proxies = []

    def save_proxies(self):
        """Save proxies to file"""
        try:
            data = {
                'proxies': self.proxies,
                'active_proxy_id': self.active_proxy_id,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.proxies_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving proxies: {e}")
            return False

    def add_proxy(self, host: str, port: int, name: str = None, 
                  username: str = None, password: str = None) -> Dict[str, Any]:
        """Add a new proxy"""
        proxy_id = f"proxy_{len(self.proxies)}_{int(datetime.now().timestamp())}"
        
        proxy = {
            'id': proxy_id,
            'host': host,
            'port': port,
            'name': name or f"{host}:{port}",
            'username': username,
            'password': password,
            'created_at': datetime.now().isoformat(),
            'last_used': None,
            'active': False
        }
        
        self.proxies.append(proxy)
        self.save_proxies()
        return proxy

    def remove_proxy(self, proxy_id: str) -> bool:
        """Remove a proxy"""
        self.proxies = [p for p in self.proxies if p['id'] != proxy_id]
        if self.active_proxy_id == proxy_id:
            self.active_proxy_id = None
        self.save_proxies()
        return True

    def set_active_proxy(self, proxy_id: str) -> bool:
        """Set active proxy"""
        # Deactivate all
        for proxy in self.proxies:
            proxy['active'] = False
        
        # Activate selected
        for proxy in self.proxies:
            if proxy['id'] == proxy_id:
                proxy['active'] = True
                proxy['last_used'] = datetime.now().isoformat()
                self.active_proxy_id = proxy_id
                self.save_proxies()
                return True
        
        return False

    def get_active_proxy(self) -> Dict[str, Any]:
        """Get currently active proxy"""
        for proxy in self.proxies:
            if proxy['id'] == self.active_proxy_id:
                return proxy
        return None

    def list_proxies(self) -> List[Dict[str, Any]]:
        """Get all proxies"""
        return self.proxies

    def import_iproxyal(self, paste_data: str) -> Dict[str, Any]:
        """
        Import proxies from iProxyal paste format
        Expected format: host:port or host:port:username:password
        One per line
        """
        imported = []
        lines = paste_data.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            parts = line.split(':')
            
            if len(parts) == 2:
                host, port = parts
                proxy = self.add_proxy(host, int(port))
                imported.append(proxy)
            elif len(parts) >= 4:
                host, port, username, password = parts[0], parts[1], parts[2], parts[3]
                proxy = self.add_proxy(host, int(port), username=username, password=password)
                imported.append(proxy)
        
        return {
            'success': len(imported) > 0,
            'imported': len(imported),
            'proxies': imported
        }

    def import_json(self, json_str: str) -> Dict[str, Any]:
        """Import proxies from JSON format"""
        try:
            data = json.loads(json_str)
            imported = []
            
            # Handle array of proxies
            if isinstance(data, list):
                for item in data:
                    proxy = self.add_proxy(
                        host=item.get('host') or item.get('ip'),
                        port=int(item.get('port')),
                        name=item.get('name'),
                        username=item.get('username'),
                        password=item.get('password')
                    )
                    imported.append(proxy)
            
            return {
                'success': len(imported) > 0,
                'imported': len(imported),
                'proxies': imported
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'imported': 0,
                'proxies': []
            }

    def import_csv(self, csv_str: str) -> Dict[str, Any]:
        """Import proxies from CSV format"""
        try:
            import csv
            from io import StringIO
            
            imported = []
            reader = csv.DictReader(StringIO(csv_str))
            
            for row in reader:
                proxy = self.add_proxy(
                    host=row.get('host') or row.get('ip') or row.get('IP'),
                    port=int(row.get('port') or row.get('PORT')),
                    name=row.get('name'),
                    username=row.get('username'),
                    password=row.get('password')
                )
                imported.append(proxy)
            
            return {
                'success': len(imported) > 0,
                'imported': len(imported),
                'proxies': imported
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'imported': 0,
                'proxies': []
            }

    def export_json(self) -> str:
        """Export proxies as JSON"""
        return json.dumps(self.proxies, indent=2)

    def export_iproxyal_format(self) -> str:
        """Export proxies in iProxyal format (host:port or host:port:user:pass)"""
        lines = []
        for proxy in self.proxies:
            if proxy.get('username') and proxy.get('password'):
                lines.append(f"{proxy['host']}:{proxy['port']}:{proxy['username']}:{proxy['password']}")
            else:
                lines.append(f"{proxy['host']}:{proxy['port']}")
        return '\n'.join(lines)

    def get_proxy_connection_string(self, proxy_id: str = None) -> str:
        """Get connection string for a proxy (for socks5://... format)"""
        proxy = None
        
        if proxy_id:
            proxy = next((p for p in self.proxies if p['id'] == proxy_id), None)
        else:
            proxy = self.get_active_proxy()
        
        if not proxy:
            return None
        
        if proxy.get('username') and proxy.get('password'):
            return f"socks5://{proxy['username']}:{proxy['password']}@{proxy['host']}:{proxy['port']}"
        else:
            return f"socks5://{proxy['host']}:{proxy['port']}"

    def get_proxy_curl_command(self, proxy_id: str = None) -> str:
        """Generate curl command with proxy"""
        connection_string = self.get_proxy_connection_string(proxy_id)
        if connection_string:
            return f'curl -x "{connection_string}" https://api.ipify.org?format=json'
        return None

    def test_proxy(self, proxy_id: str = None) -> bool:
        """Test if a proxy is reachable"""
        proxy = None
        
        if proxy_id:
            proxy = next((p for p in self.proxies if p['id'] == proxy_id), None)
        else:
            proxy = self.get_active_proxy()
        
        if not proxy:
            return False
        
        import socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((proxy['host'], proxy['port']))
            sock.close()
            return result == 0
        except Exception:
            return False
