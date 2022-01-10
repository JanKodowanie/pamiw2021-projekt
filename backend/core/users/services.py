from typing import List, Dict, Optional
from fastapi import Depends
from .models import *
from .exceptions import *
from .schemas import *
from .enums import UserRole
from .utils.hash import Hash
from uuid import UUID
from tortoise.exceptions import DoesNotExist
from common.emails.email_manager import EmailManager


class UserService:
    
    def __init__(self, email_manager: EmailManager = Depends()):
        self.hash = Hash()
        self.email_manager = email_manager
        
    async def register(self, data: UserCreateSchema, 
                               role: UserRole = UserRole.STANDARD) -> User:
        data_dict = data.dict()
        hashed_password = self.hash.hash_password(data_dict.pop('password'))    
        
        error_fields = []
        email_taken = await self._check_if_email_is_taken(data.email)
        username_taken = await self._check_if_username_is_taken(data.username)
        
        if email_taken:
            error_fields.append('email')
        if username_taken:
            error_fields.append('username')
        
        if error_fields:
            raise CredentialsAlreadyTaken('Credentials already taken',
                    detail=self._compose_credentials_taken_error(error_fields))
        
        user = await User.create(**data_dict, password=hashed_password, role=role)
        await self.email_manager.send_user_greetings_email(user.username, user.email)
        return user
        
    async def get_by_id(self, uuid: UUID) -> User:
        try:
            user = await User.get(id=uuid)
        except DoesNotExist:
            raise AccountNotFound()
        
        return user
    
    async def get_by_email(self, email: str) -> User:
        try:
            user = await User.get(email=email)
        except DoesNotExist:
            raise AccountNotFound()
        
        return user
    
    async def delete(self, user: User, send_email: bool = True) -> None:
        username = user.username
        email = user.email
        await user.delete()
        if send_email:
            await self.email_manager.send_user_farewell_email(username, email)
        
    async def get_list(self, filters: Optional[dict] = None) -> List[User]:
        if not filters:
            return await User.all()
       
        return await User.filter(**filters)
        
    async def edit(self, user: User, data: UserEditSchema) -> User:
        error_fields = []
        if data.email and user.email != data.email:
            email_taken = await self._check_if_email_is_taken(data.email)
            if email_taken:
                error_fields.append('email')
                
        if data.username and user.username != data.username:
            username_taken = await self._check_if_username_is_taken(data.username)
            if username_taken:
                error_fields.append('username')
                
        if error_fields:
            raise CredentialsAlreadyTaken('Credentials already taken',
                    detail=self._compose_credentials_taken_error(error_fields))
        
        if data.username:
            user.username = data.username
        if data.email:
            user.email = data.email
        if data.gender != user.gender:
            user.gender = data.gender
        if data.bio != user.bio:
            user.bio = data.bio
            
        await user.save()            
        return user

    async def change_password(self, user: User, new_password: str):
        user.password = self.hash.hash_password(new_password)
        await user.save()

    async def _check_if_email_is_taken(self, email: str) -> bool:
        result = await User.filter(email=email).exists()
        return result
    
    async def _check_if_username_is_taken(self, username: str) -> bool:
        result = await User.filter(username=username).exists()
        return result
    
    def _compose_credentials_taken_error(self, fields: List[str]):
        error_msg = []
        if 'email' in fields:
            error_msg.append('Założono już konto na ten adres email.')
        if 'username' in fields:
            error_msg.append('Nazwa użytkownika jest zajęta.')
        
        return self._compose_error_messages(fields, error_msg)
            
    def _compose_error_messages(self, field_names: List[str], messages: List[str]) -> Dict[str, str]:
        errors = {}
        
        for i in range(len(field_names)):
            errors[field_names[i]] = messages[i]
            
        return errors
    
    
class PasswordResetService:
    def __init__(self, email_manager: EmailManager = Depends(), user_service: UserService = Depends()):
        self.email_manager = email_manager
        self.user_service = user_service
    
    async def create_code(self, user: User):
        await PasswordResetCode.filter(user=user).delete()
        instance = await PasswordResetCode.create(user=user)
        await self.email_manager.send_password_reset_email(user.username, user.email, instance.code)
    
    async def get_code(self, code: UUID) -> PasswordResetCode:
        try:
            code = await PasswordResetCode.get(code=code).prefetch_related('user')
        except DoesNotExist:
            raise PasswordResetCodeNotFound()
        
        return code
    
    async def reset_password(self, code: PasswordResetCode, new_pass: str):
        if code.exp < datetime.now(timezone.utc):
            await code.delete()
            raise PasswordResetCodeExpired()
        
        await self.user_service.change_password(code.user, new_pass)
        await code.delete()