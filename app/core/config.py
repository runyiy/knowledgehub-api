import os
from functools import lru_cache
from dotenv import load_dotenv


def _load_env_once() -> None:
    # use ENV_FILE before running to decide which env file
    env_file = os.getenv("ENV_FILE", ".env")
    load_dotenv(env_file, override=False)


class Settings:
    def __init__(self):
        _load_env_once()

        self.ENV = os.getenv("ENV", "dev")
        self.DATABASE_URL = os.getenv("DATABASE_URL")
        self.JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
        self.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "20")
        )
        if not self.DATABASE_URL:
            raise RuntimeError(
                f"DATABASE_URL is not set (ENV_FILE={os.getenv('ENV_FILE', '.env')})"
            )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
