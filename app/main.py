from fastapi import FastAPI
from api.common.health import router as health_router
from api.common.upload import router as upload_router
from api.codeigniter.analyze import router as ci_analyze_router
from api.codeigniter.refactor import router as ci_refactor_router
from api.laravel.analyze import router as laravel_analyze_router
from api.laravel.refactor import router as laravel_refactor_router
from api.symfony.analyze import router as symfony_analyze_router
from api.symfony.refactor import router as symfony_refactor_router

app = FastAPI(
    title="PHP Code Refactor Platform",
    description="API for analyzing and refactoring PHP code across multiple frameworks",
    version="1.0.0"
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(upload_router, prefix="/api/v1")
app.include_router(ci_analyze_router, prefix="/api/v1/codeigniter")
app.include_router(ci_refactor_router, prefix="/api/v1/codeigniter")
app.include_router(laravel_analyze_router, prefix="/api/v1/laravel")
app.include_router(laravel_refactor_router, prefix="/api/v1/laravel")
app.include_router(symfony_analyze_router, prefix="/api/v1/symfony")
app.include_router(symfony_refactor_router, prefix="/api/v1/symfony")

@app.get("/")
async def root():
    return {"message": "Welcome to the PHP Code Refactor Platform API"}