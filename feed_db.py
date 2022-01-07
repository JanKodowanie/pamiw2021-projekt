from core.users.models import User
from core.users.utils.hash import Hash
from core.blog.models import Post, Tag
from core.users.enums import UserRole, UserGender


async def feed_db():
    # create test moderator
    test_moderator = {
        'username': 'moderator',
        'password': Hash().hash_password('moderator'),
        'email': 'moderator@example.com',
        'gender': UserGender.MALE,
        'role': UserRole.MODERATOR
    }
    user = await User.create(**test_moderator)
    tag = await Tag.create(name="hello", popularity=1)
    
    test_post = {
        'creator': user,
        'content': 'Cześć wszystkim! Miło mi powitać was w serwisie MicroSociety! #hello'
    }
    
    post = await Post.create(**test_post)
    await post.tags.add(tag)
    await post.save()