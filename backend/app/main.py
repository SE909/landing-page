from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.db.mongodb import close_db, connect_db
from app.routes import campaigns, generate, upload, templates, export


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()


app = FastAPI(title="Landing Page Creator", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Path(settings.upload_dir).mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

app.include_router(campaigns.router)
app.include_router(generate.router)
app.include_router(upload.router)
app.include_router(templates.router)
app.include_router(export.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
