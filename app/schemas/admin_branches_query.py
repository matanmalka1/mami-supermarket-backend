from pydantic import Field
from .common import DefaultModel
from typing import Optional
from app.models.enums import StockRequestStatus
from app.models.enums import Role

class ToggleBranchQuery(DefaultModel):
    active: bool

class ToggleCategoryQuery(DefaultModel):
    active: Optional[bool] = None

class AdminStockRequestsQuery(DefaultModel):
    status: Optional[StockRequestStatus] = None
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)

class AdminUsersQuery(DefaultModel):
    q: Optional[str] = None
    role: Optional[Role] = None
    isActive: Optional[bool] = None
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)

class RevenueQuery(DefaultModel):
    range: str = Field(default="30d", pattern=r"^\d+[dmy]$")
    granularity: Optional[str] = Field(default=None, pattern=r"^(day|month|year)?$")
