from fastapi import FastAPI
from app.routers import  users, projects, tasks, auth
# from app.core.database import engine, Base

app = FastAPI(
    title="Collaborative Kanban Board API",
    description="A professional Kanban board API with team collaboration features",
)


@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Kanban Board API!",
    }


app.include_router(users.router)
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(tasks.router)