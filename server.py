#!/usr/bin/env python3
"""
Weather App Entry Point
Runs the FastAPI server using the refactored package structure
"""

import uvicorn

from weather_app.config import HOST, PORT
from weather_app.web.app import create_app

if __name__ == "__main__":
    app = create_app()
    uvicorn.run(app, host=HOST, port=PORT)
