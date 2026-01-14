"""
Resource Path Helper for PyInstaller

Handles path resolution for both development and frozen (packaged) environments.

PyInstaller extracts bundled resources to a temporary _MEIPASS directory,
so resource paths must be resolved differently when frozen.

Usage:
    from weather_app.launcher.resource_path import get_resource_path

    # Get path to bundled icon
    icon_path = get_resource_path("weather_app/resources/icons/weather-app.png")

    # Get path to frontend
    frontend_path = get_resource_path("web/dist")
"""

import sys
from pathlib import Path


def get_resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and frozen builds.

    When running in development, resolves from project root.
    When running as PyInstaller exe, resolves from _MEIPASS.

    Args:
        relative_path: Path relative to project root (e.g., "web/dist/index.html")

    Returns:
        Path: Absolute path to resource

    Example:
        >>> icon = get_resource_path("weather_app/resources/icons/weather-app.png")
        >>> print(icon)
        # Development: /path/to/Weather-App/weather_app/resources/icons/weather-app.png
        # Frozen: C:/Users/.../AppData/Local/Temp/_MEIxxxxx/weather_app/resources/icons/weather-app.png
    """
    if getattr(sys, "frozen", False):
        # Running as PyInstaller bundle
        # PyInstaller sets sys._MEIPASS to the temp extraction directory
        base_path = Path(sys._MEIPASS)  # type: ignore[attr-defined]
    else:
        # Running in development
        # Resolve from project root (3 levels up from this file)
        base_path = Path(__file__).parent.parent.parent

    resource = base_path / relative_path
    return resource


def verify_resource_exists(relative_path, resource_name=None):
    """
    Verify that a resource exists and return its path.

    Args:
        relative_path: Path relative to project root
        resource_name: Human-readable name for error messages

    Returns:
        Path: Absolute path to resource

    Raises:
        FileNotFoundError: If resource doesn't exist
    """
    resource = get_resource_path(relative_path)
    if not resource.exists():
        name = resource_name or relative_path
        raise FileNotFoundError(
            f"Required resource not found: {name}\n"
            f"Expected at: {resource}\n"
            f"Frozen: {getattr(sys, 'frozen', False)}\n"
            f"Base path: {Path(sys._MEIPASS) if getattr(sys, 'frozen', False) else Path(__file__).parent.parent.parent}"  # type: ignore[attr-defined]
        )
    return resource


def get_frontend_path():
    """
    Get path to frontend dist directory.

    Returns:
        Path: Path to web/dist directory

    Raises:
        FileNotFoundError: If frontend not built
    """
    return verify_resource_exists("web/dist", "Frontend build")


def get_icon_path(icon_name="weather-app.png"):
    """
    Get path to app icon.

    Args:
        icon_name: Icon filename (default: weather-app.png)

    Returns:
        Path: Path to icon file

    Raises:
        FileNotFoundError: If icon not found
    """
    return verify_resource_exists(
        f"weather_app/resources/icons/{icon_name}", f"Icon: {icon_name}"
    )


def get_base_path():
    """
    Get base path for all resources.

    Returns:
        Path: Base path (project root in dev, _MEIPASS when frozen)
    """
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    else:
        return Path(__file__).parent.parent.parent


def is_frozen():
    """
    Check if running as frozen (packaged) executable.

    Returns:
        bool: True if frozen, False if development
    """
    return getattr(sys, "frozen", False)


def get_meipass():
    """
    Get PyInstaller _MEIPASS directory (frozen builds only).

    Returns:
        Path | None: _MEIPASS path if frozen, None if development
    """
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return None
