import os
import sys
import json
import requests

# Add modules to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    from modules.env_loader import load_env_file
    # Load env vars from file
    load_env_file()
except ImportError:
    pass

key = os.getenv("ANTHROPIC_API_KEY", "")
if not key:
    print("NO_KEY: ANTHROPIC_API_KEY not set in environment")
    sys.exit(2)

model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

headers = {
    "x-api-key": key,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json",
}

payload = {
    "model": model,
    "max_tokens": 1,
    "messages": [
        {"role": "user", "content": [{"type": "text", "text": "ping"}]}
    ],
}

try:
    resp = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload, timeout=20)
    print("STATUS", resp.status_code)
    try:
        print("BODY", json.dumps(resp.json(), indent=2)[:500])
    except Exception:
        print("TEXT", resp.text[:200])
    sys.exit(0 if resp.status_code == 200 else 1)
except Exception as e:
    print("ERROR", str(e))
    sys.exit(3)
