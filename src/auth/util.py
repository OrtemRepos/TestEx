import time
from uuid import UUID

import bcrypt
import jwt
from cryptography.fernet import Fernet
from fastapi import HTTPException

from src.auth.schema.token import JWTToken, JWTTokenPayload
from src.config import config

_f = Fernet(config.CRYPT_KEY)


def create_jwt_token(
    user_id: UUID,
    agent: str,
    key: str,
    expire_second: int = config.token_life_time,
    iss: str = "authserver",
) -> JWTToken:
    iss = iss
    iat = int(time.time())
    exp = iat + expire_second
    payload = JWTTokenPayload(
        iss=iss, sub=str(user_id), exp=exp, iat=iat, ag=agent, ks=key
    )

    access_token = jwt.encode(
        payload.model_dump(), config.JWT_SECRET, algorithm="HS256"
    )

    return JWTToken(payload=payload, access_token=access_token)


def verify_jwt_token(
    token: str, agent: str, iss: str = "authserver"
) -> JWTTokenPayload:
    try:
        raw_payload = jwt.decode(
            token,
            config.JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_signature": True},
            issuer=iss,
        )
        username: str = raw_payload.get("sub")
        if (
            username is None
            or raw_payload.get("ks") is None
            or raw_payload.get("ag") is None
            or raw_payload.get("iat") is None
            or raw_payload.get("exp") is None
        ):
            raise jwt.InvalidTokenError("Invalid token")

        if (
            raw_payload.get("exp") < int(time.time())
            or raw_payload.get("ag") != agent
        ):
            raise jwt.InvalidTokenError("Token expired or invalid agent")

    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=401, detail=f"Invalid token:\n\t {exc}"
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


def encrypt_token(token: str) -> str:
    return _f.encrypt(token.encode("utf-8")).decode("utf-8")


def decrypt_token(token: str) -> str:
    return _f.decrypt(token.encode("utf-8")).decode("utf-8")
