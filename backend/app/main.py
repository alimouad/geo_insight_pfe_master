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
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def no_store_cache(request, call_next):
    # Different localhost ports (frontend dev server, pgAdmin, ...) all hit
    # this API. Without an explicit no-store, browsers can serve a
    # disk-cached response — including its Access-Control-Allow-Origin —
    # for a request made from a different origin, breaking CORS silently.
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    return response


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



