from pydantic import BaseModel, Field
from typing import Optional

class ToggleBranchQuery(BaseModel):
    active: Optional[bool] = None
