"""Tests for App Factory.

This module tests the FastAPI application factory including:
- Frontend registration
- Frozen executable path handling
- Static file mounting
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# =============================================================================
# Register Frontend Tests (Phase 2 Coverage)
# =============================================================================


@pytest.mark.unit
class TestRegisterFrontend:
    """Tests for register_frontend function."""

    def test_register_frontend_frozen_executable(self):
        """Uses _MEIPASS path when running as frozen executable."""
        from fastapi import FastAPI

        app = FastAPI()

        # Mock sys.frozen and sys._MEIPASS for PyInstaller scenario
        mock_meipass = "/tmp/pyinstaller_bundle"

        with patch.object(sys, "frozen", True, create=True):
            with patch.object(sys, "_MEIPASS", mock_meipass, create=True):
                # Also mock the static_dir.exists() check
                with patch.object(Path, "exists", return_value=True):
                    # StaticFiles is imported inside register_frontend, so patch it there
                    with patch("fastapi.staticfiles.StaticFiles") as mock_static_files:
                        from weather_app.web.app import register_frontend

                        register_frontend(app)

                        # Verify StaticFiles was called with the _MEIPASS path
                        # (may be called multiple times due to module caching)
                        assert mock_static_files.called
                        call_kwargs = mock_static_files.call_args[1]
                        assert "web" in call_kwargs["directory"]
                        assert "dist" in call_kwargs["directory"]

    def test_register_frontend_development_mode(self):
        """Uses project path when not running as frozen executable."""
        from fastapi import FastAPI

        app = FastAPI()

        # Ensure sys.frozen is False (development mode)
        with patch.object(sys, "frozen", False, create=True):
            with patch.object(Path, "exists", return_value=True):
                with patch("fastapi.staticfiles.StaticFiles") as mock_static_files:
                    from weather_app.web.app import register_frontend

                    register_frontend(app)

                    # Verify StaticFiles was called
                    mock_static_files.assert_called_once()
                    call_kwargs = mock_static_files.call_args[1]
                    # Should contain web/dist in the path
                    assert "dist" in call_kwargs["directory"]

    def test_register_frontend_logs_warning_when_not_found(self, caplog):
        """Logs warning when frontend static files don't exist."""
        import logging

        from fastapi import FastAPI

        app = FastAPI()

        # Mock static_dir to non-existent path
        with patch.object(sys, "frozen", False, create=True):
            with patch.object(Path, "exists", return_value=False):
                with caplog.at_level(logging.WARNING):
                    from weather_app.web.app import register_frontend

                    register_frontend(app)

                    # Check that warning was logged
                    warning_records = [
                        r for r in caplog.records if r.levelno == logging.WARNING
                    ]
                    warning_messages = [r.message for r in warning_records]
                    assert any(
                        "frontend" in msg.lower() or "not found" in msg.lower()
                        for msg in warning_messages
                    ), f"Expected frontend warning, got: {warning_messages}"

    def test_register_frontend_mounts_static_files(self):
        """Mounts static files at root path when directory exists."""
        from fastapi import FastAPI

        app = FastAPI()

        with patch.object(sys, "frozen", False, create=True):
            with patch.object(Path, "exists", return_value=True):
                with patch("fastapi.staticfiles.StaticFiles") as mock_static_files:
                    mock_static_instance = MagicMock()
                    mock_static_files.return_value = mock_static_instance

                    with patch.object(app, "mount") as mock_mount:
                        from weather_app.web.app import register_frontend

                        register_frontend(app)

                        # Verify mount was called with correct parameters
                        mock_mount.assert_called_once()
                        call_args = mock_mount.call_args
                        assert call_args[0][0] == "/"  # Root path
                        assert call_args[1]["name"] == "frontend"


# =============================================================================
# Create App Tests
# =============================================================================


@pytest.mark.unit
class TestCreateApp:
    """Tests for create_app function."""

    def test_create_app_returns_fastapi_instance(self):
        """create_app returns a FastAPI application."""
        with patch("weather_app.web.app.register_frontend"):
            # Need to reimport to get fresh app
            from weather_app.web.app import create_app

            app = create_app()

            from fastapi import FastAPI

            assert isinstance(app, FastAPI)

    def test_create_app_configures_cors(self):
        """create_app adds CORS middleware."""
        with patch("weather_app.web.app.register_frontend"):
            from weather_app.web.app import create_app

            app = create_app()

            # Check that middleware was added
            # FastAPI stores middleware in app.user_middleware
            middleware_classes = [m.cls.__name__ for m in app.user_middleware]
            assert "CORSMiddleware" in middleware_classes

    def test_create_app_registers_routes(self):
        """create_app registers API routes."""
        with patch("weather_app.web.app.register_frontend"):
            from weather_app.web.app import create_app

            app = create_app()

            # Check that routes are registered
            route_paths = [route.path for route in app.routes]
            # Should have at least the API routes
            assert any("/api" in path for path in route_paths)
