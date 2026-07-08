import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    GEE_PROJECT_ID: str | None = os.getenv("GEE_PROJECT_ID")
    GEE_SERVICE_ACCOUNT_FILE: str | None = os.getenv("GEE_SERVICE_ACCOUNT_FILE")


settings = Settings()
