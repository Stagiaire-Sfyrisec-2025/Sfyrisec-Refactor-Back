from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1 import upload, analyze, refactor

app = FastAPI()

# 🌍 Autoriser ton frontend Next.js (localhost:3000)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # autorise uniquement ton frontend
    allow_credentials=True,
    allow_methods=["*"],          # GET, POST, PUT, DELETE...
    allow_headers=["*"],          # autoriser tous les headers
)

# 🚀 Inclusion des routes
app.include_router(upload.router, prefix="/api/v1/upload", tags=["Upload"])
app.include_router(analyze.router, prefix="/api/v1/analyze", tags=["Analyze"])
app.include_router(refactor.router, prefix="/api/v1/refactor", tags=["Refactor"])
