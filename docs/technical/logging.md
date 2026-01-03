# Structured Logging with structlog

This document describes the structured logging implementation using `structlog` throughout the Weather App.

## Overview

The application uses **structlog** for structured JSON logging, providing:

- **Machine-readable logs**: All logs are output as JSON for easy parsing and analysis
- **Consistent structure**: Standard fields across all log messages
- **Contextual information**: Automatic inclusion of timestamp, log level, source location
- **Performance metrics**: Duration tracking for operations
- **Error tracking**: Structured error information with stack traces

## Benefits

1. **Searchability**: JSON logs can be easily searched and filtered
2. **Monitoring**: Log aggregation tools (ELK, Datadog, CloudWatch) can parse JSON natively
3. **Debugging**: Rich context makes troubleshooting easier
4. **Performance Analysis**: Duration metrics help identify bottlenecks
5. **Audit Trail**: Structured logs provide clear audit trails for operations

## Log Output Format

All logs are output as JSON with standard fields:

```json
{
  "event": "api_request",
  "level": "info",
  "timestamp": "2026-01-03T16:40:43.011368Z",
  "filename": "routes.py",
  "lineno": 70,
  "func_name": "get_weather_data",
  "method": "GET",
  "endpoint": "/weather",
  "status_code": 200,
  "duration_ms": 12.34
}
```

### Standard Fields

Every log message includes:

- `event`: Event name (e.g., "api_request", "database_operation", "cli_command")
- `level`: Log level ("info", "warning", "error", "critical")
- `timestamp`: ISO 8601 timestamp with timezone
- `filename`: Source file that generated the log
- `lineno`: Line number in source file
- `func_name`: Function name that generated the log

### Custom Fields

Additional fields vary by event type:

#### API Requests
```json
{
  "event": "api_request",
  "method": "GET",
  "endpoint": "/weather/latest",
  "params": {"limit": 100, "offset": 0},
  "status_code": 200,
  "duration_ms": 15.67
}
```

#### Database Operations
```json
{
  "event": "database_operation",
  "operation": "SELECT",
  "table": "weather_data",
  "records": 100,
  "duration_ms": 8.23
}
```

#### CLI Commands
```json
{
  "event": "cli_command",
  "command": "fetch",
  "args": {"limit": 1},
  "success": true,
  "duration_ms": 1234.56
}
```

#### Errors
```json
{
  "event": "fetch_failed",
  "level": "error",
  "reason": "missing_credentials",
  "error": "API key not found",
  "duration_ms": 5.12
}
```

## Usage

### Basic Logging

```python
from weather_app.logging_config import get_logger

logger = get_logger(__name__)

# Info message
logger.info("operation_started", user_id="123", action="fetch_data")

# Warning message
logger.warning("rate_limit_approaching", remaining=10, total=1000)

# Error message
logger.error("operation_failed", error="Connection timeout", retry_count=3)
```

### Helper Functions

The `logging_config` module provides helper functions for common patterns:

#### API Request Logging

```python
from weather_app.logging_config import log_api_request

log_api_request(
    logger,
    method="GET",
    endpoint="/weather/latest",
    params={"limit": 100},
    status_code=200,
    duration_ms=15.67
)
```

#### Database Operation Logging

```python
from weather_app.logging_config import log_database_operation

log_database_operation(
    logger,
    operation="INSERT",
    table="weather_data",
    records=50,
    duration_ms=25.34
)
```

#### CLI Command Logging

```python
from weather_app.logging_config import log_cli_command

log_cli_command(
    logger,
    command="backfill",
    args={"start": "2024-01-01", "end": "2024-01-31"},
    success=True,
    duration_ms=45000.0
)
```

### Context Managers

Add context to all logs within a scope:

```python
from weather_app.logging_config import LogContext

with LogContext(request_id="abc123", user_id="user456"):
    logger.info("processing_request")
    # All logs in this block will include request_id and user_id
```

## Configuration

### Default Configuration

The logging system is auto-configured on module import with:

- **Level**: INFO
- **Format**: JSON
- **Output**: stdout

### Custom Configuration

Reconfigure logging at runtime:

```python
from weather_app.logging_config import configure_logging

# Enable debug logging
configure_logging(level="DEBUG", json_logs=True)

# Use human-readable format for development
configure_logging(level="INFO", json_logs=False)
```

### Environment Variables

Control logging via environment variables:

```bash
# Set log level
export LOG_LEVEL=DEBUG

# Disable JSON logs (development mode)
export JSON_LOGS=false
```

## Integration with Monitoring Tools

### ELK Stack (Elasticsearch, Logstash, Kibana)

Logstash configuration:

```ruby
input {
  file {
    path => "/var/log/weather-app/*.log"
    codec => json
  }
}

filter {
  # Logs are already JSON - no parsing needed
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "weather-app-%{+YYYY.MM.dd}"
  }
}
```

### Datadog

```bash
# Install Datadog agent
# Configure log collection in /etc/datadog-agent/conf.d/weather_app.yaml

logs:
  - type: file
    path: /var/log/weather-app/*.log
    service: weather-app
    source: python
    sourcecategory: sourcecode
```

### CloudWatch Logs

```python
import watchtower
import logging

# Add CloudWatch handler
logger = logging.getLogger()
logger.addHandler(watchtower.CloudWatchLogHandler(
    log_group="/weather-app/production"
))
```

## Log Levels

### INFO
Normal operations:
- API requests (2xx responses)
- Successful database queries
- CLI command completions
- Progress updates

