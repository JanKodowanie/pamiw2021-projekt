import os
import sys
import uvicorn
import settings
from feed_db import feed_db
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


try:        
    os.mkdir(settings.MEDIA_DIR)
except Exception:
    settings.logger.info("Media directory already exists")

app.mount(settings.MEDIA_ROOT, StaticFiles(directory=settings.MEDIA_DIR), name="media")


try:
    settings.create_db_connection(app)
except Exception as e:
    settings.logger.error("Couldn't connect to db")
    settings.logger.error(e)
    sys.exit(-1)
    
    
@app.on_event('startup')
async def startup():
    try:
        await feed_db()
    except Exception as e:
        settings.logger.error("Couldn't create test db data")
        settings.logger.error(e)


if __name__ == "__main__":
    uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=True)