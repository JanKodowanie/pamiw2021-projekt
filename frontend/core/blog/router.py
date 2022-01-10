import httpx
import settings
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Request, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from common.responses import *
from .schemas import *


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
async def get_blog_page(request: Request):
    # user = {
    #     "username": "Janek",
    #     "role": "standard"    
    # }
    user = None
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f'{settings.BACKEND_URL}blog/posts')
        data = response.json()
        posts = PostListSchema(posts=data)
         
    return templates.TemplateResponse("blog.html", {"request": request, "user": user, "posts": posts.dict()})