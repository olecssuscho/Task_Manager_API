from fastapi import FastAPI
from routers import users,projects
app = FastAPI()

@app.get("/")
def root():
    return {"Message":"Hello"}

app.include_router(users.router)
app.include_router(projects.router)