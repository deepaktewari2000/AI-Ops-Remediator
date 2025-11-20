from fastapi import APIRouter, BackgroundTasks
from app.schemas import IncidentCreate
from app.core.orchestrator import Orchestrator

router = APIRouter()
from app.core.dependencies import orchestrator

@router.post("/")
async def create_incident(inc: IncidentCreate, background_tasks: BackgroundTasks):
    background_tasks.add_task(orchestrator.process_incident, inc.model_dump())
    return {"message": "incident received"}
