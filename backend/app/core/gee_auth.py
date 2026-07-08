import logging

import ee

from app.core.config import settings

logger = logging.getLogger(__name__)

_initialized = False


def initialize_earthengine() -> None:
    global _initialized
    if _initialized:
        return

    if not settings.GEE_PROJECT_ID:
        logger.warning("GEE_PROJECT_ID is not set - Earth Engine will not be initialized.")
        return

    try:
        if settings.GEE_SERVICE_ACCOUNT_FILE:
            credentials = ee.ServiceAccountCredentials(email=None, key_file=settings.GEE_SERVICE_ACCOUNT_FILE)
            ee.Initialize(credentials, project=settings.GEE_PROJECT_ID)
        else:
            ee.Initialize(project=settings.GEE_PROJECT_ID)

        _initialized = True
        logger.info("Earth Engine initialized for project %s", settings.GEE_PROJECT_ID)
    except Exception:
        logger.exception("Failed to initialize Earth Engine")
        raise


def is_earthengine_ready() -> bool:
    return _initialized
