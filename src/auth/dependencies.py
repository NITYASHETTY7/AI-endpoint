from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

SECRET_KEY = "a-string-secret-at-least-256-bits-long" #to validate the token that it is not tampered with
# This should be kept secret and not hardcoded in production code
ALGORITHM = "HS256"

# OAuth2 scheme for token-based authentication
#extract token from the request/HTTP header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


async def get_user_identifier(token: Optional[str] = Depends(oauth2_scheme)):
    if token is None:                  # If no token is provided, treat as unauthenticated user/global unauthenticated user so ppl can try it out free,before becoming an user
        return "global_unauthenticated_user"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")  # 'sub' is the subject of the token, typically the user ID
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username

