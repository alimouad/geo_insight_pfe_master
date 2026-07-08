from fastapi import APIRouter

from app.api.endpoints import analyses, auth, datasets, exports, indicators, projects, regions, users

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(datasets.router, prefix="/datasets", tags=["datasets"])
api_router.include_router(indicators.router, prefix="/indicators", tags=["indicators"])
api_router.include_router(analyses.router, prefix="/analyses", tags=["analyses"])
api_router.include_router(regions.router, prefix="/regions", tags=["regions"])
api_router.include_router(exports.router, prefix="/exports", tags=["exports"])
