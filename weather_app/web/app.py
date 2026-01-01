"""
FastAPI application factory
Creates and configures the FastAPI app with middleware and routes
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from weather_app.config import API_TITLE, API_DESCRIPTION, API_VERSION, CORS_ORIGINS


def create_app() -> FastAPI:
    """
    Application factory function that creates and configures FastAPI app
    
    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title=API_TITLE,
        description=API_DESCRIPTION,
        version=API_VERSION
    )
    
    # Enable CORS for React frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Import routes after app creation to avoid circular imports
    from weather_app.web import routes
    routes.register_routes(app)
    
    return app
