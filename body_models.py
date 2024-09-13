from pydantic import BaseModel
from typing import Dict, Any

class Request(BaseModel):
    endpoint: str
    method: str
    pagination: Dict[str, Any]
    payload: Dict[str, Any]