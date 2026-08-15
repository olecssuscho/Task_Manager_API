from fastapi import FastAPI
from routers import project_members,users,projects,tasks,comments
import websocket
import asyncio
from redis_listener import listener
app = FastAPI()

@app.get("/")
def root():
    return {"Message":"Hello"}

app.include_router(users.router)
app.include_router(projects.router)
app.include_router(project_members.router)
app.include_router(tasks.router)
app.include_router(comments.router)
app.include_router(websocket.router)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(listener())
    