from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import health, location_router

app = FastAPI(
    title="Language Game API"
)

#this section allows vue (or whatever frontend we choose) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://localhost:5173"],#this is the port that vue uses
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(location_router.router)