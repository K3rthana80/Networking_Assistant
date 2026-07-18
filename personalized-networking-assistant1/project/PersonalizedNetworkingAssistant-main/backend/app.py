from fastapi import FastAPI

from backend.routes import router
from backend.config import APP_NAME, APP_VERSION

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="AI-powered Personalized Networking Assistant"
)

app.include_router(router)