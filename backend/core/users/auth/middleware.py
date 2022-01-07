import settings
from fastapi import Depends, HTTPException
from datetime import datetime, timedelta, timezone
from jose import jwt
from .exceptions import *
from ..schemas import *
from ..exceptions import AccountNotFound
from ..services import UserService
from ..models import User
from ..schemas import UserDataSchema
from ..utils.hash import Hash
from fastapi.security import OAuth2PasswordBearer


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user-management/login")


class TokenManager:

    def create_token(self, account: User):
        to_encode = self._create_jwt_data(account)
        data = UserDataSchema(**to_encode)
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt, data

    def decode_token(self, token: str) -> UserDataSchema:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            token_data = UserDataSchema(**payload)
        except Exception:
            raise MalformedAccessToken()
        
        if token_data.exp < datetime.now(timezone.utc):
            raise AccessTokenExpired()
        
        return token_data
            
    def _create_jwt_data(self, account: User) -> dict:
        iat = datetime.now(timezone.utc)
        exp = iat + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode = {
            'sub': str(account.id),
            'username': account.username,
            'role': account.role.value,
            'iat': iat,
            'exp': exp
        }
        
        return to_encode
    

class AuthHandler:
    
    async def authenticate_user(self, email, password) -> TokenSchema:
        try:
            user = await UserService().get_by_email(email)
        except AccountNotFound:
            raise InvalidCredentials()
        
        if not Hash().verify(user.password, password):
            raise InvalidCredentials()
        
        access_token, data = TokenManager().create_token(user)
        token_type = 'Bearer'
        
        return TokenSchema(access_token=access_token, token_type=token_type, data=data)
    
    @classmethod
    async def get_user_from_token(cls, token: str = Depends(oauth2_scheme)) -> User:
        try:
            data = TokenManager().decode_token(token)
            user = await UserService().get_by_id(data.sub)
        except Exception as e:
            raise HTTPException(401, detail=e.detail)
        
        return user