# Claude Code Guidelines

**Project:** Weather Dashboard Application
**Stack:** FastAPI + React + TypeScript + DuckDB
**Last Updated:** January 2026

---

## ⚡ Quick Start Checklist

Before starting ANY task:

- [ ] **Check git branch**: `git branch --show-current` (must NOT be `main`)
- [ ] **Create feature branch** if on main: `git checkout -b feature/descriptive-name`
- [ ] **Load relevant standards** (see "When to Load Docs" below)
- [ ] **Understand requirements** (ask clarifying questions if unclear)

---

## 🚨 Critical Non-Negotiables

These rules apply to EVERY task. Violations will break CI/CD:

### 1. Git Workflow
**NEVER commit directly to main. ALWAYS use feature branches.**

```bash
# Before ANY code changes
git branch --show-current              # Check current branch

# If on main, immediately create feature branch
git checkout -b feature/my-feature     # Use descriptive name

# Work, commit, push
git add .
git commit -m "Add: Clear description"
git push -u origin feature/my-feature
```

**Branch naming:**
- `feature/` - New functionality
- `bugfix/` - Bug fixes
- `refactor/` - Code improvements
- `docs/` - Documentation only
- `chore/` - Dependencies, config

### 2. Type Safety
**ADD type hints (Python) and types (TypeScript) to ALL code.**

```python
# Python - REQUIRED
def process_weather(
    data: WeatherData,
    start_date: datetime
) -> List[ProcessedReading]:
    ...
```

```typescript
// TypeScript - REQUIRED
interface WeatherProps {
  data: WeatherReading[];
  onUpdate: (data: WeatherReading[]) => void;
}
```

### 3. Testing
**WRITE tests for all new features and bug fixes.**

```bash
# Before pushing
pytest tests/ -v           # Python tests must pass
npm test                   # TypeScript tests must pass
```

### 4. Accessibility
**ENSURE keyboard navigation works and screen readers announce content.**

Every UI component checklist:
- [ ] Keyboard navigation (Tab, Enter, Escape)
- [ ] Screen reader announces correctly
- [ ] Color contrast ≥ 4.5:1
- [ ] Touch targets ≥ 44×44px

---

## 📚 When to Load Specialized Documentation

**Before implementing, load the relevant documentation:**

### Decision Tree

```
What are you working on?

├─ API Endpoints (FastAPI routes)
│  └─ READ: docs/standards/API-STANDARDS.md
│  └─ THEN: Check docs/examples/api-patterns.md
│
├─ UI Components (React)
│  └─ READ: docs/standards/ACCESSIBILITY.md
│  └─ AND: docs/standards/REACT-STANDARDS.md
│  └─ THEN: Check docs/examples/component-patterns.md
│
├─ Database Queries (DuckDB)
│  └─ READ: docs/standards/DATABASE-PATTERNS.md
│  └─ THEN: Check docs/examples/query-patterns.md
│
├─ Tests (pytest/Vitest)
│  └─ READ: docs/standards/TESTING.md
│
├─ Security-sensitive code
│  └─ READ: docs/standards/SECURITY.md
│
├─ Performance optimization
│  └─ READ: docs/guides/PERFORMANCE.md
│
└─ Architecture decisions
   └─ READ: docs/architecture/overview.md
   └─ DISCUSS: Before implementing major changes
```

### Quick Reference Table

| Working on... | Load these docs (in order) | Critical checks |
|---------------|---------------------------|-----------------|
| **API endpoint** | API-STANDARDS.md → api-patterns.md | Type hints, error handling, tests |
| **UI component** | ACCESSIBILITY.md → REACT-STANDARDS.md | Keyboard nav, screen reader, contrast |
| **Database query** | DATABASE-PATTERNS.md → query-patterns.md | Parameterized queries, indexes |
| **Tests** | TESTING.md | Fixtures, mocks, assertions |
| **Deployment** | docs/technical/deployment-guide.md | Docker, env vars |

---

## 🎯 Model Selection Guide

Choose the right Claude model for your task:

| Task Complexity | Model | Cost | Use When |
|-----------------|-------|------|----------|
| **Simple** | Haiku 4.5 | 1x | Typo fixes, file searches, boilerplate |
| **Standard** | Sonnet 4.5 | 3-5x | Most development tasks (DEFAULT) |
| **Complex** | Opus 4 | 15-20x | Architecture, schema changes, major refactors |

