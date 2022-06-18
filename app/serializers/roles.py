from typing import Optional

from pydantic import BaseModel


class RoleBody(BaseModel):
    id: Optional[int]
    name: str
