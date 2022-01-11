import pydantic
from uuid import UUID
from typing import Optional
from .enums import *
from common.validators import *
from datetime import datetime


class UserCreateSchema(pydantic.BaseModel):
    username: pydantic.constr(strip_whitespace=True, min_length=6, max_length=20)
    email: pydantic.EmailStr
    password: pydantic.constr(strip_whitespace=True, min_length=6, max_length=30)
    gender: UserGender
    
    _username_is_alphanumeric: classmethod = alphanumeric_validator("username")
    

class UserEditSchema(pydantic.BaseModel):
    username: pydantic.constr(strip_whitespace=True, min_length=6, max_length=20)
    bio: Optional[pydantic.constr(strip_whitespace=True, min_length=1, max_length=300)]
    email: pydantic.EmailStr
    gender: UserGender
    
    _username_is_alphanumeric: classmethod = alphanumeric_validator("username")
    
    
class UserGetListSchema(pydantic.BaseModel):
    id: UUID
    username: str
    role: UserRole
        
        
class UserGetProfileSchema(UserGetListSchema):
    bio: Optional[str]
    date_joined: datetime
    gender: UserGender
    
    
class LoginResponse(pydantic.BaseModel):
    access_token: str
    token_type: str
    user: UserGetListSchema
    
    
class LoginRequest(pydantic.BaseModel):
    username: str
    password: str
    

class PassResetCodeRequestSchema(pydantic.BaseModel):
    email: pydantic.EmailStr
    
    
class PasswordResetSchema(pydantic.BaseModel):
    code: UUID
    password: pydantic.constr(strip_whitespace=True, min_length=6, max_length=30)
    
    def dict(self):
        return {
            "code": str(self.code),
            "password": self.password
        }
    

class PasswordResetSuccessResponse(pydantic.BaseModel):
    detail: str = "Password reset successfully"
    
    
class UserSession(pydantic.BaseModel):
    id: UUID
    username: str
    role: UserRole
    token: str