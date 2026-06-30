"""
API serverless pour Vercel — Authentification Notion
Fichier unique pour Vercel Python serverless functions.
"""
import os
import json
import httpx
import bcrypt
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# --- Config ---
JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 1

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"

# --- App ---
app = FastAPI(title="IA Doc Security Checker API")

# CORS — allow all origins (Vercel frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoginRequest(BaseModel):
    email: str
    password: str


@app.post("/api/auth/login")
async def login(req: LoginRequest):
    """Authentification: email + password → JWT token via Notion."""
    notion_token = os.environ.get("NOTION_TOKEN", "")
    notion_db_id = os.environ.get("NOTION_USERS_DB_ID", "")

    if not notion_token or not notion_db_id:
        raise HTTPException(status_code=500, detail="Configuration Notion manquante")

    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }

    payload = {
        "filter": {
            "and": [
                {"property": "Email", "email": {"equals": req.email}},
                {"property": "Actif", "checkbox": {"equals": True}},
            ]
        },
        "page_size": 1,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{NOTION_API}/databases/{notion_db_id}/query",
                headers=headers,
                json=payload,
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur Notion: {str(e)}")

    if resp.status_code != 200:
        raise HTTPException(status_code=500, detail="Erreur Notion API")

    data = resp.json()
    results = data.get("results", [])
    if not results:
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    page = results[0]
    props = page.get("properties", {})

    # Extract password hash
    password_hash = ""
    rich_text = props.get("Password hash", {}).get("rich_text", [])
    if rich_text:
        password_hash = rich_text[0].get("plain_text", "")

    if not password_hash:
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    # Verify password
    try:
        if not bcrypt.checkpw(req.password.encode("utf-8"), password_hash.encode("utf-8")):
            raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    except Exception:
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

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
        "sub": req.email,
        "name": name,
        "formation": formation,
        "exp": expire,
    }
    token = jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return {"token": token, "user": {"name": name, "email": req.email, "formation": formation}}


@app.get("/api/health")
async def health():
    """Health check."""
    notion_ok = bool(os.environ.get("NOTION_TOKEN") and os.environ.get("NOTION_USERS_DB_ID"))
    return {
        "status": "ok",
        "notion": "configured" if notion_ok else "not_configured",
        "ollama": "vps_required",
    }


@app.post("/api/analyze")
async def analyze(request: Request):
    """
    Proxy vers le VPS pour l'analyse de documents.
    Le VPS a Ollama local, Vercel n'en a pas.
    """
    vps_url = os.environ.get("VPS_API_URL", "https://ai-checker.srv1179315.hstgr.cloud")

    # Forward the request to VPS
    auth = request.headers.get("authorization", "")
    content_type = request.headers.get("content-type", "")

    body = await request.body()

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{vps_url}/analyze",
                headers={
                    "Authorization": auth,
                    "Content-Type": content_type,
                },
                content=body,
            )
        return JSONResponse(content=resp.json(), status_code=resp.status_code)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erreur VPS: {str(e)}")