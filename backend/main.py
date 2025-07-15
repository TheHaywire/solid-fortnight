from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .orchestrator import run_orchestration  # Import the orchestrator logic

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or ["http://localhost:3000"] for more security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProjectRequest(BaseModel):
    user_request: str

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/project")
def submit_project(request: ProjectRequest):
    result = run_orchestration(request.user_request)
    return result 