**Default rule:** Use Sonnet 4.5 unless you have a specific reason for another model.

---

## 🔧 Essential Commands

### Development

```bash
# Backend (Python)
uvicorn weather_app.web.app:create_app --factory --reload  # Start dev server
pytest tests/ -v                              # Run tests
black weather_app/                            # Format code
ruff check --fix weather_app/                 # Lint and auto-fix
mypy weather_app/                             # Type check

# Frontend (TypeScript)
cd web && npm run dev                         # Start dev server
npm test                                      # Run tests
npm run lint:fix                              # Lint and auto-fix
npm run test:a11y                             # Accessibility tests

# Database
duckdb weather.db                             # Open database CLI
```

### Git Workflow

```bash
git branch --show-current                     # Check current branch
git checkout -b feature/my-feature            # Create feature branch
git add .                                     # Stage changes
git commit -m "Add: Description"              # Commit with clear message
git push -u origin feature/my-feature         # Push and set upstream
```

### Pre-push Checklist

```bash
# Run ALL checks before pushing
black weather_app/ && \
ruff check --fix weather_app/ && \
mypy weather_app/ && \
pytest tests/ -v && \
cd web && npm run lint:fix && npm test
```

---

## 📋 Quick Reference Patterns

### Error Handling (FastAPI)

```python
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

@app.get("/api/weather/latest")
async def get_latest_weather() -> WeatherData:
    try:
        result = await db.query_latest()
        if not result:
            raise HTTPException(
                status_code=404,
                detail="No weather data found"
            )
        return WeatherData(**result)
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
```

### Component Props (React)

```typescript
interface WeatherChartProps {
  data: WeatherReading[];
  dateRange: DateRange;
  onRangeChange: (range: DateRange) => void;
  isLoading?: boolean;
}

export function WeatherChart({
  data,
  dateRange,
  onRangeChange,
  isLoading = false
}: WeatherChartProps) {
  // Implementation
}
```

### Accessible Button (React)

```typescript
import { useButton } from '@react-aria/button';

function ActionButton({ onPress, children }) {
  const ref = React.useRef();
  const { buttonProps } = useButton({ onPress }, ref);

  return (
    <button
      {...buttonProps}
      ref={ref}
      className="btn"
    >
      {children}
    </button>
  );
}
```

### Database Query (DuckDB)

```python
def get_weather_range(
    start: datetime,
    end: datetime,
    station_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Query weather data with parameterized SQL."""
    query = """
        SELECT *
        FROM weather_data
        WHERE timestamp BETWEEN ? AND ?
        AND (? IS NULL OR station_id = ?)
        ORDER BY timestamp
    """
    return conn.execute(
        query,
        [start, end, station_id, station_id]
    ).fetchall()
```

---

## 🐛 Common Mistakes & Fixes

### Forgot to Create Feature Branch

**Symptom:** Already made commits on main

**Fix:**
```bash
git branch feature/my-feature    # Create branch with current work
git reset --hard origin/main     # Reset main to remote state
git checkout feature/my-feature  # Switch to feature branch
```

### Type Hints Missing

**Symptom:** `mypy` errors in CI

**Fix:**
```bash
mypy weather_app/                # Run locally to see errors
# Add type hints to flagged functions
# Re-run until clean
```

### Accessibility Tests Failing

**Symptom:** axe-core violations in CI

**Fix:**
1. Open `docs/standards/ACCESSIBILITY.md`
2. Review WCAG 2.2 checklist
3. Fix violations (usually missing ARIA labels or keyboard handlers)
4. Run `npm run test:a11y` locally to verify

### Tests Failing Locally

**Symptom:** Tests pass on your machine, fail in CI

**Fix:**
```bash
# Clear test cache
pytest --cache-clear

# Use same Python version as CI (3.11+)
python --version

# Check for hardcoded paths or timing issues
```

---

## 💡 Working with Claude Code

### Start of Session

1. **Review requirements** - Understand what you're building
2. **Load relevant docs** - Use decision tree above
3. **Check existing patterns** - Look for similar code in project
4. **Ask clarifying questions** - Better to ask than assume

### During Implementation

