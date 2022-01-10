import pydantic
from .models import *
from core.users.schemas import UserGetListSchema
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from tortoise.contrib.pydantic import PydanticModel


class TagGetBasicSchema(pydantic.BaseModel):
    name: str
    
    class Config:
        orm_mode = True


class TagGetFullSchema(TagGetBasicSchema):
    name: str
    date_created: datetime
    popularity: int
    
    
class LikeGetSchema(pydantic.BaseModel):
    creator_id: UUID
    
    class Config:
        orm_mode = True


class CommentCreateSchema(pydantic.BaseModel):
    content: pydantic.constr(strip_whitespace=True, min_length=1, max_length=300)
    
    
class CommentUpdateSchema(CommentCreateSchema):
    pass    


class CommentGetSchema(pydantic.BaseModel):
    id: int
    post_id: int
    content: str
    creator: UserGetListSchema
    date_created: datetime
    
    class Config:
        orm_mode = True
    

class PostCreateSchema(pydantic.BaseModel):
    content: pydantic.constr(strip_whitespace=True, min_length=1, max_length=500)
     
  
class PostGetListSchema(PydanticModel):
    id: int
    creator: UserGetListSchema
    content: str 
    picture_url: Optional[str]
    date_created: datetime
    tags: Optional[List[TagGetBasicSchema]]
    likes: Optional[List[LikeGetSchema]]
    
    class Config:
        orm_mode = True
    
    
class PostGetDetailsSchema(PostGetListSchema):
    comments: Optional[List[CommentGetSchema]]
    
    class Config:
        orm_mode = True