"""Common API schema placeholders."""

from pydantic import BaseModel


class PaginationParams(BaseModel):
    offset: int = 0
    limit: int = 20


class PaginatedResponse(BaseModel):
    items: list
    total: int
    offset: int
    limit: int
