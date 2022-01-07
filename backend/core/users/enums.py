from enum import Enum


class UserRole(str,Enum):
    STANDARD = 'standard'
    MODERATOR = 'moderator'
    
    
class UserGender(str,Enum):
    MALE = 'male'
    FEMALE = 'female'