from fastapi import FastAPI
from routers import users
app = FastAPI()

@app.get("/")
def root():
    return {"Message":"Hello"}

app.include_router(users.router)