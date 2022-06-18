from typing import List, Optional

from pydantic import BaseModel

from .auth import UserBody
from .roles import RoleBody


class UserRolesBody(BaseModel):
    user: UserBody
    roles: List[RoleBody]


class PaginationUsersBody(BaseModel):
    count: int
    total_pages: int
    page: int
    results: List[UserRolesBody]


class QueryPaginationBody(BaseModel):
    search: Optional[str]
    page: int = 1
    per_page: int = 20
