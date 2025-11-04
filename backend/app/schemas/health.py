from typing import Any, Dict
from pydantic import BaseModel


class HealthResponse(BaseModel):
    success: bool
    data: Dict[str, Any]


