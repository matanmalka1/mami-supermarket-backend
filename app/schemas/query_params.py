from pydantic import Field
from .common import DefaultModel
from typing import Optional

class ProductSearchQuery(DefaultModel):
    q: Optional[str] = None
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)
    min_price: Optional[float] = Field(default=None, ge=0)
    max_price: Optional[float] = Field(default=None, ge=0)
    sort: Optional[str] = Field(default=None, pattern=r"^(price|name|date)$")
    category_id: Optional[int] = Field(default=None, ge=1)
    branch_id: Optional[int] = Field(default=None, ge=1)
    in_stock: Optional[bool] = None
    organic_only: Optional[bool] = None
