from dotenv import load_dotenv
from fastapi import FastAPI

from app.api.routes import api_router
from app.core.config import get_settings
from app.db.session import init_engine


def create_app() -> FastAPI:
    load_dotenv()
    app = FastAPI(
        title="KnowledgeHub API",
        description="This app is for practicing",
        version="0.1.0",
    )
    settings = get_settings()
    init_engine(settings.DATABASE_URL)

    app.include_router(api_router, prefix="/api")

    return app


app = create_app()


@app.get("/")
async def root():
    return {"Hello": "World"}
