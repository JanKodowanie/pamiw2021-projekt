import pydantic
from fastapi import UploadFile
from core.users.schemas import UserGetListSchema
from typing import Optional, List
from uuid import UUID
from common.date_converter import *


class TagGetBasicSchema(pydantic.BaseModel):
    name: str
    

class TagGetFullSchema(TagGetBasicSchema):
    name: str
    date_created: str
    popularity: int
    
    
class LikeGetSchema(pydantic.BaseModel):
    creator_id: UUID


class PostCreateSchema(pydantic.BaseModel):
    content: pydantic.constr(strip_whitespace=True, min_length=1, max_length=500)
    picture: Optional[UploadFile]
    
     
class PostGetSchema(pydantic.BaseModel):
    id: int
    creator: UserGetListSchema
    content: str 
    picture_url: Optional[str]
    date_created: str
    tags: Optional[List[TagGetBasicSchema]]
    likes: Optional[List[LikeGetSchema]]
    
    
class PostListSchema(pydantic.BaseModel):
    posts: Optional[List[PostGetSchema]]
    
    def dict(self):
        result = super().dict().get('posts')
        for post in result:
            post['date_created'] = DateConverter.convert_str_to_datetime(post['date_created'])
            
        return result