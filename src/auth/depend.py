from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from src.auth.util import verify_jwt_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_currnet_user(token: str = Depends(oauth2_scheme)):
    jwt_payload = verify_jwt_token(token)
    