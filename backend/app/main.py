import sys
from pathlib import Path

from dotenv import load_dotenv

# Repo root so top-level AI/ package imports resolve when running from backend/.
_REPO_ROOT = Path(__file__).resolve().parents[2]
_BACKEND_DIR = Path(__file__).resolve().parent.parent

load_dotenv(_BACKEND_DIR / ".env")

if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.community_reports import router as community_reports_router
from app.routers.flood import router as flood_router
from app.routers.earthquake import router as earthquake_router
from app.routers.test_ui import router as test_ui_router
from app.routers.decision import router as decision_router
from app.routers.pipeline import router as pipeline_router
from app.routers.assistance import router as assistance_router
from app.routers.accessibility import router as accessibility_router
from app.routers.dashboard import router as dashboard_router

from app.routers import users

from app.routers import auth

app = FastAPI(
    title="MONJED API",
    description=(
        "AI-powered disaster risk interpretation "
        "and action support platform"
    ),
    version="0.1.0",
)


# ============================================================
# CORS
# ============================================================

# Local frontend development origins.
# Vite usually uses port 5173.
# React/Next development may use port 3000.
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ROUTERS
# ============================================================

app.include_router(flood_router)
app.include_router(earthquake_router)
app.include_router(community_reports_router)
app.include_router(decision_router)
app.include_router(pipeline_router)
app.include_router(assistance_router)
app.include_router(accessibility_router)
app.include_router(test_ui_router)
app.include_router(dashboard_router)
app.include_router(users.router)
app.include_router(auth.router)

# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "Welcome to MONJED API",
        "service": "MONJED API",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "MONJED API",
    }