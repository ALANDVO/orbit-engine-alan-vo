from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import init_db
from app.api import health, concepts, domains, progress, auth, import_taxonomy


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(domains.router, prefix="/api/v1", tags=["domains"])
app.include_router(concepts.router, prefix="/api/v1", tags=["concepts"])
app.include_router(progress.router, prefix="/api/v1", tags=["progress"])
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(import_taxonomy.router, prefix="/api/v1", tags=["import"])