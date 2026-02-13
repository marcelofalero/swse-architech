from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import json
import time
import uuid
from jose import jwt
import httpx
import js

app = FastAPI()

# --- Helpers ---

async def get_env():
    return js.env

async def get_db():
    env = await get_env()
    return env.DB

# --- Models ---

class Link(BaseModel):
    href: str
    rel: str
    method: str

class Ship(BaseModel):
    id: str
    owner_id: str
    name: Optional[str]
    data: Dict[str, Any]
    visibility: str
    created_at: int
    updated_at: int
    links: Dict[str, Link] = Field(alias="_links")

class CreateShip(BaseModel):
    name: str
    data: Dict[str, Any]
    visibility: str = "private"

class ShareShip(BaseModel):
    grantee_id: str
    grantee_type: str # user, group, app
    access_level: str # read, write, admin

class User(BaseModel):
    id: str
    email: str
    name: str

# --- Auth ---

jwks_cache = {"keys": None, "expiry": 0}

async def get_jwks():
    now = time.time()
    if jwks_cache["keys"] and now < jwks_cache["expiry"]:
        return jwks_cache["keys"]
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get("https://www.googleapis.com/oauth2/v3/certs")
            keys = resp.json()
            jwks_cache["keys"] = keys
            jwks_cache["expiry"] = now + 3600
            return keys
        except Exception as e:
            print(f"Failed to fetch JWKS: {e}")
            return None

async def verify_google_token(token: str, client_id: str):
    jwks = await get_jwks()
    if not jwks:
        return None

    try:
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            audience=client_id,
            options={"verify_at_hash": False}
        )
        return payload
    except Exception as e:
        print(f"Token verification failed: {e}")
        return None

async def get_current_user(request: Request) -> Optional[User]:
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return None
    token = auth.split(" ")[1]
    env = await get_env()
    try:
        payload = jwt.decode(token, env.SESSION_SECRET, algorithms=["HS256"])
        return User(id=payload["sub"], email=payload["email"], name=payload["name"])
    except:
        return None

# --- Endpoints ---

@app.get("/auth/google")
async def auth_google(token: str):
    env = await get_env()
    payload = await verify_google_token(token, env.GOOGLE_CLIENT_ID)
    if not payload:
        raise HTTPException(status_code=400, detail="Invalid token")

    user_id = payload["sub"]
    email = payload["email"]
    name = payload.get("name", "")

    db = await get_db()

    # Upsert user
    res = await db.prepare("SELECT * FROM users WHERE id = ?").bind(user_id).all()
    results = res.results
    if hasattr(results, 'to_py'):
        results = results.to_py()

    if not results:
        await db.prepare("INSERT INTO users (id, email, name) VALUES (?, ?, ?)").bind(user_id, email, name).run()

    # Create session token
    session_payload = {
        "sub": user_id,
        "email": email,
        "name": name,
        "exp": int(time.time()) + 86400 * 7 # 7 days
    }
    session_token = jwt.encode(session_payload, env.SESSION_SECRET, algorithm="HS256")
    return {"access_token": session_token, "token_type": "bearer"}

@app.get("/ships", response_model=List[Ship])
async def list_ships(request: Request):
    user = await get_current_user(request)
    user_id = user.id if user else None

    db = await get_db()

    if user_id:
        # Select distinct ships and the specific permission level for the user
        sql = """
        SELECT s.*, p.access_level
        FROM ships s
        LEFT JOIN permissions p ON s.id = p.target_id AND p.grantee_id = ? AND p.grantee_type = 'user'
        WHERE s.visibility = 'public'
           OR s.owner_id = ?
           OR p.access_level IS NOT NULL
        """
        params = [user_id, user_id]
    else:
        sql = "SELECT *, NULL as access_level FROM ships WHERE visibility = 'public'"
        params = []

    res = await db.prepare(sql).bind(*params).all()
    results = res.results
    if hasattr(results, 'to_py'):
        results = results.to_py()

    ships = []
    for row in results:
        # Determine access level
        effective_access = 'read' # default for public
        if user_id and row['owner_id'] == user_id:
            effective_access = 'admin'
        elif 'access_level' in row and row['access_level']:
            effective_access = row['access_level']

        # HATEOAS Links
        links = {
            "self": Link(href=f"/ships/{row['id']}", rel="self", method="GET")
        }

        if effective_access in ['write', 'admin']:
            links["update"] = Link(href=f"/ships/{row['id']}", rel="update", method="PUT")

        if effective_access == 'admin':
            links["share"] = Link(href=f"/ships/{row['id']}/share", rel="share", method="PATCH")
            links["delete"] = Link(href=f"/ships/{row['id']}", rel="delete", method="DELETE")

        ships.append(Ship(
            id=row['id'],
            owner_id=row['owner_id'],
            name=row['name'],
            data=json.loads(row['data']),
            visibility=row['visibility'],
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            _links=links
        ))
    return ships

@app.post("/ships", response_model=Ship)
async def create_ship(ship_req: CreateShip, request: Request):
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    ship_id = str(uuid.uuid4())
    db = await get_db()

    # Store data
    await db.prepare("""
        INSERT INTO ships (id, owner_id, name, data, visibility)
        VALUES (?, ?, ?, ?, ?)
    """).bind(
        ship_id, user.id, ship_req.name, json.dumps(ship_req.data), ship_req.visibility
    ).run()

    links = {
        "self": Link(href=f"/ships/{ship_id}", rel="self", method="GET"),
        "update": Link(href=f"/ships/{ship_id}", rel="update", method="PUT"),
        "share": Link(href=f"/ships/{ship_id}/share", rel="share", method="PATCH"),
        "delete": Link(href=f"/ships/{ship_id}", rel="delete", method="DELETE")
    }

    current_time = int(time.time())

    return Ship(
        id=ship_id,
        owner_id=user.id,
        name=ship_req.name,
        data=ship_req.data,
        visibility=ship_req.visibility,
        created_at=current_time,
        updated_at=current_time,
        _links=links
    )

@app.patch("/ships/{ship_id}/share")
async def share_ship(ship_id: str, share_req: ShareShip, request: Request):
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    db = await get_db()

    # Verify ownership or admin access
    # Fetch ship and user permission
    res = await db.prepare("""
        SELECT s.owner_id, p.access_level
        FROM ships s
        LEFT JOIN permissions p ON s.id = p.target_id AND p.grantee_id = ?
        WHERE s.id = ?
    """).bind(user.id, ship_id).all()

    results = res.results
    if hasattr(results, 'to_py'):
        results = results.to_py()

    if not results:
        raise HTTPException(status_code=404, detail="Ship not found")

    row = results[0]
    is_owner = row['owner_id'] == user.id
    access_level = row.get('access_level')

    if not is_owner and access_level != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized to share this ship")

    # Upsert permission
    await db.prepare("""
        INSERT INTO permissions (target_id, grantee_id, grantee_type, access_level)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(target_id, grantee_id, grantee_type)
        DO UPDATE SET access_level = excluded.access_level
    """).bind(
        ship_id, share_req.grantee_id, share_req.grantee_type, share_req.access_level
    ).run()

    return {"status": "ok"}
