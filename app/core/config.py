import os
from functools import lru_cache


class Settings:
    def __init__(self):
        self.ENV = os.getenv("ENV", "dev")
        self.DATABASE_URL = os.getenv("DATABASE_URL")
        self.JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
        self.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "20")
        )
        if not self.DATABASE_URL:
            raise RuntimeError("DATABASE_URL is not set")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
