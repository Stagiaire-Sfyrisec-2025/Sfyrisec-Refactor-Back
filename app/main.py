from fastapi import FastAPI
from app.api.v1 import upload

app = FastAPI(title="Code Refactor API")

app.include_router(upload.router, prefix="/api/v1/upload", tags=["Upload"])