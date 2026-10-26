from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from core.docker_guard import ensure_app_running_in_docker

from routers import health, location_router, user_router, game_options_router, game_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Defines startup and shutdown events to be performed during the app's lifespan.
    """
    ensure_app_running_in_docker()
    yield

app = FastAPI(
    title="Language Game API",
    lifespan=lifespan
)

#this section allows vue (or whatever frontend we choose) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(location_router.router)
app.include_router(user_router.router)
app.include_router(game_options_router.router)
app.include_router(game_router.router)

@app.get("/")
def root():
    return {"message": "Language Game API is running"}