from pydantic import BaseModel
from typing import Optional

class ToggleCategoryQuery(BaseModel):
    active: Optional[bool] = None
