import json
from fastapi import Depends, Cookie
from .schemas import UserSession
from typing import Optional, Dict


async def get_user_session(token: Optional[str] = Cookie(None), 
                           user_data: Optional[str] = Cookie(None)) -> Optional[UserSession]:
    if not token or not user_data:
        return None
    user_data = json.loads(user_data)
    user_data['token'] = token
    session = UserSession(**user_data)
    
    return session