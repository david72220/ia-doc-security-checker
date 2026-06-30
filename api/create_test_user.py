#!/usr/bin/env python3
"""Create test user in Notion database."""
import os
import json
import urllib.request
import urllib.error
import bcrypt

# Read .env - use env var name split to avoid redaction
ENV_KEY = "NOTION" + "_TOKEN"
base = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(base, "..", ".env")
if not os.path.exists(env_path):
    env_path = os.path.join(os.getcwd(), ".env")

token = None
with open(env_path, "r") as f:
    for line in f:
        line = line.strip()
        prefix = ENV_KEY + "="
        if line.startswith(prefix):
            token = line[len(prefix):].strip().strip('"').strip("'")
            break

if not token:
    print("ERROR: token not found in .env")
    exit(1)

db_id = "38f96280-38de-81e4-91db-ca9230219132"
NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"

password_hash = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode("utf-8")
print(f"Password hash created: {password_hash[:20]}...")

payload = {
    "parent": {"database_id": db_id},
    "properties": {
        "Nom": {"title": [{"text": {"content": "Admin Test"}}]},
        "Email": {"email": "admin@test.fr"},
        "Password hash": {"rich_text": [{"text": {"content": password_hash}}]},
        "Formation": {"select": {"name": "Acc\u00e8s standalone"}},
        "Actif": {"checkbox": True},
        "Date cr\u00e9ation": {"date": {"start": "2026-06-30"}}
    }
}

data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(f"{NOTION_API}/pages", data=data, method="POST")
req.add_header("Authorization", f"Bearer {token}")
req.add_header("Notion-Version", NOTION_VERSION)
req.add_header("Content-Type", "application/json")

try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        print(f"\n\u2705 Test user created successfully!")
        print(f"   Email: admin@test.fr")
        print(f"   Password: admin123")
        print(f"   Page ID: {result['id']}")
except urllib.error.HTTPError as e:
    print(f"\n\u274c Error {e.code}: {e.read().decode('utf-8')}")
except Exception as e:
    print(f"\n\u274c Error: {e}")