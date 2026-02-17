from app.routes.todo_routes import router as todo_router
from app.routes.auth_routes import router as auth_router

__all__ = ["todo_router", "auth_router"]
