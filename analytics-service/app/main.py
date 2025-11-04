from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from . import models
from .database import engine
from .routers import analytics

# Create database tables
models.Base.metadata.create_all(bind=engine)

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
