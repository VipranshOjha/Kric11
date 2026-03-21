from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Kric11 - Fantasy Cricket Dashboard",
    description="API for the private IPL 2026 Fantasy League",
    version="1.0.0"
)

from app.auth import router as auth_router
from app.api import router as fantasy_router

app.include_router(auth_router)
app.include_router(fantasy_router)

from app.web import router as web_router
from app.cron import router as cron_router

app.include_router(web_router)
app.include_router(cron_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev purposes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "Welcome to the Kric11 IPL 2026 Fantasy Engine!",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "ok"}
