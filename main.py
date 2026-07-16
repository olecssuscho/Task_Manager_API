from fastapi import FastAPI
from routers import project_members,users,projects,tasks
app = FastAPI()

@app.get("/")
def root():
    return {"Message":"Hello"}

app.include_router(users.router)
app.include_router(projects.router)
app.include_router(project_members.router)
app.include_router(tasks.router)
