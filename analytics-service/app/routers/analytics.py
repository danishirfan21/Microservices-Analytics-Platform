from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from typing import List, Optional
from datetime import datetime, timedelta
import httpx
import os

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/analytics", tags=["analytics"])

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8000")

@router.post("/events", response_model=schemas.EventResponse, status_code=201)
async def create_event(event: schemas.EventCreate, db: Session = Depends(get_db)):
    """Record a new user activity event"""
    db_event = models.Event(
        event_type=event.event_type,
        user_id=event.user_id,
        event_metadata=event.event_metadata
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@router.get("/events", response_model=List[schemas.EventResponse])
async def get_events(
    skip: int = 0,
    limit: int = 100,
    event_type: Optional[str] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get all events with optional filtering"""
    query = db.query(models.Event)

    if event_type:
        query = query.filter(models.Event.event_type == event_type)
    if user_id:
        query = query.filter(models.Event.user_id == user_id)

    events = query.order_by(models.Event.created_at.desc()).offset(skip).limit(limit).all()
    return events

@router.get("/summary", response_model=schemas.AnalyticsSummary)
async def get_analytics_summary(db: Session = Depends(get_db)):
    """Get overall analytics summary"""
    # Get total users from user service
    total_users = 0
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{USER_SERVICE_URL}/users", timeout=5.0)
            if response.status_code == 200:
                users = response.json()
                total_users = len(users)
    except Exception as e:
        print(f"Failed to fetch users from user service: {e}")
        # Fallback: count distinct user_ids from events
        total_users = db.query(func.count(distinct(models.Event.user_id))).scalar()

    # Get active users in last 24 hours
    last_24h = datetime.utcnow() - timedelta(hours=24)
    active_users_24h = db.query(func.count(distinct(models.Event.user_id))).filter(
        models.Event.created_at >= last_24h
    ).scalar()

    # Get total events
    total_events = db.query(func.count(models.Event.id)).scalar()

    # Get event type counts
    event_counts = db.query(
        models.Event.event_type,
        func.count(models.Event.id).label('count')
    ).group_by(models.Event.event_type).all()

    event_type_counts = {event_type: count for event_type, count in event_counts}

    return schemas.AnalyticsSummary(
        total_users=total_users or 0,
        active_users_24h=active_users_24h or 0,
        total_events=total_events or 0,
        event_type_counts=event_type_counts
    )

@router.get("/events/by-type", response_model=List[schemas.EventTypeCount])
async def get_events_by_type(db: Session = Depends(get_db)):
    """Get event counts grouped by type"""
    event_counts = db.query(
        models.Event.event_type,
        func.count(models.Event.id).label('count')
    ).group_by(models.Event.event_type).order_by(func.count(models.Event.id).desc()).all()

    return [
        schemas.EventTypeCount(event_type=event_type, count=count)
        for event_type, count in event_counts
    ]

@router.get("/events/date-range", response_model=schemas.DateRangeAnalytics)
async def get_analytics_by_date_range(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    """Get analytics for a specific date range"""
    query = db.query(models.Event)

    # Default to last 7 days if no dates provided
    if not start_date and not end_date:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)

    if start_date:
        query = query.filter(models.Event.created_at >= start_date)
    if end_date:
        query = query.filter(models.Event.created_at <= end_date)

    # Total events in range
    total_events = query.count()

    # Unique users in range
    unique_users = query.with_entities(func.count(distinct(models.Event.user_id))).scalar()

    # Event breakdown by type
    event_breakdown = {}
    event_counts = query.with_entities(
        models.Event.event_type,
        func.count(models.Event.id).label('count')
    ).group_by(models.Event.event_type).all()

    event_breakdown = {event_type: count for event_type, count in event_counts}

    return schemas.DateRangeAnalytics(
        start_date=start_date,
        end_date=end_date,
        total_events=total_events,
        unique_users=unique_users or 0,
        event_breakdown=event_breakdown
    )

@router.get("/users/{user_id}/events", response_model=List[schemas.EventResponse])
async def get_user_events(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all events for a specific user"""
    events = db.query(models.Event).filter(
        models.Event.user_id == user_id
    ).order_by(models.Event.created_at.desc()).offset(skip).limit(limit).all()

    return events
