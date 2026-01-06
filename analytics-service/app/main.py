from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
import logging

from . import models
from .database import engine
from .routers import analytics

app = FastAPI(
    title="Analytics Service API",
    description="Microservice for user activity analytics and event tracking",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus instrumentation
Instrumentator().instrument(app).expose(app)

@app.on_event("startup")
async def startup_event():
    """Create database tables when the application starts"""
    try:
        models.Base.metadata.create_all(bind=engine)
        logging.info("Database tables created successfully")
    except Exception as e:
        logging.error(f"Error creating database tables: {e}")

# Include routers
app.include_router(analytics.router)

@app.get("/")
async def root():
    return {
        "service": "Analytics Service",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
