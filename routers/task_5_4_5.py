import re
from fastapi import APIRouter, Request, HTTPException, Response
from pydantic import BaseModel, field_validator
from datetime import datetime

router = APIRouter()

ACCEPT_LANG_RE = re.compile(
    r"^[a-zA-Z]{1,8}(-[a-zA-Z0-9]{1,8})?"
    r"(,\s*[a-zA-Z]{1,8}(-[a-zA-Z0-9]{1,8})?(;q=[01](\.\d{1,3})?)?)* *$"
)


@router.get("/headers")
def get_headers(request: Request):
    ua = request.headers.get("user-agent")
    al = request.headers.get("accept-language")
    if not ua:
        raise HTTPException(status_code=400, detail="Missing header: User-Agent")
    if not al:
        raise HTTPException(status_code=400, detail="Missing header: Accept-Language")
    if not ACCEPT_LANG_RE.match(al):
        raise HTTPException(status_code=400, detail="Invalid Accept-Language format")
    return {"User-Agent": ua, "Accept-Language": al}


class CommonHeaders(BaseModel):
    user_agent: str
    accept_language: str

    @field_validator("accept_language")
    @classmethod
    def validate_accept_language(cls, v: str) -> str:
        if not ACCEPT_LANG_RE.match(v):
            raise ValueError("Invalid Accept-Language format")
        return v

    @classmethod
    def from_request(cls, request: Request) -> "CommonHeaders":
        ua = request.headers.get("user-agent", "")
        al = request.headers.get("accept-language", "")
        if not ua:
            raise HTTPException(status_code=400, detail="Missing header: User-Agent")
        if not al:
            raise HTTPException(status_code=400, detail="Missing header: Accept-Language")
        return cls(user_agent=ua, accept_language=al)


@router.get("/info")
def info(request: Request, response: Response):
    h = CommonHeaders.from_request(request)
    response.headers["X-Server-Time"] = datetime.now().isoformat(timespec="seconds")
    return {
        "message": "Добро пожаловать! Ваши заголовки успешно обработаны.",
        "headers": {
            "User-Agent": h.user_agent,
            "Accept-Language": h.accept_language,
        },
    }