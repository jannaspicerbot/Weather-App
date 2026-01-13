# Security Standards

**Weather App Security Requirements**
**When to load:** Security-sensitive code, authentication, data handling
**Priority:** CRITICAL - Security rules are non-negotiable

---

## Table of Contents

1. [Security Philosophy](#security-philosophy)
2. [Authentication & Authorization](#authentication--authorization)
3. [Input Validation](#input-validation)
4. [SQL Injection Prevention](#sql-injection-prevention)
5. [XSS Prevention](#xss-prevention)
6. [CSRF Protection](#csrf-protection)
7. [Secrets Management](#secrets-management)
8. [API Security](#api-security)
9. [Data Privacy](#data-privacy)
10. [Security Checklist](#security-checklist)

---

## Security Philosophy

### Core Principles

**1. Defense in Depth**
- Multiple layers of security
- Never rely on single protection mechanism
- Assume every layer can fail

**2. Principle of Least Privilege**
- Grant minimum necessary permissions
- Restrict access by default
- Escalate only when needed

**3. Fail Securely**
- Errors should not expose sensitive data
- Default to denying access
- Log security events for audit

**4. Never Trust User Input**
- Validate everything from client
- Sanitize all inputs
- Use parameterized queries
- Encode outputs

---

## Authentication & Authorization

### JWT Authentication

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os

# ✅ DO: Use environment variables for secrets
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

if not SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY environment variable not set")

security = HTTPBearer()

def create_access_token(data: dict) -> str:
    """
    Create JWT access token.

    ✅ Includes expiration
    ✅ Signs with secret key
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Validate JWT token and return user.

    Raises:
        HTTPException: 401 if token invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        # Verify token not expired (jwt.decode checks this automatically)
        return {"user_id": user_id}

    except JWTError:
        raise credentials_exception

# Usage in endpoints
@app.get("/api/weather/protected")
async def protected_endpoint(
    current_user: dict = Depends(get_current_user)
):
    """Only accessible with valid JWT token."""
    return {"message": f"Hello {current_user['user_id']}"}
```

### API Key Authentication

```python
from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader
import secrets

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# ✅ DO: Store hashed API keys in database
def verify_api_key(api_key: str) -> bool:
    """Verify API key against database."""
    # In production: query database for hashed key
    stored_hash = get_api_key_hash_from_db(api_key)
    return secrets.compare_digest(api_key, stored_hash)

async def get_api_key(api_key: str = Security(api_key_header)):
    """Validate API key."""
    if not api_key or not verify_api_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API key"
        )
    return api_key

# Usage
@app.get("/api/external/weather")
async def external_api(api_key: str = Depends(get_api_key)):
    """External API endpoint requiring API key."""
    return {"data": "sensitive information"}
```

### Password Hashing

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ✅ DO: Hash passwords with bcrypt
def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)

# ❌ DON'T: Store plain text passwords
def bad_store_password(password: str):
    """NEVER DO THIS!"""
    db.execute("INSERT INTO users (password) VALUES (?)", [password])

# ✅ DO: Hash before storing
def good_store_password(password: str):
    """Always hash passwords."""
    hashed = hash_password(password)
    db.execute("INSERT INTO users (password_hash) VALUES (?)", [hashed])
```

---

## Input Validation

### Request Validation with Pydantic

```python
from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional
import re

class StationInput(BaseModel):
    """Validated station input."""
    station_id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        regex="^[A-Za-z0-9_-]+$"  # Alphanumeric only
    )
    name: str = Field(..., min_length=1, max_length=200)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

    @validator('station_id')
    def validate_station_id(cls, v):
        """Additional validation for station ID."""
        # Prevent path traversal
        if '../' in v or '..' in v:
            raise ValueError("Invalid station ID format")
        return v

class WeatherReadingInput(BaseModel):
    """Validated weather input."""
    temperature_f: float = Field(..., ge=-150, le=150)
    humidity: int = Field(..., ge=0, le=100)
    wind_speed_mph: Optional[float] = Field(None, ge=0, le=200)

    @validator('temperature_f')
    def validate_temperature(cls, v):
        """Sanity check temperature."""
        if v < -150 or v > 150:
            raise ValueError("Temperature out of realistic range")
        return v

# Usage
@app.post("/api/station")
async def create_station(station: StationInput):
    """Pydantic validates input automatically."""
    # Input already validated, safe to use
    await db.insert_station(station.dict())
    return {"success": True}
```

### Sanitization

```python
import bleach
import html

# ✅ DO: Sanitize HTML input
def sanitize_html_input(text: str) -> str:
    """Remove dangerous HTML tags and attributes."""
    allowed_tags = ['p', 'br', 'strong', 'em']
    allowed_attrs = {}

    cleaned = bleach.clean(
        text,
        tags=allowed_tags,
        attributes=allowed_attrs,
        strip=True
    )
    return cleaned

# ✅ DO: Escape HTML output
def escape_for_html(text: str) -> str:
    """Escape special characters for HTML output."""
    return html.escape(text)

# Usage
@app.post("/api/comment")
async def post_comment(comment: str):
    """Sanitize user-provided HTML."""
    safe_comment = sanitize_html_input(comment)
    await db.insert_comment(safe_comment)
    return {"success": True}
```

---

## SQL Injection Prevention

### Parameterized Queries (CRITICAL)

```python
import duckdb

# ✅ DO: ALWAYS use parameterized queries
def get_weather_safe(conn, station_id: str):
    """Secure: Uses parameter binding."""
    query = "SELECT * FROM weather_data WHERE station_id = ?"
    return conn.execute(query, [station_id]).fetchall()

# ❌ DON'T: NEVER use string formatting
def get_weather_unsafe(conn, station_id: str):
    """VULNERABLE TO SQL INJECTION!"""
    query = f"SELECT * FROM weather_data WHERE station_id = '{station_id}'"
    return conn.execute(query).fetchall()

    # Attacker input: "'; DROP TABLE weather_data; --"
    # Results in: SELECT * FROM weather_data WHERE station_id = ''; DROP TABLE weather_data; --'

# ✅ DO: Parameterized with multiple values
def complex_query_safe(conn, station_id: str, start_date: str, end_date: str):
    """Multiple parameters, still secure."""
    query = """
        SELECT * FROM weather_data
        WHERE station_id = ?
          AND timestamp BETWEEN ? AND ?
    """
    return conn.execute(query, [station_id, start_date, end_date]).fetchall()

# ❌ DON'T: Even with "trusted" input
def query_with_trusted_input_still_bad(conn, station_id: str):
    """Still vulnerable! Always use parameters."""
    # Even if you think input is "safe", don't do this
    query = f"SELECT * FROM weather_data WHERE station_id = '{station_id}'"
    return conn.execute(query).fetchall()
```

### Dynamic Query Building (When Unavoidable)

```python
from typing import List, Dict, Any

def build_safe_dynamic_query(
    filters: Dict[str, Any],
    allowed_columns: List[str]
) -> tuple[str, List[Any]]:
    """
    Build dynamic query safely.

    ✅ Whitelist allowed columns
    ✅ Use parameterized values
    """
    # Whitelist validation
    for col in filters.keys():
        if col not in allowed_columns:
            raise ValueError(f"Invalid column: {col}")

    # Build WHERE clause
    conditions = []
    params = []

    for col, value in filters.items():
        conditions.append(f"{col} = ?")  # Column name from whitelist
        params.append(value)              # Value as parameter

    where_clause = " AND ".join(conditions) if conditions else "1=1"
    query = f"SELECT * FROM weather_data WHERE {where_clause}"

    return query, params

# Usage
allowed_columns = ['station_id', 'temperature_f', 'humidity']
filters = {'station_id': 'STATION001', 'humidity': 50}

query, params = build_safe_dynamic_query(filters, allowed_columns)
result = conn.execute(query, params).fetchall()
```

---

## XSS Prevention

### React Automatic Escaping

```typescript
// ✅ SAFE: React escapes by default
function WeatherDisplay({ stationName }: { stationName: string }) {
  // React automatically escapes stationName
  return <h1>{stationName}</h1>;
}

// ❌ DANGEROUS: dangerouslySetInnerHTML
function UnsafeDisplay({ html }: { html: string }) {
  // DON'T USE THIS unless HTML is trusted and sanitized!
  return <div dangerouslySetInnerHTML={{ __html: html }} />;
}

// ✅ SAFE: Sanitize before using dangerouslySetInnerHTML
import DOMPurify from 'dompurify';

function SafeHtmlDisplay({ html }: { html: string }) {
  const sanitized = DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ['p', 'br', 'strong', 'em'],
    ALLOWED_ATTR: []
  });

  return <div dangerouslySetInnerHTML={{ __html: sanitized }} />;
}
```

### URL Validation

```typescript
// ✅ DO: Validate URLs before using
function isValidUrl(url: string): boolean {
  try {
    const parsed = new URL(url);
    // Only allow http/https
    return ['http:', 'https:'].includes(parsed.protocol);
  } catch {
    return false;
  }
}

function ExternalLink({ href, children }: { href: string; children: React.ReactNode }) {
  if (!isValidUrl(href)) {
    console.error(`Invalid URL: ${href}`);
    return <span>{children}</span>; // Don't create link
  }

  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer" // Prevent window.opener access
    >
      {children}
    </a>
  );
}

// ❌ DON'T: Use javascript: URLs
// <a href="javascript:alert('XSS')">Click</a>
```

---

## CSRF Protection

### CSRF Tokens

```python
from fastapi import Cookie, HTTPException
from fastapi.responses import Response
import secrets

# Generate CSRF token
def generate_csrf_token() -> str:
    """Generate cryptographically secure token."""
    return secrets.token_urlsafe(32)

# Store in secure cookie
@app.get("/api/csrf-token")
async def get_csrf_token(response: Response):
    """Issue CSRF token."""
    token = generate_csrf_token()

    # Set secure cookie
    response.set_cookie(
        key="csrf_token",
        value=token,
        httponly=True,
        secure=True,  # HTTPS only
        samesite="strict"
    )

    return {"csrf_token": token}

# Validate CSRF token
async def verify_csrf_token(
    csrf_token: str = Header(...),
    csrf_cookie: str = Cookie(...)
):
    """Verify CSRF token matches cookie."""
    if not secrets.compare_digest(csrf_token, csrf_cookie):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid CSRF token"
        )

# Require for state-changing operations
@app.post("/api/weather/batch")
async def batch_insert(
    readings: List[WeatherReading],
    csrf: None = Depends(verify_csrf_token)
):
    """Protected by CSRF token."""
    await db.batch_insert(readings)
    return {"success": True}
```

### SameSite Cookies

```python
from fastapi import Response

@app.post("/login")
async def login(response: Response, username: str, password: str):
    """Set secure session cookie."""
    if verify_credentials(username, password):
        token = create_access_token({"sub": username})

        response.set_cookie(
            key="session_token",
            value=token,
            httponly=True,      # Not accessible to JavaScript
            secure=True,        # HTTPS only
            samesite="strict",  # CSRF protection
            max_age=3600        # 1 hour expiry
        )

        return {"success": True}

    raise HTTPException(status_code=401, detail="Invalid credentials")
```

---

## Secrets Management

### Environment Variables

```python
import os
from dotenv import load_dotenv

# ✅ DO: Load from environment
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
JWT_SECRET = os.getenv("JWT_SECRET_KEY")
API_KEY = os.getenv("EXTERNAL_API_KEY")

# Validate required secrets
if not JWT_SECRET:
    raise ValueError("JWT_SECRET_KEY not set in environment")

# ❌ DON'T: Hardcode secrets
DATABASE_URL = "postgresql://user:password@localhost/db"  # NEVER!
JWT_SECRET = "super-secret-key-123"  # NEVER!
```

### .env File (Never Commit!)

```bash
# .env (add to .gitignore!)
DATABASE_URL=postgresql://user:password@localhost/weather_db
JWT_SECRET_KEY=your-secret-key-here-use-secrets.token_urlsafe(32)
EXTERNAL_API_KEY=your-api-key-here

# Production: Use secret management service
# - AWS Secrets Manager
# - HashiCorp Vault
# - Azure Key Vault
```

### .gitignore (CRITICAL)

```bash
# .gitignore - MUST include:
.env
.env.local
.env.production
*.key
*.pem
secrets/
config/secrets.yaml

# Never commit:
# - API keys
# - Passwords
# - Private keys
# - JWT secrets
# - Database credentials
```

---

## API Security

### Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Apply rate limit
@app.get("/api/weather/latest")
@limiter.limit("100/minute")  # 100 requests per minute
async def get_latest(request: Request):
    """Rate-limited endpoint."""
    return await db.get_latest()

# Stricter limit for expensive operations
@app.post("/api/weather/batch")
@limiter.limit("10/minute")
async def batch_insert(request: Request, readings: List[WeatherReading]):
    """Strict rate limit for writes."""
    return await db.batch_insert(readings)
```

### CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

# ✅ DO: Restrict CORS in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://weather-app.com",
        "https://www.weather-app.com"
    ],  # Specific origins only
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Only needed methods
    allow_headers=["Content-Type", "Authorization"],
    max_age=3600  # Cache preflight for 1 hour
)

# ❌ DON'T: Allow all origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # DANGEROUS in production!
    allow_credentials=True
)
```

### Security Headers

```python
from fastapi import Response

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)

    # Prevent clickjacking
    response.headers["X-Frame-Options"] = "DENY"

    # Prevent MIME sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"

    # Enable XSS protection
    response.headers["X-XSS-Protection"] = "1; mode=block"

    # Content Security Policy
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline';"
    )

    # HSTS (HTTPS only)
    if request.url.scheme == "https":
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

    return response
```

---

## Data Privacy

### PII Handling

```python
from typing import Optional

class User(BaseModel):
    """User model with PII."""
    id: int
    email: str
    name: str
    ssn: Optional[str] = None  # Sensitive!

class UserPublic(BaseModel):
    """Public user model - no PII."""
    id: int
    name: str
    # email excluded
    # ssn excluded

# ✅ DO: Return sanitized model
@app.get("/api/users/{user_id}", response_model=UserPublic)
async def get_user(user_id: int):
    """Returns only non-sensitive fields."""
    user = await db.get_user(user_id)
    return user  # FastAPI filters to UserPublic fields

# ❌ DON'T: Log sensitive data
def bad_logging(user: User):
    """NEVER log PII!"""
    logger.info(f"User {user.email} with SSN {user.ssn}")  # BAD!

# ✅ DO: Sanitize logs
def good_logging(user: User):
    """Log only necessary data."""
    logger.info(f"User {user.id} accessed resource")  # Good
```

### Data Encryption

```python
from cryptography.fernet import Fernet
import base64

# Generate encryption key (store securely!)
# key = Fernet.generate_key()

def encrypt_sensitive_data(data: str, key: bytes) -> str:
    """Encrypt sensitive data before storage."""
    f = Fernet(key)
    encrypted = f.encrypt(data.encode())
    return base64.b64encode(encrypted).decode()

def decrypt_sensitive_data(encrypted_data: str, key: bytes) -> str:
    """Decrypt sensitive data after retrieval."""
    f = Fernet(key)
    decrypted = f.decrypt(base64.b64decode(encrypted_data))
    return decrypted.decode()

# Usage
encryption_key = os.getenv("ENCRYPTION_KEY").encode()

def store_api_key(user_id: int, api_key: str):
    """Store encrypted API key."""
    encrypted = encrypt_sensitive_data(api_key, encryption_key)
    db.execute(
        "UPDATE users SET encrypted_api_key = ? WHERE id = ?",
        [encrypted, user_id]
    )
```

---

## Security Checklist

### Before Every Deployment

**Authentication & Authorization:**
- [ ] JWT tokens have expiration
- [ ] Passwords hashed with bcrypt (not plain text)
- [ ] API keys stored hashed in database
- [ ] Sensitive endpoints require authentication
- [ ] Authorization checks on all protected resources

**Input Validation:**
- [ ] All inputs validated with Pydantic
- [ ] Regex patterns for string fields
- [ ] Range limits on numeric fields
- [ ] File uploads have size limits
- [ ] File types validated (not just extension)

**SQL Injection:**
- [ ] ALL queries use parameterized syntax
- [ ] No string formatting in queries (f-strings, %)
- [ ] Dynamic queries use column whitelists
- [ ] ORM/query builder used correctly

**XSS Prevention:**
- [ ] React default escaping used
- [ ] dangerouslySetInnerHTML avoided or sanitized
- [ ] URLs validated before use
- [ ] User input never executed as code

**API Security:**
- [ ] Rate limiting configured
- [ ] CORS restricted to specific origins
- [ ] Security headers added to responses
- [ ] HTTPS enforced in production

**Secrets Management:**
- [ ] No secrets in code
- [ ] .env in .gitignore
- [ ] Environment variables used
- [ ] Secrets rotated regularly

**Data Privacy:**
- [ ] PII not logged
- [ ] Sensitive data encrypted at rest
- [ ] Public APIs don't expose PII
- [ ] GDPR compliance considered

**Dependencies:**
- [ ] All packages up to date
- [ ] No known vulnerabilities (run `pip audit`)
- [ ] Dependencies pinned in requirements.txt
- [ ] Supply chain attacks considered

---

## Security Incident Response

### If Security Issue Discovered

1. **Immediate Actions:**
   - Document the issue (don't fix yet)
   - Assess impact and severity
   - Notify security team/stakeholders

2. **Containment:**
   - Disable affected features if critical
   - Rotate compromised credentials
   - Block malicious IPs if applicable

3. **Investigation:**
   - Review logs for exploitation
   - Identify affected users/data
   - Document timeline of events

4. **Remediation:**
   - Deploy fix to production
   - Verify fix resolves issue
   - Add tests to prevent regression

5. **Post-Incident:**
   - Notify affected users if required
   - Update security documentation
   - Conduct retrospective

---

## Security Resources

### Tools

- **Dependency Scanning:** `pip-audit`, `safety`
- **Code Analysis:** `bandit` (Python), `ESLint` (JavaScript)
- **Secrets Detection:** `truffleHog`, `git-secrets`
- **Penetration Testing:** OWASP ZAP, Burp Suite

### Best Practices

- **OWASP Top 10:** https://owasp.org/www-project-top-ten/
- **Security Checklist:** https://owasp.org/www-project-web-security-testing-guide/
- **CWE:** https://cwe.mitre.org/

---

**See also:**
- API-STANDARDS.md - API security patterns
- DATABASE-PATTERNS.md - Query security
- TESTING.md - Security testing

**Remember:** Security is not optional. Every line of code must consider security implications.
