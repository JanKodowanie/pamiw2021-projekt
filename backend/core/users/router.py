from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from .schemas import *
from .exceptions import *
from .services import *
from .auth.middleware import AuthHandler
from .auth.exceptions import InvalidCredentials
from core.users.auth.permissions import *
from common.responses import *
from typing import List
from uuid import UUID


router = APIRouter(
    prefix="/user-management",
    tags=['User management'],
    responses= {
        status.HTTP_401_UNAUTHORIZED: NotAuthenticatedResponse().dict(),
        status.HTTP_403_FORBIDDEN: ForbiddenResponse().dict(),
        status.HTTP_404_NOT_FOUND: NotFoundResponse().dict()
    }
)


@router.post(
    '/user', 
    response_model=UserGetProfileSchema,
    status_code=status.HTTP_201_CREATED
)
async def register_new_user(
    request: UserCreateSchema, 
    service: UserService = Depends()
):
    try:
        user = await service.register(request)
    except CredentialsAlreadyTaken as e:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.detail) 
    
    return user


@router.get(
    '/user', 
    response_model=UserGetProfileSchema,
    status_code=status.HTTP_200_OK
)
async def get_current_user_profile(
    user: User = Depends(AuthHandler.get_user_from_token)
):
    return user


@router.put(
    '/user', 
    response_model=UserGetProfileSchema,
    status_code=status.HTTP_200_OK
)
async def edit_current_user_profile(
    request: UserEditSchema, 
    service: UserService = Depends(),
    user: User = Depends(AuthHandler.get_user_from_token)
):
    try:
        user = await service.edit(user, request)
    except CredentialsAlreadyTaken as e:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.details) 
    
    return user


@router.delete(
    '/user', 
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_current_user(
    service: UserService = Depends(),
    user: User = Depends(AuthHandler.get_user_from_token)
):
    await service.delete(user)
    return 


@router.get(
    '/users', 
    response_model=List[UserGetListSchema],
    status_code=status.HTTP_200_OK
)
async def get_user_list(
    service: UserService = Depends()
):
    users = await service.get_list()
    return users


@router.get(
    '/user/{id}', 
    response_model=UserGetProfileSchema,
    status_code=status.HTTP_200_OK
)
async def get_user_profile(
    id: UUID, 
    service: UserService = Depends()
):
    try:
        user = await service.get_by_id(id)
    except AccountNotFound as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=NotFoundResponse().detail)
    return user


@router.delete(
    '/user/{id}', 
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_user_as_moderator(
    id: UUID, 
    service: UserService = Depends(),
    user: User = Depends(AuthHandler.get_user_from_token)
):
    if not IsModerator.has_permission(user):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=ForbiddenResponse().detail)
    
    try:
        user_to_delete = await service.get_by_id(id)
    except AccountNotFound:
        return
    
    service.delete(user_to_delete, False)


@router.post(
    '/login',
    response_model=LoginResponse,
    status_code=status.HTTP_201_CREATED
)
async def login(
    request: OAuth2PasswordRequestForm = Depends(), 
    auth_handler: AuthHandler = Depends()
):
    try:
        token = await auth_handler.authenticate_user(email=request.username, 
                                                     password=request.password)
    except InvalidCredentials as e:   
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=e.detail)
    return token


@router.post(
    '/password-reset-code',
    status_code=status.HTTP_200_OK,
    response_model=OkResponse
)
async def get_password_reset_code(
    request: PassResetCodeRequestSchema,
    password_reset_service: PasswordResetService = Depends(),
    user_service: UserService = Depends()
):
    response = OkResponse(detail="Email z linkiem do resetu hasła został wysłany.")
    try:
        user = await user_service.get_by_email(request.email)
    except AccountNotFound:
        return response
    
    await password_reset_service.create_code(user)
    return response
    
    
@router.patch(
    '/user/reset-password',
    status_code=status.HTTP_200_OK
)
async def reset_password(
    request: PasswordResetSchema,
    password_reset_service: PasswordResetService = Depends()
):
    try:
        code = await password_reset_service.get_code(request.code)
    except PasswordResetCodeNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=e.detail)
       
    try:
        await password_reset_service.reset_password(code, request.password)
    except PasswordResetCodeExpired as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=e.detail)
    
    return PasswordResetSuccessResponse()