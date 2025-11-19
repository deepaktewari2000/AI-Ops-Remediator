from fastapi import APIRouter, BackgroundTasks
from app.schemas import IncidentCreate
from app.core.orchestrator import Orchestrator

router = APIRouter()
orc = Orchestrator()

@router.post("/")
async def create_incident(inc: IncidentCreate, background_tasks: BackgroundTasks):
    background_tasks.add_task(orc.process_incident, inc.dict())
    return {"message": "incident received"}
