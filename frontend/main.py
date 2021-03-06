import uvicorn
import settings
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from core.users.router import router as users_router
from core.blog.router import router as blog_router


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.CORS_ALLOWED_METHODS,
    allow_headers=settings.CORS_ALLOWED_HEADERS
)
app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS
)

app.include_router(users_router)
app.include_router(blog_router)


app.mount('/static', StaticFiles(directory='static'), name="static")


if __name__ == "__main__":
    uvicorn.run('main:app', host="0.0.0.0", port=3000, reload=True)