import time
from uuid import UUID

import bcrypt
import jwt
from cryptography.fernet import Fernet
from fastapi import HTTPException

from src.auth.config import config
from src.auth.schema.token import JWTToken, JWTTokenPayload

_f = Fernet(config.CRYPT_KEY)


def create_jwt_token(
    user_id: UUID,
    agent: str,
    key: bytes,
    expire_second: int = config.token_life_time,
) -> JWTToken:
    iss = "authserver"
    iat = int(time.time())
    exp = iat + expire_second
    payload = JWTTokenPayload(
        iss=iss, sub=str(user_id), exp=exp, iat=iat, ag=agent, ks=key
    )

    access_token = jwt.encode(
        payload.model_dump(), config.JWT_SECRET, algorithm="HS256"
    )

    return JWTToken(payload=payload, access_token=access_token)


def verify_jwt_token(token: str, agent: str) -> JWTTokenPayload:
    try:
        raw_payload = jwt.decode(
            token,
            config.JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_signature": True},
            issuer="auth",
        )
        print(f"\n\nagent: {agent}\n\n{raw_payload}\n\n\n")
        username: str = raw_payload.get("sub")
        if (
            username is None
            or raw_payload.get("ks") is None
            or raw_payload.get("ag") != agent
        ):
            raise jwt.InvalidTokenError("No 'sub' field in token")

        if (
            raw_payload.get("exp") is not None
            and raw_payload.get("exp") < int(time.time())
            or raw_payload.get("iat") is not None
        ):
            raise jwt.InvalidTokenError("Token expired")
        
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=401, detail=f"Invalid token: {exc}"
        ) from exc

    return JWTTokenPayload(**raw_payload)


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt(),
    ).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def encrypt_token(token: str) -> bytes:
    return _f.encrypt(token.encode("utf-8"))


def decrypt_token(token: bytes) -> str:
    return _f.decrypt(token).decode("utf-8")
