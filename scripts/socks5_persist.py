#!/usr/bin/env python3
"""Persistent SOCKS5 connector.

Usage:
  - Run and paste a curl command or JSON proxy spec (EOF to end paste), or pass `--file <path>` to read JSON.
  - The script extracts host, port, optional username/password, connects to the SOCKS5 proxy,
    performs SOCKS5 greeting and optional username/password auth, then keeps the TCP socket open
    until you press Ctrl+C.
"""
import argparse
import json
import re
import socket
import sys
import time


def parse_curl_or_text(text: str):
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return parse_json_obj(obj)
    except Exception:
        pass

    m = re.search(r'(socks5h?://[^\s"\']+)', text)
    if m:
        return parse_proxy_url(m.group(1))

    m = re.search(r'--socks5(?:-host)?\s+([^\s"\']+)', text)
    if m:
        return parse_proxy_url('socks5://' + m.group(1))
    m = re.search(r'--proxy\s+([^\s"\']+)', text)
    if m:
        return parse_proxy_url(m.group(1))
    m = re.search(r' -x\s+([^\s"\']+)', text)
    if m:
        return parse_proxy_url(m.group(1))

    m = re.search(r'([0-9a-zA-Z.-]+):(\d{1,5})', text)
    if m:
        return {"host": m.group(1), "port": int(m.group(2))}

    raise ValueError("Could not parse proxy from input")


def parse_proxy_url(url: str):
    if not re.match(r'^[a-zA-Z]+://', url):
        url = 'socks5://' + url
    m = re.match(r'^(?P<scheme>[^:]+)://(?:(?P<user>[^:@]+)(?::(?P<pass>[^@]*))?@)?(?P<host>[^:]+)(?::(?P<port>\d+))?$', url)
    if not m:
        raise ValueError(f'Unsupported proxy URL: {url}')
    host = m.group('host')
    port = int(m.group('port') or 1080)
    user = m.group('user')
    pwd = m.group('pass')
    return {"host": host, "port": port, "username": user, "password": pwd}


def parse_json_obj(obj: dict):
    if 'proxy' in obj and isinstance(obj['proxy'], str):
        return parse_proxy_url(obj['proxy'])
    host = obj.get('host') or obj.get('hostname')
    port = obj.get('port')
    if not host or not port:
        raise ValueError('JSON must contain host and port, or a proxy URL')
    return {"host": host, "port": int(port), "username": obj.get('username'), "password": obj.get('password')}


def socks5_handshake(sock: socket.socket, username=None, password=None, timeout=10):
    if username is not None and password is not None:
        methods = b"\x02"
    else:
        methods = b"\x00"
    sock.settimeout(timeout)
    sock.sendall(b"\x05" + bytes([len(methods)]) + methods)
    resp = sock.recv(2)
    if len(resp) < 2 or resp[0] != 0x05:
        raise RuntimeError('Invalid SOCKS5 response')
    method = resp[1]
    if method == 0xFF:
        raise RuntimeError('No acceptable authentication methods')
    if method == 0x02:
        u = username.encode('utf-8')
        p = password.encode('utf-8')
        if len(u) > 255 or len(p) > 255:
            raise RuntimeError('Username/password too long')
        auth = b"\x01" + bytes([len(u)]) + u + bytes([len(p)]) + p
        sock.sendall(auth)
        r = sock.recv(2)
        if len(r) < 2 or r[1] != 0x00:
            raise RuntimeError('SOCKS5 username/password auth failed')


def main():
    p = argparse.ArgumentParser(description='Persistent SOCKS5 connector (paste curl or JSON)')
    p.add_argument('--file', '-f', help='Read JSON spec from file instead of stdin/paste')
    args = p.parse_args()

    if args.file:
        with open(args.file, 'r', encoding='utf-8') as fh:
            content = fh.read()
    else:
        if not sys.stdin.isatty():
            content = sys.stdin.read()
        else:
            print('Paste the curl command or JSON proxy spec. End with EOF (Ctrl+Z+Enter on Windows).')
            content = sys.stdin.read()

    try:
        spec = parse_curl_or_text(content.strip())
    except Exception as e:
        print('Error parsing input:', e)
        sys.exit(2)

    host = spec['host']
    port = int(spec['port'])
    username = spec.get('username')
    password = spec.get('password')

    print(f'Connecting to SOCKS5 proxy {host}:{port}...')
    sock = socket.create_connection((host, port))
    try:
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        except Exception:
            pass
        socks5_handshake(sock, username=username, password=password)
    except Exception as e:
        sock.close()
        print('Handshake failed:', e)
        sys.exit(3)

    print('Authenticated (if required). Connection is now open and will be kept alive. Press Ctrl+C to terminate.')
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        print('\nTerminating connection...')
    finally:
        try:
            sock.close()
        except Exception:
            pass


if __name__ == '__main__':
    main()
