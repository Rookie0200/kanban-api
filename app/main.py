from fastapi import FastAPI

app = FastAPI(
    title="Collaborative Kanban Board API",
    description="A professional Kanban board API with team collaboration features",
    version="1.0.0",
)


@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Kanban Board API!",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}