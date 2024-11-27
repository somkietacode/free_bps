import configparser
import secrets
from fastapi import FastAPI, Request, HTTPException, Depends, Query
from datetime import datetime, timedelta
from typing import Dict
import httpx

app = FastAPI()

# Mock session store and brute force protection
SESSION_STORE: Dict[str, dict] = {}
BLOCKED_IPS: Dict[str, datetime] = {}
INVALID_REQUESTS: Dict[str, list] = {}

API_KEY_EXPIRATION = timedelta(days=1)

# Load backend configuration from bps.conf
config = configparser.ConfigParser()
config.read("bps.conf")
BACKEND_URL = config.get("backend", "url")

if not BACKEND_URL:
    raise ValueError("Backend URL not configured in bps.conf")


@app.post("/auth")
async def auth_proxy(request: Request):
    ip = request.client.host
    
    if ip in BLOCKED_IPS and datetime.now() < BLOCKED_IPS[ip]:
        raise HTTPException(status_code=403, detail="IP blocked due to repeated invalid requests.")

    # Forward the request to the backend
    try:
        async with httpx.AsyncClient() as client:
            backend_response = await client.post(f"{BACKEND_URL}/auth", content=await request.body())
            backend_response_json = backend_response.json()

        # Check backend response
        if backend_response_json.get("success"):
            # Generate a random 16-character API key
            api_key = secrets.token_hex(8)  # Generates a 16-character hexadecimal string
            SESSION_STORE[api_key] = {
                "expires_at": datetime.now() + API_KEY_EXPIRATION
            }
            return {"API_KEY": api_key}
        else:
            return {"error": "Invalid credentials"}
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Error forwarding to backend: {exc}")


@app.get("/{endpoint}")
async def proxy_request(endpoint: str, KEY: str = Query(None), request: Request = None):
    ip = request.client.host
    
    if ip in BLOCKED_IPS and datetime.now() < BLOCKED_IPS[ip]:
        raise HTTPException(status_code=403, detail="IP blocked due to repeated invalid requests.")

    # Validate API Key
    if not KEY:
        track_invalid_requests(ip)
        return {"error": "key not provided"}
    
    session = SESSION_STORE.get(KEY)
    if not session or session["expires_at"] < datetime.now():
        track_invalid_requests(ip)
        return {"error": "Invalid key"}
    
    # Forward request to backend without the KEY parameter
    try:
        async with httpx.AsyncClient() as client:
            # Forward request headers and body
            backend_response = await client.get(
                f"{BACKEND_URL}/{endpoint}",
                params=request.query_params.dict(exclude={"KEY"}),
                headers=request.headers
            )
        return backend_response.json()
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Error forwarding to backend: {exc}")


def track_invalid_requests(ip: str):
    now = datetime.now()
    INVALID_REQUESTS.setdefault(ip, []).append(now)
    
    # Remove old entries outside the 5-second window
    INVALID_REQUESTS[ip] = [t for t in INVALID_REQUESTS[ip] if now - t <= timedelta(seconds=5)]
    
    if len(INVALID_REQUESTS[ip]) > 5:
        BLOCKED_IPS[ip] = now + timedelta(days=1)
        del INVALID_REQUESTS[ip]


# Cleanup expired sessions
@app.on_event("startup")
async def cleanup_sessions():
    import asyncio
    while True:
        expired_keys = [key for key, session in SESSION_STORE.items() if session["expires_at"] < datetime.now()]
        for key in expired_keys:
            del SESSION_STORE[key]
        await asyncio.sleep(60)  # Cleanup every 60 seconds


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
