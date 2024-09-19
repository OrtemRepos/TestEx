from pydantic import BaseModel


class JWTTokenPayload(BaseModel):
    iss: str
    sub: str
    exp: int
    iat: int
    ag: str
    ks: str


class JWTToken(BaseModel):
    payload: JWTTokenPayload
    access_token: str


class RefreshToken(BaseModel):
    refresh_token: str
