from core.users.enums import UserRole
from tortoise.models import Model
from core.users.models import User


class IsStandardUser:
    
    @classmethod
    def has_permission(cls, user: User) -> bool:
        return user.role == UserRole.STANDARD
    
    @classmethod
    def has_object_permission(cls, object: Model, user: User) -> bool:
        if hasattr(object, 'user'):
            return cls.has_permission(user) and object.user.id == user.id
        else:
            return cls.has_permission(user) and object.id == user.id
    
    
class IsModerator:
    
    @classmethod
    def has_permission(cls, user: User) -> bool:
        return user.role == UserRole.MODERATOR