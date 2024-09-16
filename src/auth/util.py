import time
from fastapi import HTTPException
import passlib  # type: ignore
import jwt
from src.auth.schema import JWTToken, JWTTokenPayload
from src.auth.config import config


def create_jwt_token(user_id: str, expire_second: int = 3600) -> JWTToken:
    iss = "auth"
    iat = int(time.time())
    exp = iat + expire_second
    payload = JWTTokenPayload(iss=iss, sub=user_id, exp=exp, iat=iat)

    access_token = jwt.encode(
        payload.model_dump(), config.JWT_SECRET, algorithm="HS256"
    )

    return JWTToken(payload=payload, access_token=access_token)


def verify_jwt_token(token: str) -> JWTTokenPayload:
    try:
        raw_payload = jwt.decode(
            token,
            config.JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_signature": True},
            issuer="auth",
        )
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail=f"Invalid token: {exc}")

    return JWTTokenPayload(**raw_payload)


pwd_context = passlib.context.CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password.encode("utf-8"))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )
