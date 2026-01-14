"""
Structured logging configuration using structlog

This module provides centralized logging configuration for the entire application.
All log messages are output as structured JSON for easy parsing and analysis.

Usage:
    from weather_app.logging_config import get_logger

    logger = get_logger(__name__)
    logger.info("user_action", action="fetch_weather", device_id="12345")
"""

import logging
import sys
from collections.abc import Mapping
from typing import Any

import structlog
from structlog.contextvars import BoundVarsToken


def configure_logging(level: str = "INFO", json_logs: bool = True) -> None:
    """
    Configure structured logging for the application

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: If True, output JSON logs. If False, use human-readable format
    """
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper()),
    )

    # Build processor chain
    processors = [
        # Add log level
        structlog.stdlib.add_log_level,
        # Add timestamp
        structlog.processors.TimeStamper(fmt="iso"),
        # Add caller info (file, line, function)
        structlog.processors.CallsiteParameterAdder(
            [
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.LINENO,
                structlog.processors.CallsiteParameter.FUNC_NAME,
            ]
        ),
        # Stack unwinder for exceptions
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    # Add appropriate renderer
    if json_logs:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    # Configure structlog
    structlog.configure(
        processors=processors,  # type: ignore[arg-type]
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a configured logger instance

    Args:
        name: Logger name (typically __name__ of the calling module)

    Returns:
        Configured structlog logger

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("api_request", method="GET", endpoint="/weather/latest")
        >>> logger.error("database_error", error="Connection failed", table="weather_data")
    """
    return structlog.get_logger(name)  # type: ignore[return-value]


# Context managers for request tracking
class LogContext:
    """Context manager for adding context to all logs within a scope"""

    def __init__(self, **context: Any):
        """
        Initialize log context

        Args:
            **context: Key-value pairs to add to all logs in this context

        Example:
            >>> with LogContext(request_id="abc123", user_id="user456"):
            ...     logger.info("processing_request")
            # Output includes request_id and user_id automatically
        """
        self.context = context
        self.token: Mapping[str, BoundVarsToken] | None = None

    def __enter__(self) -> "LogContext":
        self.token = structlog.contextvars.bind_contextvars(**self.context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        structlog.contextvars.unbind_contextvars(*self.context.keys())


# Logging utilities
def log_api_request(
    logger: structlog.stdlib.BoundLogger,
    method: str,
    endpoint: str,
    params: dict[str, Any] | None = None,
    status_code: int | None = None,
    duration_ms: float | None = None,
) -> None:
    """
    Log an API request with standard fields

    Args:
        logger: Structlog logger instance
        method: HTTP method (GET, POST, etc.)
        endpoint: API endpoint path
        params: Optional request parameters
        status_code: Optional response status code
        duration_ms: Optional request duration in milliseconds
    """
    log_data: dict[str, Any] = {
        "event": "api_request",
        "method": method,
        "endpoint": endpoint,
    }

    if params:
        log_data["params"] = params
    if status_code:
        log_data["status_code"] = status_code
    if duration_ms is not None:
        log_data["duration_ms"] = round(duration_ms, 2)

    # Log as info if successful, warning if client error, error if server error
    if status_code:
        if status_code >= 500:
            logger.error(**log_data)  # type: ignore[arg-type]
        elif status_code >= 400:
            logger.warning(**log_data)  # type: ignore[arg-type]
        else:
            logger.info(**log_data)  # type: ignore[arg-type]
    else:
        logger.info(**log_data)  # type: ignore[arg-type]


def log_database_operation(
    logger: structlog.stdlib.BoundLogger,
    operation: str,
    table: str,
    records: int | None = None,
    duration_ms: float | None = None,
    error: str | None = None,
) -> None:
    """
    Log a database operation with standard fields

    Args:
        logger: Structlog logger instance
        operation: Database operation (SELECT, INSERT, UPDATE, etc.)
        table: Table name
        records: Optional number of records affected
        duration_ms: Optional operation duration in milliseconds
        error: Optional error message
    """
    log_data: dict[str, Any] = {
        "event": "database_operation",
        "operation": operation,
        "table": table,
    }

    if records is not None:
        log_data["records"] = records
    if duration_ms is not None:
        log_data["duration_ms"] = round(duration_ms, 2)
    if error:
        log_data["error"] = error
        logger.error(**log_data)  # type: ignore[arg-type]
    else:
        logger.info(**log_data)  # type: ignore[arg-type]


def log_cli_command(
    logger: structlog.stdlib.BoundLogger,
    command: str,
    args: dict[str, Any] | None = None,
    success: bool = True,
    error: str | None = None,
    duration_ms: float | None = None,
) -> None:
    """
    Log a CLI command execution

    Args:
        logger: Structlog logger instance
        command: CLI command name
        args: Optional command arguments
        success: Whether command succeeded
        error: Optional error message
        duration_ms: Optional command duration in milliseconds
    """
    log_data: dict[str, Any] = {
        "event": "cli_command",
        "command": command,
        "success": success,
    }

    if args:
        log_data["args"] = args
    if error:
        log_data["error"] = error
    if duration_ms is not None:
        log_data["duration_ms"] = round(duration_ms, 2)

    if success:
        logger.info(**log_data)  # type: ignore[arg-type]
    else:
        logger.error(**log_data)  # type: ignore[arg-type]


# Initialize logging on module import with sensible defaults
# Can be reconfigured by calling configure_logging() with different settings
configure_logging(level="INFO", json_logs=True)
