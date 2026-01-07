# Contributing to Weather App

This guide explains how to contribute to the Weather App project, including documentation standards and development workflows.

---

## 📝 Documentation Strategy

### Documentation Structure

The project follows a **separation of concerns** approach for documentation:

```
docs/
├── README.md                      # Navigation guide
├── product/                       # Business & user-focused docs
│   └── requirements.md            # Product Requirements Document (PRD)
├── architecture/                  # System design & decisions
│   ├── overview.md                # High-level architecture
│   └── decisions/                 # Architecture Decision Records (ADRs)
│       ├── 001-fastapi-backend.md
│       ├── 002-duckdb-migration.md
│       ├── 003-typescript-frontend.md
│       ├── 004-docker-deployment.md
│       └── 005-retention-strategy.md
├── technical/                     # Implementation guides
│   ├── api-reference.md           # REST API documentation
│   ├── cli-reference.md           # CLI command reference
│   ├── database-schema.md         # DuckDB schema & queries
│   └── deployment-guide.md        # Installation & setup
└── archive/                       # Historical docs
```

### Documentation Types

#### 1. Product Documentation (docs/product/)

**Purpose:** Business context, user needs, project goals

**Content:**
- Executive summary
- Problem statement & Jobs-to-be-Done (JTBD)
- User personas
- Functional & non-functional requirements
- Success metrics & acceptance criteria
- Out of scope items
- Risk assessment

**Audience:** Product managers, stakeholders, business users

**When to update:** Per phase (quarterly) or when requirements change

#### 2. Architecture Documentation (docs/architecture/)

**Purpose:** System design, technology choices, trade-offs

**Content:**

**overview.md:**
- Technology stack with status table
- System diagrams (C4 model: Context → Container → Component)
- Data flow diagrams
- Database schema overview
- API design patterns
- Deployment architecture
- Performance benchmarks

**decisions/ (ADRs - Architecture Decision Records):**
- Context: Why this decision is needed
- Decision: What we're choosing
- Rationale: Why this over alternatives (with comparisons)
- Consequences: Positive, negative, neutral
- Alternatives Considered: What else was evaluated
- Validation: Success criteria & metrics

**Audience:** Architects, senior developers, technical leads

**When to update:**
- overview.md: Per phase (quarterly)
- ADRs: When making major technology decisions

#### 3. Technical Documentation (docs/technical/)

**Purpose:** Implementation details, usage guides, reference material

**Content:**

**api-reference.md:**
- All REST endpoints with request/response schemas
- Error codes and handling
- Code examples (TypeScript, Python, curl)
- OpenAPI schema reference

**cli-reference.md:**
- All CLI commands with arguments/options
- Usage examples
- Scheduling (cron, systemd, Task Scheduler)
- Troubleshooting common issues

**database-schema.md:**
- Table structures with column definitions
- Indexes and constraints
- Common query patterns
- Backup & restore procedures
- Performance characteristics

**deployment-guide.md:**
- Installation steps (Docker Compose, native)
- Configuration (environment variables)
- Automated data collection setup
- Monitoring & health checks
- Updates & maintenance
- Platform-specific notes

**Audience:** Developers, DevOps engineers, end users

**When to update:** Per release (monthly) or when implementation changes

### ADR (Architecture Decision Record) Pattern

**When to create an ADR:**
- Choosing between major technologies (database, framework, language)
- Significant architectural changes (data retention, deployment strategy)
- Decisions that affect multiple teams or future development
- Trade-offs that need to be documented for future reference

**ADR Template:**

```markdown
# ADR-XXX: Title

**Status:** 🟡 Proposed | ✅ Accepted | ❌ Rejected | ♻️ Superseded
**Date:** YYYY-MM-DD
**Deciders:** Names

## Context
What is the issue we're seeing that is motivating this decision?

## Decision
What is the change we're proposing?

## Rationale
Why this approach over alternatives?
- Include comparison tables
- Benchmarks where applicable
- Peer review feedback

## Consequences

### Positive
- ✅ Benefits of this decision

### Negative
- ⚠️ Drawbacks or limitations

### Neutral
- Other considerations

## Alternatives Considered
What other options were evaluated and why were they rejected?

## Validation
Success criteria and metrics to measure if this decision was correct.

## References
Links to relevant documentation, benchmarks, peer reviews.
```

**ADR Numbering:** Use sequential numbers (001, 002, 003...) in filename

