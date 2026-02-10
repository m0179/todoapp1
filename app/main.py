"""
Main FastAPI application entry point.
Initializes the app and registers routes.
"""
from fastapi import FastAPI
from app.config import settings
from app.routes import todo_router
from app.database import engine, Base

# Create database tables
# Note: In production, use Alembic migrations instead
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="A scalable Todo API with CRUD operations",
    version="1.0.0",
    debug=settings.DEBUG
)


# Root endpoint
@app.get("/", tags=["root"])
def read_root():
    """
    Root endpoint - health check.
    
    Returns:
        dict: Welcome message and API info
    """
    return {
        "message": "Welcome hello to to Todo API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


# Register routers
app.include_router(todo_router)


if __name__ == "__main__":
    import uvicorn
    # Run the application
    # Use: python -m app.main
    # Or: uvicorn app.main:app --reload
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
