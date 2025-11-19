from pydantic import BaseModel
from typing import Dict, Optional

class IncidentCreate(BaseModel):
    source: str
    severity: str
    details: Dict
    timestamp: Optional[str] = None