1. **Implement incrementally** - Small changes, test frequently
2. **Commit often** - Clear commit messages
3. **Explain decisions** - When multiple approaches exist
4. **Follow established patterns** - Consistency over cleverness

### Before Finishing

1. **Run all checks** - Pre-push checklist above
2. **Test manually** - Actually use the feature
3. **Update docs** - If patterns changed
4. **Verify accessibility** - Keyboard navigation + screen reader

### Effective Communication Patterns

```bash
# ❌ Too vague
"Fix the frontend"

# ✅ Specific and actionable
"Fix temperature chart not displaying data from /api/weather/range endpoint.
Error in console: 'Cannot read property timestamp of undefined'"

# ❌ Missing context
"Add validation"

# ✅ Complete context
"Add validation to weather API endpoint to reject dates in the future.
Return 400 with message 'Future dates not allowed'. See API-STANDARDS.md
section 3 for error response format."
```

---

## 📖 Documentation Navigation

### Core References

- **This file (CLAUDE.md)** - Start here for every task
- **docs/standards/README.md** - Index of all standards
- **docs/README.md** - Full documentation navigation

### Detailed Standards (Load contextually)

- **docs/standards/API-STANDARDS.md** - FastAPI patterns and requirements
- **docs/standards/REACT-STANDARDS.md** - React component patterns
- **docs/standards/ACCESSIBILITY.md** - WCAG 2.2 compliance (REQUIRED for UI)
- **docs/standards/DATABASE-PATTERNS.md** - DuckDB best practices
- **docs/standards/TESTING.md** - Test strategies and patterns
- **docs/standards/SECURITY.md** - Security requirements

### Examples & Recipes

- **docs/examples/api-patterns.md** - Common API implementations
- **docs/examples/component-patterns.md** - React component recipes
- **docs/examples/query-patterns.md** - DuckDB query examples

### Architecture & Planning

- **docs/architecture/overview.md** - System design and tech stack
- **docs/architecture/decisions/** - Architecture Decision Records (ADRs)

### Guides & Tutorials

- **docs/guides/adding-endpoints.md** - Step-by-step API guide
- **docs/guides/adding-components.md** - Step-by-step UI guide
- **docs/guides/deployment.md** - Deployment instructions

---

## ✅ Definition of Done

A feature is complete when ALL of these are true:

- [ ] Code follows style guidelines (Black, ESLint)
- [ ] Type hints/types added (Python, TypeScript)
- [ ] Tests written and passing (`pytest`, `npm test`)
- [ ] Accessibility checklist complete (for UI features)
- [ ] Error handling implemented (proper HTTP status codes)
- [ ] Documentation updated (if new patterns introduced)
- [ ] Pre-push checks pass (see Essential Commands)
- [ ] Feature branch created (not on main)
- [ ] Code committed with clear messages
- [ ] Ready for PR review

---

## 🎓 Learning Resources

When you need more context:

1. **Project docs** - Always start here for established patterns
2. **Official docs** - Framework-specific questions
   - FastAPI: https://fastapi.tiangolo.com/
   - React: https://react.dev/
   - DuckDB: https://duckdb.org/docs/
   - React Aria: https://react-spectrum.adobe.com/react-aria/
   - Victory: https://commerce.nearform.com/open-source/victory/

3. **Accessibility** - WCAG and implementation
   - WCAG 2.2: https://www.w3.org/TR/WCAG22/
   - WebAIM: https://webaim.org/

---

## 🚀 Project Status

**Current Phase:** Phase 3 (APScheduler integration, accessibility improvements)
**Active Development:** Multi-station support, real-time updates
**Next Phase:** Web-based configuration UI

**Recent updates:**
- APScheduler integration complete (automated data fetching)
- Victory Charts migration complete (accessible charts)
- React Aria integration (accessible components)
- DuckDB optimization (10-100x faster than SQLite)

---

## 📞 Questions?

- **Unclear requirements?** Ask before implementing
- **Pattern not documented?** Check similar code in project
- **Need architectural guidance?** Read docs/architecture/overview.md first
- **Major decision needed?** Discuss before implementing

**Remember:** It's better to ask questions than to build the wrong thing.

---

**This is your starting point for every Claude Code session. Load specialized documentation as needed based on your task.**
