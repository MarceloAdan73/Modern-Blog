"""
Security helpers: JWT creation/validation and current-user dependency.

FASE 2 (2026-08-14): auth real reemplaza al mock-token.
- SECRET_KEY: leer de env JWT_SECRET (obligatorio en produccion).
  En desarrollo se usa un fallback local con WARNING (nunca para produccion).
- Token: JWT firmado HS256, payload {"sub": user_id}, expiracion 7 dias.
"""

import os
import warnings
import contextvars
from datetime import datetime, timedelta

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from database import get_db
from models.models import User

# --- Current request (para GraphQL) ---
# WORKAROUND: en strawberry 0.324 un context_getter con parametro request
# rompe la validacion del body (422 "missing query"). Un context_getter sin
# argumentos funciona. Capturamos la request en una contextvar via middleware
# y el context_getter la lee de ahi.
_current_request: contextvars.ContextVar = contextvars.ContextVar(
    "current_request", default=None
)


def get_current_request():
    """Devuelve la request HTTP actual (seteada por el middleware)."""
    return _current_request.get()


def set_current_request(request) -> contextvars.Token:
    return _current_request.set(request)


def reset_current_request(token: contextvars.Token) -> None:
    _current_request.reset(token)

# --- Config ---
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 7 * 24 * 60  # 7 dias (demo: no molestar con re-login)

SECRET_KEY = os.environ.get("JWT_SECRET", "")
if not SECRET_KEY:
    # Fallback SOLO para desarrollo local. En produccion (Render) se setea JWT_SECRET.
    SECRET_KEY = "dev-only-secret-change-me-in-production"
    warnings.warn(
        "JWT_SECRET no esta definido. Usando fallback de desarrollo. "
        "Configurar JWT_SECRET en produccion.",
        RuntimeWarning,
    )

# --- Token creation ---
def create_access_token(user_id: int) -> str:
    """Crea un JWT valido por 7 dias para el usuario."""
    payload = {
        "sub": str(user_id),
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> int | None:
    """Decodifica el JWT y devuelve el user_id (None si invalido/vencido)."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        return None


# --- FastAPI dependency ---
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """FastAPI dependency: valida el Bearer token y devuelve el User (o 401)."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
