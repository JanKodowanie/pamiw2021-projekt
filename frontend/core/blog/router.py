import httpx
import settings
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Request, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from common.responses import *
from .schemas import *
from core.users.schemas import UserSession
from core.users.auth import get_user_session
from typing import Optional, Dict


router = APIRouter(
    tags=['Blog'],
    responses= {
        status.HTTP_401_UNAUTHORIZED: NotAuthenticatedResponse().dict(),
        status.HTTP_403_FORBIDDEN: ForbiddenResponse().dict(),
        status.HTTP_404_NOT_FOUND: NotFoundResponse().dict()
    }
)


templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def get_blog_page(
    request: Request,
    user: Optional[UserSession] = Depends(get_user_session)
):
    async with httpx.AsyncClient() as client:
        response = await client.get(f'{settings.BACKEND_URL}blog/posts')
        data = response.json()
        posts = PostListSchema(posts=data)
         
    return templates.TemplateResponse("blog.html", {"request": request, "user": user, "posts": posts.dict()})


@router.get("/tag/{name}", response_class=HTMLResponse)
async def get_tag_view(
    name: str,
    request: Request,
    user: Optional[UserSession] = Depends(get_user_session)
):
    async with httpx.AsyncClient() as client:
        response = await client.get(f'{settings.BACKEND_URL}blog/tag/{name}')
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
        else:
            data = []
        posts = PostListSchema(posts=data)
         
    return templates.TemplateResponse("blog_tag.html", {"request": request, "tag": name, "user": user, "posts": posts.dict()})