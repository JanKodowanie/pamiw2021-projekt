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
    
    test_standard = {
        'username': 'standard',
        'password': Hash().hash_password('standard'),
        'email': 'standard@example.com',
        'gender': UserGender.FEMALE,
        'role': UserRole.STANDARD
    }
    
    if not await User.filter(username='moderator').exists():
        user = await User.create(**test_moderator)
        tag = await Tag.create(name="hello", popularity=1)
        
        test_post = {
            'creator': user,
            'content': 'Cześć wszystkim! Miło mi powitać was w serwisie MicroSociety! #hello'
        }
        
        post = await Post.create(**test_post)
        await post.tags.add(tag)
        await post.save()
        
    if not await User.filter(username='standard').exists():
        user = await User.create(**test_standard)
        tag1, _ = await Tag.get_or_create(name="hello")
        tag1.popularity += 1
        await tag1.save()
        tag2 = await Tag.create(name="programowanie", popularity=1)
        tag3 = await Tag.create(name="python", popularity=1)
        
        test_post1 = {
            'creator': user,
            'content': 'Cześć! Bardzo fajny serwis! #hello'
        }
        
        post1 = await Post.create(**test_post1)
        await post1.tags.add(tag1)
        await post1.save()
        
        test_post2 = {
            'creator': user,
            'content': 'Szukam dobrej książki do nauki Pythona.\nJakieś propozycje?\n#programowanie #python'
        }
        
        post2 = await Post.create(**test_post2)
        await post2.tags.add(tag2)
        await post2.tags.add(tag3)
        await post2.save()