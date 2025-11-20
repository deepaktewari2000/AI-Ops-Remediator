from fastapi import FastAPI
from app.api.v1 import health, incidents
from app.core.orchestrator import Orchestrator

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await orchestrator.start()
    await monitor.start()
    yield
    await monitor.stop()
    await orchestrator.stop()

app = FastAPI(title="AI-Ops-Remediator", version="0.1.0", lifespan=lifespan)

app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
app.include_router(incidents.router, prefix="/api/v1/incidents", tags=["incidents"])

from app.core.dependencies import orchestrator, monitor
