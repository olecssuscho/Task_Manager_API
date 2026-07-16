from fastapi import FastAPI
from routers import users,projects,project_member
app = FastAPI()

@app.get("/")
def root():
    return {"Message":"Hello"}

app.include_router(users.router)
app.include_router(projects.router)
app.include_router(project_member.router)