#!/usr/bin/env python3
"""Create the Notion database for user authentication."""
import os
import sys
import json
import urllib.request
import urllib.error

# Read .env
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
if not os.path.exists(env_path):
    env_path = os.path.join(os.getcwd(), ".env")

with open(env_path, "r") as f:
    for line in f:
        line = line.strip()
        if line.startswith("NOTION_TOKEN="):
            token = line.split("=", 1)[1].strip().strip('"').strip("'")
            break
    else:
        print("ERROR: NOTION_TOKEN not found in .env")
        sys.exit(1)

print(f"Token loaded: {token[:8]}...{token[-4:]} (length: {len(token)})")

# Notion API
NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"

# Page parent (from URL: 38f9628038de80f28641c799de26156d)
PAGE_ID = "38f96280-38de-80f2-8641-c799de26156d"

# Create database
payload = {
    "parent": {"type": "page_id", "page_id": PAGE_ID},
    "icon": {"type": "emoji", "emoji": "\U0001F510"},
    "title": [{"type": "text", "text": {"content": "Utilisateurs \u2014 IA Doc Security Checker"}}],
    "properties": {
        "Nom": {"title": {}},
        "Email": {"email": {}},
        "Password hash": {"rich_text": {}},
        "Formation": {
            "select": {
                "options": [
                    {"name": "Formation IA s\u00e9curis\u00e9e", "color": "blue"},
                    {"name": "Formation TPE", "color": "green"},
                    {"name": "Formation PME", "color": "purple"},
                    {"name": "Acc\u00e8s standalone", "color": "gray"}
                ]
            }
        },
        "Actif": {"checkbox": {}},
        "Date cr\u00e9ation": {"date": {}}
    }
}

data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(
    f"{NOTION_API}/databases",
    data=data,
    method="POST"
)
req.add_header("Authorization", f"Bearer {token}")
req.add_header("Notion-Version", NOTION_VERSION)
req.add_header("Content-Type", "application/json")

try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        db_id = result["id"]
        db_url = result["url"]
        print(f"\n\u2705 Database created successfully!")
        print(f"   Database ID: {db_id}")
        print(f"   URL: {db_url}")
        print(f"\n   Add this to .env:")
        print(f"   NOTION_USERS_DB_ID={db_id}")

        # Now create a test user
        print("\nCreating test user...")
        from passlib.hash import bcrypt
        password_hash = bcrypt.hash("admin123")

        user_payload = {
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

        user_data = json.dumps(user_payload).encode("utf-8")
        user_req = urllib.request.Request(
            f"{NOTION_API}/pages",
            data=user_data,
            method="POST"
        )
        user_req.add_header("Authorization", f"Bearer {token}")
        user_req.add_header("Notion-Version", NOTION_VERSION)
        user_req.add_header("Content-Type", "application/json")

        with urllib.request.urlopen(user_req, timeout=15) as user_resp:
            print(f"\n\u2705 Test user created: admin@test.fr / admin123")

        print(f"\n\u2705 Setup complete! Add to .env:")
        print(f"   NOTION_USERS_DB_ID={db_id}")

except urllib.error.HTTPError as e:
    error_body = e.read().decode("utf-8")
    print(f"\n\u274c Error {e.code}: {error_body}")
except Exception as e:
    print(f"\n\u274c Error: {e}")