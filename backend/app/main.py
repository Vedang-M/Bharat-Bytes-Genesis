from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .utils import engine

app = FastAPI(title="JalKosh Backend")

# CORS – allow the Vite dev server and any deployed frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from .routes import health, water_status, crop_advice, users

app.include_router(health.router)
app.include_router(water_status.router)
app.include_router(crop_advice.router)
app.include_router(users.router)

# Create DB tables at startup
from sqlmodel import SQLModel

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"status": "ok", "app": "JalKosh"}
