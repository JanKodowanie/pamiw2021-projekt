import httpx
import settings
from fastapi import APIRouter, HTTPException, File, UploadFile, Form, Request, status, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from common.responses import *
from .schemas import *


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
        backend_response = await client.post(f'{settings.BACKEND_URL}user-management/login', data=login_data.dict())
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
        response = await client.post(f'{settings.BACKEND_URL}user-management/user', json=data.dict())
        response_data = response.json()
        if response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=response_data['detail'])
        
    return OkResponse(detail="Konto zostało utworzone.")