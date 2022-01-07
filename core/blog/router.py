from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, status
from typing import List
from uuid import UUID
from .schemas import *
from .services import *
from .exceptions import *
from common.responses import *
from core.users.models import User
from core.users.auth.permissions import *
from core.users.auth.middleware import AuthHandler


router = APIRouter(
    prefix="/blog",
    tags=['Blog'],
    responses= {
        status.HTTP_401_UNAUTHORIZED: NotAuthenticatedResponse().dict(),
        status.HTTP_403_FORBIDDEN: ForbiddenResponse().dict(),
        status.HTTP_404_NOT_FOUND: NotFoundResponse().dict()
    }
)


@router.post(
    '/post',
    response_model=PostGetDetailsSchema,
    status_code=status.HTTP_201_CREATED
)
async def create_post(
    content: str = Form(..., max_length=500),
    picture: UploadFile = File(None), 
    service: PostService = Depends(),
    user: User = Depends(AuthHandler.get_user_from_token)
):
    try:
        instance = await service.create(user, content, picture)
    except InvalidPostData as e:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.detail)
    
    return instance


@router.get(
    '/post/{id}',
    response_model = PostGetDetailsSchema,
    status_code=status.HTTP_200_OK
)
async def get_post_details(
    id: int,
    service: PostService = Depends()
):
    try:
        instance = await service.get(id)
    except PostNotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=NotFoundResponse().detail)

    return instance


@router.delete(
    '/post/{id}',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_post(
    id: int, 
    service: PostService = Depends(),
    user: User = Depends(AuthHandler.get_user_from_token)
):
    try:
        instance = await service.get(id)
    except PostNotFound:
        return
    
    if not IsBlogUser.has_object_permission(instance, user) \
                and not IsModerator.has_permission(user):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=ForbiddenResponse().detail)

    await service.delete(instance)
    
    
@router.patch(
    '/post/{id}',
    response_model = PostGetDetailsSchema,
    status_code=status.HTTP_200_OK
)
async def edit_post(
    id: int,
    content: str = Form(None, max_length=500),
    picture: UploadFile = File(None), 
    delete_picture: bool = Form(False),
    service: PostService = Depends(),
    user: User = Depends(AuthHandler.get_user_from_token)
):
    try:
        instance = await service.get(id)
    except PostNotFound as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=NotFoundResponse().detail)
    
    if not IsBlogUser.has_object_permission(instance, user):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=ForbiddenResponse().detail)

    try:
        instance = await service.edit(instance, content, delete_picture, picture)
    except InvalidPostData as e:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.detail)
    
    return instance


@router.post(
    '/post/{id}/like',
    response_model = PostGetDetailsSchema,
    status_code=status.HTTP_200_OK
)
async def create_post_like(
    id: int,
    like_service: LikeService = Depends(),
    post_service: PostService = Depends(),
    user: User = Depends(AuthHandler.get_user_from_token)
):
    try:
        post = await post_service.get(id)
    except PostNotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=NotFoundResponse().detail)
    
    try:
        await like_service.create(post, user)
    except LikeAlreadyCreated as e:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.detail)

    return post


@router.delete(
    '/post/{id}/like',
    response_model = PostGetDetailsSchema,
    status_code=status.HTTP_200_OK
)
async def create_post_like(
    id: int,
    like_service: LikeService = Depends(),
    post_service: PostService = Depends(),
    user: User = Depends(AuthHandler.get_user_from_token)
):
    try:
        post = await post_service.get(id)
    except PostNotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=NotFoundResponse().detail)
    
    await like_service.delete(post, user)
    return post


@router.get(
    '/posts',
    response_model=List[PostGetListSchema]
)
async def get_post_list(
    service: PostService = Depends()
):
    return await service.get_list()


@router.get(
    '/posts/{user_id}',
    response_model=List[PostGetListSchema]
)
async def get_posts_by_user_id(
    user_id: UUID, 
    service: PostService = Depends()
):
    filters = {
        "creator_id": user_id
    }
    return await service.get_list(filters)


@router.get(
    '/tags',
    response_model=List[TagGetFullSchema]
)
async def get_tag_list(
    service: TagService = Depends()
):
    return await service.get_tag_list()


@router.get(
    '/tag/{name}',
    response_model=List[PostGetListSchema]
)
async def get_posts_in_tag(
    name: str, 
    service: TagService = Depends()
):
    try:
        posts = await service.get_posts_in_tag(name)
    except TagNotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=NotFoundResponse().detail)
    
    return posts