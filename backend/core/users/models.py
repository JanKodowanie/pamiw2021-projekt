from tortoise import fields, models
from datetime import datetime, timezone, timedelta
from .enums import *


class User(models.Model):
    id = fields.UUIDField(pk=True)
    username = fields.CharField(max_length=20, unique=True)
    email = fields.CharField(max_length=60, unique=True)
    password = fields.CharField(max_length=128)
    date_joined = fields.DatetimeField(auto_now_add=True)
    bio = fields.TextField(max_length=300, null=True)
    gender = fields.CharEnumField(enum_type=UserGender)
    role = fields.CharEnumField(enum_type=UserRole, default=UserRole.STANDARD)
    
    class Meta:
        ordering = ["username"]
        
        
class PasswordResetCode(models.Model):
    code = fields.UUIDField(pk=True)
    user = fields.OneToOneField('models.User', related_name='reset_code')
    exp = fields.DatetimeField(
        default=datetime.now(timezone.utc) + timedelta(hours=24))