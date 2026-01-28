from pydantic import BaseModel, Field
from typing import Optional

class BranchesQuery(BaseModel):
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)

class DeliverySlotsQuery(BaseModel):
    dayOfWeek: Optional[int] = Field(default=None, ge=0, le=6)
    branchId: Optional[int] = None
