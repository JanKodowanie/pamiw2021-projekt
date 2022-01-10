from .models import *
from .schemas import *
from .exceptions import *
from core.users.models import User
from fastapi import Depends, UploadFile
from tortoise.exceptions import DoesNotExist
from common.files.file_manager import FileManager


class TagService:
    
    async def create_tags_from_post(self, post: Post):
        tag_names = await post.extract_hashtags()
        for name in tag_names:
            tag = await Tag.get_or_create(name=name.lower())
            tag = tag[0]
            tag.popularity += 1
            await tag.save()
                
            await post.tags.add(tag)
            await post.save()
    
    async def decrease_post_tags_popularity(self, post: Post):
        for tag in post.tags:
            tag.popularity -= 1
            if tag.popularity != 0:
                await tag.save()
            else:
                await tag.delete()
    
    async def get_tag_list(self) -> List[Tag]:
        return await Tag.all()
    
    async def get_posts_in_tag(self, tag_name: str) -> List[Post]:
        try:
            tag = await Tag.get(name=tag_name)
        except DoesNotExist:
            raise TagNotFound()
        await tag.fetch_related('posts')
        return await tag.posts.all().prefetch_related('tags', 'likes')


class PostService:
    
    def __init__(self, tag_service: TagService = Depends()):
        self.tag_service = tag_service

    async def create(self, creator: User, 
                               content: str, picture: Optional[UploadFile]) -> Post:
        
        data = PostCreateSchema(content=content).dict()
        if picture:
            try:
                FileManager().validate_file(picture, ['jpg', 'jpeg', 'png'])
            except Exception as e:
                error = {'picture': str(e)}
                raise InvalidPostData('Uploaded file is not a valid picture', detail=error)   
                
        instance = await Post.create(creator=creator, **data)
        if picture:
            path, url = FileManager().upload_file(picture, instance.id, 'post_pics', ['jpg', 'jpeg', 'png'])
            instance.picture_path = path
            instance.picture_url = url
            await instance.save()
        
        await self.tag_service.create_tags_from_post(instance)
        await instance.fetch_related('creator', 'tags', 'comments', 'likes')
        return instance
    
    async def get(self, id: int) -> Post:
        try:
            instance = await Post.get(id=id)
        except DoesNotExist:
            raise PostNotFound()
        
        await instance.fetch_related('creator', 'tags', 'comments', 'likes')
        return instance

    async def edit(self, instance: Post, 
                        new_content: Optional[str], delete_picture: bool, new_picture: Optional[UploadFile]) -> Post:
        if new_picture:
            try:
                path, url = FileManager().upload_file(new_picture, instance.id, 'post_pics', ['jpg', 'jpeg', 'png'])
                instance.picture_path = path
                instance.picture_url = url
                await instance.save()
            except Exception as e:
                error = {'picture': str(e)}
                raise InvalidPostData('Uploaded file is not a valid picture', detail=error)
        elif delete_picture:
            await self.delete_picture(instance)
            
        if new_content:
            await self.tag_service.decrease_post_tags_popularity(instance)
            await instance.tags.clear()
            instance.content = PostCreateSchema(content=new_content).content
            await instance.save()
            await self.tag_service.create_tags_from_post(instance)
        
        await instance.fetch_related('creator', 'tags', 'comments', 'likes')
        return instance
    
    async def delete(self, instance: Post):
        await self.tag_service.decrease_post_tags_popularity(instance)
        await instance.delete()

    async def get_list(self, filters: dict = None) -> List[Post]:
        if not filters:
            posts = await Post.all().prefetch_related('creator', 'tags', 'likes')
        else:
            posts = await Post.filter(**filters).prefetch_related('creator', 'tags', 'likes')
        return posts
    
    async def bulk_delete(self, filters: dict = None):
        posts = await Post.filter(**filters).prefetch_related('tags', 'likes')
        for post in posts:
            await self.delete(post)
            
    async def delete_picture(self, instance: Post):
        if instance.picture_path:
            FileManager().delete_file(instance.picture_path)
        instance.picture_path = None
        instance.picture_url = None
        await instance.save()
        
        
class LikeService:
        
    async def create(self, post: Post, user: User):
        if await Like.filter(creator=user, post=post).exists():
            raise LikeAlreadyCreated()
        await Like.create(creator=user, post=post)
        await post.fetch_related('likes')
    
    async def delete(self, post: Post, user: User):
        await Like.filter(creator=user, post=post).delete()
        await post.fetch_related('likes')