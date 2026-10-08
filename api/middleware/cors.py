"""
CORS middleware configuration for Megan API.
Allows the React frontend (localhost:5173) to connect.
"""

from fastapi.middleware.cors import CORSMiddleware


def add_cors(app):
    """Add CORS middleware to the FastAPI app."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",   # Vite dev server
            "http://localhost:3000",   # Alternative React port
            "http://127.0.0.1:5173",
            "http://127.0.0.1:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
