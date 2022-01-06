import os
import sys
import uvicorn
import settings
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


app = FastAPI()
# app.include_router(users_router)
# app.include_router(blog_router)


try:        
    os.mkdir(settings.MEDIA_DIR)
except Exception as e:
    settings.logger.info(e)

app.mount(settings.MEDIA_ROOT, StaticFiles(directory=settings.MEDIA_DIR), name="media")


try:
    settings.create_db_connection(app)
except Exception as e:
    settings.logger.error("Couldn't connect to db")
    settings.logger.error(e)
    sys.exit(-1)


if __name__ == "__main__":
    uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=True)