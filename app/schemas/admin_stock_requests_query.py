from pydantic import BaseModel, Field
from typing import Optional
from app.models.enums import StockRequestStatus

class AdminStockRequestsQuery(BaseModel):
    status: Optional[StockRequestStatus] = None
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)
