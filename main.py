from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from routers import project_members,users,projects,tasks,comments
from fastapi_pagination import add_pagination
import websocket
import asyncio
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler
from redis_listener import listener
from lim import limiter

@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.getenv("TESTING") != "1":
        asyncio.create_task(listener())   
    yield  

app = FastAPI(lifespan=lifespan)

@app.get("/")
def root():
    return {"Message":"Hello"}

app.include_router(users.router)
app.include_router(projects.router)
app.include_router(project_members.router)
app.include_router(tasks.router)
app.include_router(comments.router)
app.include_router(websocket.router)

add_pagination(app)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

if os.getenv("TESTING") != "1":
    app.add_middleware(SlowAPIMiddleware)