### WARNING
Recoverable issues:
- API rate limits hit
- Client errors (4xx responses)
- Retryable failures
- Deprecated feature usage

### ERROR
Failures requiring attention:
- Server errors (5xx responses)
- Database connection failures
- Command failures
- Unhandled exceptions

### CRITICAL
System-level failures:
- Service unavailable
- Data corruption
- Security breaches

## Performance Considerations

### Minimal Overhead

Structured logging adds negligible overhead:
- **~0.1ms** per log message
- **Async logging** available for high-throughput scenarios
- **Lazy evaluation** of expensive fields

### Production Recommendations

1. **Set appropriate log level**: Use INFO in production, DEBUG only for troubleshooting
2. **Rotate logs**: Use `logrotate` to manage log file size
3. **Sample high-volume events**: For high-traffic endpoints, sample 10% of requests
4. **Use async logging**: For critical paths, consider async handlers

### Log Rotation

Example logrotate configuration:

```
/var/log/weather-app/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0644 weather-app weather-app
    sharedscripts
    postrotate
        systemctl reload weather-app
    endscript
}
```

## Troubleshooting

### Logs Not Appearing

**Problem**: No log output

**Solutions**:
1. Check log level: `configure_logging(level="DEBUG")`
2. Verify logger creation: `logger = get_logger(__name__)`
3. Check output stream: Logs go to stdout by default

### Malformed JSON

**Problem**: JSON parsing errors in log aggregation

**Solutions**:
1. Ensure `json_logs=True` in configuration
2. Catch and log exceptions properly:
   ```python
   try:
       operation()
   except Exception as e:
       logger.error("operation_failed", error=str(e), exc_info=True)
   ```

### Performance Issues

**Problem**: Logging causing slowdowns

**Solutions**:
1. Reduce log level to WARNING or ERROR
2. Sample high-volume events
3. Use async logging handlers
4. Avoid logging large payloads

## Examples

### CLI Command with Logging

```python
import time
from weather_app.logging_config import get_logger, log_cli_command

logger = get_logger(__name__)

@cli.command()
def my_command():
    start_time = time.time()

    try:
        logger.info("command_started", command="my_command")

        # Do work
        result = perform_operation()

        duration_ms = (time.time() - start_time) * 1000
        log_cli_command(logger, "my_command", success=True, duration_ms=duration_ms)

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        log_cli_command(logger, "my_command", success=False,
                       error=str(e), duration_ms=duration_ms)
        raise
```

### API Endpoint with Logging

```python
import time
from weather_app.logging_config import get_logger, log_api_request

logger = get_logger(__name__)

@app.get("/api/endpoint")
def my_endpoint(request: Request, limit: int = 100):
    start_time = time.time()

    try:
        result = query_database(limit=limit)

        duration_ms = (time.time() - start_time) * 1000
        log_api_request(logger, "GET", "/api/endpoint",
                       params={"limit": limit}, status_code=200,
                       duration_ms=duration_ms)

        return result

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        log_api_request(logger, "GET", "/api/endpoint",
                       params={"limit": limit}, status_code=500,
                       duration_ms=duration_ms)
        raise HTTPException(status_code=500, detail=str(e))
```

### Database Operation with Logging

```python
import time
from weather_app.logging_config import get_logger, log_database_operation

logger = get_logger(__name__)

def insert_records(records):
    start_time = time.time()

    try:
        # Perform database operation
        result = db.insert(records)

        duration_ms = (time.time() - start_time) * 1000
        log_database_operation(logger, "INSERT", "weather_data",
                              records=len(records), duration_ms=duration_ms)

        return result

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        log_database_operation(logger, "INSERT", "weather_data",
                              duration_ms=duration_ms, error=str(e))
        raise
```

## Best Practices

1. **Use consistent event names**: `operation_started`, `operation_completed`, `operation_failed`
2. **Include context**: Add relevant fields like IDs, counts, durations
3. **Log at boundaries**: API requests, database operations, external calls
4. **Avoid sensitive data**: Never log passwords, API keys, PII
5. **Use appropriate levels**: INFO for normal ops, WARNING for issues, ERROR for failures
6. **Track performance**: Always include `duration_ms` for operations
7. **Log exceptions**: Use `exc_info=True` for full stack traces
8. **Keep messages concise**: Use fields for data, not long text messages

## Security Considerations

### Don't Log Sensitive Data

❌ **Never log**:
- Passwords or password hashes
- API keys or secrets
- Credit card numbers
- Personal Identifiable Information (PII)
- Session tokens

✅ **Safe to log**:
- Request IDs
- User IDs (if not considered PII)
- Operation types
- Counts and durations
- Error types (not sensitive details)

### Redacting Sensitive Fields

```python
def sanitize_log_data(data):
    """Remove sensitive fields before logging"""
    sensitive_keys = ['password', 'api_key', 'secret', 'token']
    return {k: v for k, v in data.items() if k not in sensitive_keys}

logger.info("user_data", **sanitize_log_data(user_dict))
```

## Future Enhancements

1. **Distributed Tracing**: Add OpenTelemetry integration for request tracing
2. **Log Sampling**: Implement probabilistic sampling for high-volume events
3. **Metrics Export**: Export metrics to Prometheus from log data
4. **Alert Rules**: Define alerting rules based on log patterns
5. **Log Analysis**: ML-based anomaly detection on log patterns

---

**Last Updated**: 2026-01-03
**Status**: Production Ready
**Maintainer**: Weather App Team
