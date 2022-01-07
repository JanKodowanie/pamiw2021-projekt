from tortoise import fields, models
from typing import List
from tortoise.signals import post_delete
from common.files.file_manager import FileManager
import re


class Tag(models.Model):
    name = fields.CharField(max_length=30, pk=True)
    date_created = fields.DatetimeField(auto_now_add=True)
    popularity = fields.IntField(default=0)
    posts: fields.ManyToManyRelation["Post"]
    
    class Meta:
        ordering = ["-popularity"]
        
    
class Post(models.Model):
    creator = fields.ForeignKeyField(model_name="models.User", related_name="posts")
    content = fields.TextField(max_length=500)
    picture_url = fields.CharField(max_length=300, null=True)
    picture_path = fields.CharField(max_length=300, null=True)
    date_created = fields.DatetimeField(auto_now_add=True)
    tags: fields.ManyToManyRelation["Tag"] \
        = fields.ManyToManyField(model_name='models.Tag', related_name='posts',
                    null=True)
    comments: fields.ManyToManyRelation["Comment"] 
        
    class Meta:
        ordering = ["-date_created"]
            
    async def extract_hashtags(self) -> List[str]:
        regex = "#(\w+)"
        hashtag_list = re.findall(regex, self.content)
        
        return hashtag_list
 
 
class Comment(models.Model):
    creator = fields.ForeignKeyField(model_name="models.User")
    post = fields.ForeignKeyField(model_name="models.Post", related_name="comments")
    content = fields.TextField(max_length=300)
    date_created = fields.DatetimeField(auto_now_add=True)
        
    class Meta:
        ordering = ["date_created"] 
        
        
class Like(models.Model):
    creator = fields.ForeignKeyField(model_name="models.User")
    post = fields.ForeignKeyField(model_name="models.Post")
 
    
@post_delete(Post)
async def delete_post_picture(sender, instance, using_db) -> None:
    if instance.picture_path:
        FileManager().delete_file(instance.picture_path)