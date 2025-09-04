from fastapi import FastAPI
from api.v1 import upload, analyze, refactor

app = FastAPI()

app.include_router(upload.router, prefix="/api/v1/upload", tags=["Upload"])
app.include_router(analyze.router, prefix="/api/v1/analyze", tags=["Analyze"])
app.include_router(refactor.router, prefix="/api/v1/refactor", tags=["Refactor"])