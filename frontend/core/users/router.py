import httpx
import settings
from fastapi import APIRouter, HTTPException, Form, Request, status, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from common.responses import *
from .schemas import *
from .auth import *
from core.blog.schemas import PostListSchema


router = APIRouter(
    tags=['Users'],
    responses= {
        status.HTTP_401_UNAUTHORIZED: NotAuthenticatedResponse().dict(),
        status.HTTP_403_FORBIDDEN: ForbiddenResponse().dict(),
        status.HTTP_404_NOT_FOUND: NotFoundResponse().dict()
    }
)


templates = Jinja2Templates(directory="templates")


@router.get("/login", response_class=HTMLResponse)
async def get_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post(
    "/login", 
    response_model=OkResponse,
    status_code=status.HTTP_201_CREATED
)
async def login_user(
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
):
    login_data = LoginRequest(username=email, password=password)
    async with httpx.AsyncClient() as client:
        backend_response = await client.post(f'{settings.BACKEND_URL}/user-management/login', data=login_data.dict())
        response_data = backend_response.json()
        if backend_response.status_code == status.HTTP_401_UNAUTHORIZED:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail=response_data['detail'])
    
    response_data = LoginResponse(**response_data)
    response.set_cookie(key="token", value=f"{response_data.token_type} {response_data.access_token}", httponly=True)
    response.set_cookie(key="user_data", value=response_data.user.json(), httponly=True)
    
    return OkResponse(detail="Logowanie powiodło się.")


@router.get(
    "/logout",
    response_model=OkResponse, 
    status_code=status.HTTP_200_OK)
async def logout_user(response: Response):
    response.delete_cookie('token')
    response.delete_cookie('user_data')
    return OkResponse(detail="Użytkownik został wylogowany.")


@router.get("/sign-up", response_class=HTMLResponse)
async def get_registration_page(request: Request):
    return templates.TemplateResponse("registration.html", {"request": request})


@router.post(
    "/sign-up", 
    response_model=OkResponse,
    status_code=status.HTTP_201_CREATED
)
async def register_user(
    username: str = Form(...),
    password: str = Form(...),
    email: str = Form(...),
    gender: str = Form(...)
):
    data = UserCreateSchema(username=username, email=email, password=password, gender=gender)
    async with httpx.AsyncClient() as client:
        response = await client.post(f'{settings.BACKEND_URL}/user-management/user', json=data.dict())
        response_data = response.json()
        if response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=response_data['detail'])
        
    return OkResponse(detail="Konto zostało utworzone.")


@router.get("/password-reset-code", response_class=HTMLResponse)
async def get_password_reset_code_form(request: Request):
    return templates.TemplateResponse("pass_reset_code.html", {"request": request})


@router.post(
    "/password-reset-code", 
    response_model=OkResponse,
    status_code=status.HTTP_201_CREATED
)
async def get_password_reset_code(
    email: str = Form(...)
):
    msg = "Email z linkiem do resetu hasła został wysłany."
    try:
        data = PassResetCodeRequestSchema(email=email)
    except Exception:
        return OkResponse(detail=msg)
        
    async with httpx.AsyncClient() as client:
        await client.post(f'{settings.BACKEND_URL}/user-management/password-reset-code', json=data.dict())
        
    return OkResponse(detail=msg)


@router.get("/account/reset-password/{code}", response_class=HTMLResponse)
async def get_password_reset_form(
    request: Request,
    code: UUID
):
    return templates.TemplateResponse("pass_reset_form.html", {"request": request})


@router.patch(
    "/account/reset-password/{code}", 
    response_model=OkResponse,
    status_code=status.HTTP_200_OK
)
async def reset_password(
    code: UUID,
    new_pass1: str = Form(...)
):
    data = PasswordResetSchema(code=code, password=new_pass1)
        
    async with httpx.AsyncClient() as client:
        response = await client.patch(f'{settings.BACKEND_URL}/user-management/user/reset-password', json=data.dict())
        response_data = response.json()
        if response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=response_data['detail'])
    
    return OkResponse(detail=response_data['detail'])


@router.delete(
    "/account/{id}", 
    response_model=OkResponse,
    status_code=status.HTTP_200_OK
)
async def delete_account(
    id: UUID,
    response: Response,
    user: Optional[UserSession] = Depends(get_user_session)
):
    if user and user.id == id:
        request_url = "/user-management/user"
    elif user and user.role == UserRole.MODERATOR:
        request_url = f"/user-management/user/{id}"
    else:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Nie możesz wykonać tej operacji.")
    
    async with httpx.AsyncClient() as client:
        headers = {'authorization': user.token}
        await client.delete(f'{settings.BACKEND_URL}{request_url}', headers=headers)
    
    response.delete_cookie('token')
    response.delete_cookie('user_data')
    return OkResponse(detail="Konto zostało usunięte.")


@router.get("/profile/{id}", response_class=HTMLResponse)
async def get_user_profile(
    id: UUID,
    request: Request,
    user: Optional[UserSession] = Depends(get_user_session)
):
    async with httpx.AsyncClient() as client:
        profile_response = await client.get(f'{settings.BACKEND_URL}/user-management/user/{id}')
        profile = profile_response.json()
        if profile_response.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail=profile['detail'])

        profile = UserGetProfileSchema(**profile)

        response = await client.get(f'{settings.BACKEND_URL}/blog/posts/{id}')
        posts = response.json()
        posts = PostListSchema(posts=posts)
         
    return templates.TemplateResponse("user_profile.html", {"request": request, "user": user, "posts": posts.dict(), "profile": profile})