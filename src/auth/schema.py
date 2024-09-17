import json

from pydantic import BaseModel, model_serializer


class JWTTokenPayload(BaseModel):
    iss: str
    sub: str
    exp: int
    iat: int


class JWTToken(BaseModel):
    payload: JWTTokenPayload
    access_token: str

    @model_serializer
    def ser_model_dump(self) -> str:
        model_data = {
            "payload": self.payload.model_dump(),
            "access_token": self.access_token,
        }
        data = json.dumps(model_data)
        return data
