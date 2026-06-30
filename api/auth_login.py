"""
Authentification via Notion API — Vercel Serverless Function
POST /api/auth/login → { email, password } → { token, user }
"""
import os
import json
import httpx
import bcrypt
from datetime import datetime, timedelta, timezone
from jose import jwt

JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 1

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


def handler(request):
    """Vercel Python serverless handler."""
    # Parse body
    try:
        body = request.json() if hasattr(request, "json") else json.loads(request.body)
    except Exception:
        body = request if isinstance(request, dict) else {}

    email = body.get("email", "")
    password = body.get("password", "")

    if not email or not password:
        return {
            "statusCode": 400,
            "body": json.dumps({"detail": "Email et mot de passe requis"}),
        }

    notion_token = os.environ.get("NOTION_TOKEN", "")
    notion_db_id = os.environ.get("NOTION_USERS_DB_ID", "")

    if not notion_token or not notion_db_id:
        return {
            "statusCode": 500,
            "body": json.dumps({"detail": "Configuration Notion manquante"}),
        }

    # Query Notion for user
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }

    payload = {
        "filter": {
            "and": [
                {"property": "Email", "email": {"equals": email}},
                {"property": "Actif", "checkbox": {"equals": True}},
            ]
        },
        "page_size": 1,
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(
                f"{NOTION_API}/databases/{notion_db_id}/query",
                headers=headers,
                json=payload,
            )
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"detail": f"Erreur Notion: {str(e)}"}),
        }

    if resp.status_code != 200:
        return {
            "statusCode": 500,
            "body": json.dumps({"detail": "Erreur Notion API"}),
        }

    data = resp.json()
    results = data.get("results", [])
    if not results:
        return {
            "statusCode": 401,
            "body": json.dumps({"detail": "Email ou mot de passe incorrect"}),
        }

    page = results[0]
    props = page.get("properties", {})

    # Extract password hash
    password_hash = ""
    rich_text = props.get("Password hash", {}).get("rich_text", [])
    if rich_text:
        password_hash = rich_text[0].get("plain_text", "")

    # Verify password
    if not password_hash:
        return {
            "statusCode": 401,
            "body": json.dumps({"detail": "Email ou mot de passe incorrect"}),
        }

    try:
        if not bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8")):
            return {
                "statusCode": 401,
                "body": json.dumps({"detail": "Email ou mot de passe incorrect"}),
            }
    except Exception:
        return {
            "statusCode": 401,
            "body": json.dumps({"detail": "Email ou mot de passe incorrect"}),
        }

    # Extract user info
    name = ""
    title = props.get("Nom", {}).get("title", [])
    if title:
        name = title[0].get("plain_text", "")

    formation = ""
    select = props.get("Formation", {}).get("select")
    if select:
        formation = select.get("name", "")

    # Create JWT
    expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS)
    token_payload = {
        "sub": email,
        "name": name,
        "formation": formation,
        "exp": expire,
    }
    token = jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "token": token,
            "user": {"name": name, "email": email, "formation": formation},
        }),
    }