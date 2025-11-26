from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRouter

from src.api.routers.health import router as health_router

openapi_tags = [
    {
        "name": "Health",
        "description": "Operational health and diagnostics endpoints (unauthenticated).",
    }
]

app = FastAPI(
    title="MVP Career Platform Backend API",
    description="Backend service for the Career Platform MVP. Internal endpoints for diagnostics and business logic.",
    version="1.0.0",
    openapi_tags=openapi_tags,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Versioned API router
api_v1 = APIRouter(prefix="/api/v1")

# Mount routers under /api/v1
api_v1.include_router(health_router)

app.include_router(api_v1)


# PUBLIC_INTERFACE
@app.get("/", summary="Health Check", tags=["Health"])
def health_check():
    """Basic service liveness probe that returns a static message."""
    return {"message": "Healthy"}
