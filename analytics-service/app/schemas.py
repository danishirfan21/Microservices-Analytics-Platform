from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class EventCreate(BaseModel):
    event_type: str
    user_id: int
    metadata: Optional[Dict[str, Any]] = {}

class EventResponse(EventCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class AnalyticsSummary(BaseModel):
    total_users: int
    active_users_24h: int
    total_events: int
    event_type_counts: Dict[str, int]

class EventTypeCount(BaseModel):
    event_type: str
    count: int

class DateRangeAnalytics(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    total_events: int
    unique_users: int
    event_breakdown: Dict[str, int]
