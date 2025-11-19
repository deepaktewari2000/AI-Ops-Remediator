from fastapi import FastAPI
from app.api.v1 import health, incidents
from app.core.orchestrator import Orchestrator

app = FastAPI(title="AI-Ops-Remediator", version="0.1.0")

app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
app.include_router(incidents.router, prefix="/api/v1/incidents", tags=["incidents"])

orchestrator = Orchestrator()

@app.on_event("startup")
async def startup():
    await orchestrator.start()

@app.on_event("shutdown")
async def shutdown():
    await orchestrator.stop()