**ADR Status:**
- 🟡 **Proposed:** Under discussion
- ✅ **Accepted:** Implemented and in use
- ❌ **Rejected:** Decided against
- ♻️ **Superseded:** Replaced by newer ADR (link to replacement)

### Documentation Best Practices

#### Separation of Concerns
- **DON'T** mix business requirements with technical implementation
- **DON'T** duplicate content across multiple docs
- **DO** link between related documents
- **DO** keep each document focused on its purpose

#### Writing Style
- **Product docs:** User-focused, business language, outcomes
- **Architecture docs:** Design-focused, trade-offs, diagrams
- **Technical docs:** Implementation-focused, code examples, how-to

#### Maintenance
- **Add changelog** at bottom of each document
- **Update version/date** when making changes
- **Move outdated docs** to archive/ directory
- **Keep archive/** for historical reference (never delete)

#### Navigation
- **docs/README.md** is the entry point
- Organize by **topic** (Installation, API, CLI, Database)
- Organize by **role** (End User, Developer, Architect)
- Provide **use case-based paths** ("I want to...")

### Code Comments

In addition to documentation files, write clear code comments:

- **Explain WHY**, not what (code shows what)
- **Document complex logic**
- **Add docstrings** to all functions
- **Keep comments updated** when code changes

```python
# ✅ GOOD - Explains reasoning
def calculate_dew_point(temp_f: float, humidity: float) -> float:
    """
    Calculate dew point using Magnus formula.

    Uses the simplified Magnus formula which is accurate for
    typical weather conditions (temp: -40°F to 122°F, RH: 1-100%).

    Args:
        temp_f: Temperature in Fahrenheit
        humidity: Relative humidity as percentage (0-100)

    Returns:
        Dew point temperature in Fahrenheit
    """
    # Convert F to C for formula
    temp_c = (temp_f - 32) * 5/9

    # Magnus formula constants
    a = 17.27
    b = 237.7

    # Calculate dew point in Celsius
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    dew_point_c = (b * alpha) / (a - alpha)

    # Convert back to Fahrenheit
    return (dew_point_c * 9/5) + 32

# ❌ BAD - Just restates code
def calc(t, h):
    # Convert to celsius
    tc = (t - 32) * 5/9
    # Do calculation
    result = some_formula(tc, h)
    # Return result
    return result
```

### Documentation Workflow

#### When Adding New Features
1. **Update requirements.md** if feature changes business goals
2. **Create ADR** if making architectural decision
3. **Update architecture/overview.md** if changing system design
4. **Update technical guides** (API, CLI, database) with new functionality
5. **Add examples** showing how to use the new feature

#### When Making Breaking Changes
1. **Create ADR** documenting the change and rationale
2. **Update all affected docs** (architecture, technical guides)
3. **Add migration guide** if users need to take action
4. **Archive old versions** to archive/ directory

#### When Deprecating Features
1. **Update docs** with deprecation notices
2. **Document migration path** to replacement
3. **Set timeline** for removal
4. **Keep docs** until feature is fully removed

---

## 🔒 Security Best Practices

### Git Pre-Commit Hook Installation

The repository includes a pre-commit hook that prevents accidentally committing sensitive files like `.env`. This provides an additional safety layer beyond `.gitignore`.

**To install the pre-commit hook:**

The hook source is version-controlled at `scripts/git-hooks/pre-commit`. To install it:

**Linux/macOS:**
```bash
# Copy the hook to your local .git/hooks directory
cp scripts/git-hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

**Windows:**
```powershell
# Copy the hook to your local .git/hooks directory
Copy-Item scripts/git-hooks/pre-commit .git/hooks/pre-commit
```

**What the hook does:**
- ❌ **Blocks** commits containing `.env` files
- ⚠️ **Warns** about other potential secret files (`secrets.py`, `*.pem`, `*.key`)
- 📝 **Provides** clear error messages and remediation steps

**Testing the hook:**
```bash
# This should be blocked by .gitignore, but the hook provides extra safety
git add .env
git commit -m "Test"
# Hook will prevent the commit if .env somehow gets staged
```

### Credential Management

**NEVER commit credentials to version control:**
- ✅ Use `.env` file for local development (already in `.gitignore`)
- ✅ Use `.env.example` for documentation (safe to commit)
- ✅ Rotate credentials before making repository public
- ❌ Never hardcode API keys in source code
- ❌ Never commit `.env` files

See [docs/technical/deployment-guide.md](technical/deployment-guide.md#credential-security) for complete credential rotation instructions.

---

**Last Updated:** January 6, 2026
