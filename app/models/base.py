from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from datetime import datetime


class TimestampModel(BaseModel):
    """Base model with timestamp tracking"""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class ResponseBase(BaseModel):
    """Base class for API responses"""
    success: bool = True
    message: str = ""


class PaginationParams(BaseModel):
    """Common pagination parameters"""
    skip: int = 0
    limit: int = 100


class PaginatedResponse(ResponseBase):
    """Response with pagination metadata"""
    count: int = 0
    total: int = 0
    page: int = 1
    pages: int = 1
    has_next: bool = False
    has_prev: bool = False
