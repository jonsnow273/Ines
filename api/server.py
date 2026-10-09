"""
Megan FastAPI Server.
Bridges the React frontend to the Python AI backend.

Run with:
    uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload

Or:
    python -m api.server
"""

from fastapi import FastAPI

from core import config, logger
from api.middleware.cors import add_cors
from api.middleware.error_handler import global_exception_handler

# Import route modules
from api.routes import chat as chat_routes
from api.routes import steering as steering_routes
from api.routes import voice as voice_routes
from api.routes import automation as automation_routes
from api.routes import settings as settings_routes
from api.routes import organizer as organizer_routes
from api.routes import auth as auth_routes
from api.routes import memory as memory_routes
from api.routes import focus as focus_routes

# Import WebSocket modules
from api.websocket import chat_ws
from api.websocket import voice_ws


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title="Megan API",
        description="The first local AI assistant with controllable behavior.",
        version="0.1.0",
    )

    # Middleware
    add_cors(app)
    app.add_exception_handler(Exception, global_exception_handler)

    # REST routes
    app.include_router(auth_routes.router)
    app.include_router(chat_routes.router)
    app.include_router(steering_routes.router)
    app.include_router(voice_routes.router)
    app.include_router(automation_routes.router)
    app.include_router(settings_routes.router)
    app.include_router(organizer_routes.router)
    app.include_router(memory_routes.router)
    app.include_router(focus_routes.router)

    # WebSocket routes
    app.include_router(chat_ws.router)
    app.include_router(voice_ws.router)

    @app.on_event("startup")
    async def startup():
        """Load model and wire up all modules on server start."""
        logger.info("Starting Megan API server...")

        # Initialize local auth database
        try:
            from auth import init_db
            init_db()
            logger.info("Auth database initialized.")
        except Exception as e:
            logger.error(f"Auth database initialization failed: {e}")

        # Initialize Digital Memory service
        try:
            from memory import DigitalMemoryService
            mem_service = DigitalMemoryService()
            memory_routes.init(mem_service)
            logger.info("Digital Memory service initialized.")
        except Exception as e:
            logger.error(f"Digital Memory initialization failed: {e}")

        try:
            from llm import loader, engine
            from steering import SteeringEngine
            from chatbot import ContextManager
            from automation import ActionHandler
            from organizer import FolderWatcher, AuditLog

            # Load model
            logger.info(f"Loading model: {config.default_model}")
            loader.load()

            # Init steering
            se = SteeringEngine(loader.model, loader.tokenizer_wrapper, engine)
            logger.info("Steering engine initialized.")

            # Init context manager
            cm = ContextManager(
                tokenizer_wrapper=loader.tokenizer_wrapper,
                max_tokens=config.max_context_tokens,
            )

            # Init automation
            ah = ActionHandler(require_confirmation=config.confirmation_required)

            # Init organizer
            org_audit = AuditLog()
            org_watcher = FolderWatcher()

            # Wire dependencies into routes
            chat_routes.init(engine, se, cm)
            steering_routes.init(se, engine)
            voice_routes.init()
            automation_routes.init(ah)
            organizer_routes.init(org_watcher, org_audit)

            # Wire WebSocket handlers
            chat_ws.init(engine, se, cm)
            voice_ws.init()

            logger.info("Megan API ready!")

        except Exception as e:
            logger.error(f"Startup failed: {e}")
            logger.warning("API running in degraded mode. Model not loaded.")

    @app.get("/")
    async def root():
        return {
            "name": "Megan",
            "version": "0.1.0",
            "status": "online",
            "docs": "/docs",
        }

    @app.get("/health")
    async def health():
        from llm import loader
        return {
            "status": "healthy",
            "model_loaded": loader.is_loaded if hasattr(loader, "is_loaded") else False,
        }

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
