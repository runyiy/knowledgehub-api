from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from app.db.session import engine
from app.db.base import Base
from app.api.routes import api_router

app = FastAPI(
    title="KnowledgeHub API",
    description="This app is for practicing",
    version="0.1.0"
)
app.include_router(api_router, prefix="/api")
Base.metadata.create_all(bind=engine)


@app.get("/")
async def root():
    return {"Hello": "World"}