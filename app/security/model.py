from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/security/token")
