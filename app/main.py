from fastapi import FastAPI
from api.v1 import upload

app = FastAPI()

app.include_router(upload.router, prefix="/api/v1/upload", tags=["Upload"])