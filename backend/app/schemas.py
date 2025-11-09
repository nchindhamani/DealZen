from pydantic import BaseModel, Field
from typing import List, Optional, Any

class QueryRequest(BaseModel):
    query: str = Field(..., max_length=250) # Enforce 250 char limit

class ChatResponse(BaseModel):
    answer: str
    source_deals: List[dict]

