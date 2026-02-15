
Persistent SOCKS5 connector
===========================

Quick script to parse a curl command or a JSON proxy spec and keep a TCP connection to a SOCKS5 proxy open until terminated.

Usage
-----

- Run interactively and paste a curl command or JSON, finish with EOF (Ctrl+Z then Enter on Windows):

```bash
python scripts/socks5_persist.py
# paste: --socks5 user:pass@proxy.example.com:1080
# then EOF (Ctrl+Z+Enter on Windows)
```

- Or provide a JSON file:

```bash
cat proxy.json
# {"host":"proxy.example.com","port":1080,"username":"user","password":"pass"}
python scripts/socks5_persist.py --file proxy.json
```

Supported input forms
---------------------
- curl forms with `--socks5`, `--proxy socks5://...`, or `-x HOST:PORT`
- JSON objects with `proxy` string (e.g. `"socks5://user:pass@host:port"`) or fields `host`/`port`/`username`/`password`

Notes
-----
- The script performs the SOCKS5 greeting and optional username/password auth, then leaves the socket open.
- On Windows, socket keepalive intervals use OS defaults. Press Ctrl+C to terminate and close the connection.

Security
--------
- Be careful with credentials in shell history or files.
