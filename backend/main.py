"""MeshForce FastAPI application entry point."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

from routers.incidents import router as incidents_router
from routers.volunteers import router as volunteers_router

app = FastAPI(title="MeshForce API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(incidents_router)
app.include_router(volunteers_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
