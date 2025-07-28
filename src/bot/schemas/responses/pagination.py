from typing import Generic, Sequence, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic schema for paginated responses."""

    items: Sequence[T]
    total_count: int
    page: int
    page_size: int
    total_pages: int
