from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Import the individual apps
from user_service.user_app.main import app as user_app
from analytics_service.analytics_app.main import app as analytics_app

app = FastAPI(
    title="Analytics Platform Monolith",
    description="Combined User and Analytics services for easy free deployment",
    version="1.0.0"
)

# Configure CORS for the monolith
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the individual apps
# This allows them to function at /user-service/... and /analytics-service/...
app.mount("/user-service", user_app)
app.mount("/analytics-service", analytics_app)

from user_service.user_app.database import engine as user_engine, Base as UserBase
from analytics_service.analytics_app.database import engine as analytics_engine, Base as AnalyticsBase

@app.on_event("startup")
async def startup_event():
    UserBase.metadata.create_all(bind=user_engine)
    AnalyticsBase.metadata.create_all(bind=analytics_engine)

@app.get("/")
async def root():
    return {
        "message": "Analytics Platform Monolith is running",
        "services": {
            "user_service": "/user-service",
            "analytics_service": "/analytics-service"
        },
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "mode": "monolith"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
