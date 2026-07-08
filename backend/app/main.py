import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, SessionLocal, engine
from app.api.router import api_router
from app.core.gee_auth import initialize_earthengine
from app.core.seed import seed_catalog
import app.models  # noqa: F401

logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)


app = FastAPI(title="geoInsight API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.on_event("startup")
def on_startup():
    try:
        initialize_earthengine()
    except Exception:
        logger.warning("Earth Engine did not initialize - GEE-backed endpoints will fail until it does.")

    db = SessionLocal()
    try:
        seed_catalog(db)
    finally:
        db.close()



