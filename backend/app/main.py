from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routes import auth, dashboard, opportunities

settings = get_settings()

app = FastAPI(
    title="Salesforce Dashboard API",
    version="1.0.0",
    description="Backend API for the Salesforce Opportunity Dashboard",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(
    opportunities.router, prefix="/api/opportunities", tags=["Opportunities"]
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
