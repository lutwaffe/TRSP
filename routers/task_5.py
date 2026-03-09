import uuid
import time
from fastapi import APIRouter, Response, Cookie
from pydantic import BaseModel
from typing import Optional
from itsdangerous import URLSafeSerializer, BadSignature

router = APIRouter()

FAKE_USERS = {
    "user123": "password123",
    "admin": "admin",
}

FAKE_PROFILES = {
    "user123": {"username": "user123", "email": "user123@example.com", "role": "user"},
    "admin":   {"username": "admin",   "email": "admin@example.com",   "role": "admin"},
}

active_sessions: dict[str, str] = {}
user_store: dict[str, str] = {}
session_users: dict[str, str] = {}

SECRET_KEY = "super-secret-key"
signer = URLSafeSerializer(SECRET_KEY)
session_signer = URLSafeSerializer(SECRET_KEY + "_session")

SESSION_TTL = 300
RENEW_THRESHOLD = 180


class LoginData(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(data: LoginData, response: Response):
    if FAKE_USERS.get(data.username) != data.password:
        response.status_code = 401
        return {"message": "Invalid credentials"}
    token = str(uuid.uuid4())
    active_sessions[token] = data.username
    response.set_cookie(key="session_token", value=token, httponly=True, max_age=3600)
    return {"message": "Login successful"}


@router.get("/user")
def get_user(response: Response, session_token: Optional[str] = Cookie(default=None)):
    if session_token is None or session_token not in active_sessions:
        response.status_code = 401
        return {"message": "Unauthorized"}
    return FAKE_PROFILES[active_sessions[session_token]]


@router.post("/login_signed")
def login_signed(data: LoginData, response: Response):
    if FAKE_USERS.get(data.username) != data.password:
        response.status_code = 401
        return {"message": "Invalid credentials"}
    user_id = str(uuid.uuid4())
    user_store[user_id] = data.username
    token = signer.dumps(user_id)
    response.set_cookie(key="session_token", value=token, httponly=True, max_age=3600)
    return {"message": "Login successful", "user_id": user_id}


@router.get("/profile")
def get_profile(response: Response, session_token: Optional[str] = Cookie(default=None)):
    if session_token is None:
        response.status_code = 401
        return {"message": "Unauthorized"}
    try:
        user_id = signer.loads(session_token)
    except BadSignature:
        response.status_code = 401
        return {"message": "Unauthorized"}
    username = user_store.get(user_id)
    if not username:
        response.status_code = 401
        return {"message": "Unauthorized"}
    return FAKE_PROFILES[username]


def _make_session_token(user_id: str, ts: float) -> str:
    return session_signer.dumps({"uid": user_id, "ts": ts})


def _set_session_cookie(response: Response, user_id: str, ts: float):
    response.set_cookie(
        key="session_token",
        value=_make_session_token(user_id, ts),
        httponly=True,
        secure=False,
        max_age=SESSION_TTL,
    )


@router.post("/login_session")
def login_session(data: LoginData, response: Response):
    if FAKE_USERS.get(data.username) != data.password:
        response.status_code = 401
        return {"message": "Invalid credentials"}
    user_id = str(uuid.uuid4())
    session_users[user_id] = data.username
    _set_session_cookie(response, user_id, time.time())
    return {"message": "Login successful", "user_id": user_id}


@router.get("/profile_session")
def get_profile_session(response: Response, session_token: Optional[str] = Cookie(default=None)):
    if session_token is None:
        response.status_code = 401
        return {"message": "Unauthorized"}
    try:
        payload = session_signer.loads(session_token)
    except BadSignature:
        response.status_code = 401
        return {"message": "Invalid session"}
    user_id, last_ts = payload["uid"], payload["ts"]
    username = session_users.get(user_id)
    if not username:
        response.status_code = 401
        return {"message": "Invalid session"}
    elapsed = time.time() - last_ts
    if elapsed >= SESSION_TTL:
        response.status_code = 401
        return {"message": "Session expired"}
    renewed = elapsed >= RENEW_THRESHOLD
    if renewed:
        _set_session_cookie(response, user_id, time.time())
    return {
        **FAKE_PROFILES[username],
        "session_age_seconds": round(elapsed, 1),
        "cookie_renewed": renewed,
    }