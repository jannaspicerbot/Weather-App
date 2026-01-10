# Weather App Documentation

Welcome to the Weather App documentation! This guide will help you navigate the different types of documentation available.

---

## 📖 Documentation Structure

```
docs/
├── README.md                          ← You are here
├── product/                           # Business & user-focused docs
│   └── requirements.md                # Product Requirements (PRD)
├── architecture/                      # System design & decisions
│   ├── overview.md                    # High-level architecture
│   └── decisions/                     # Architecture Decision Records (ADRs)
│       ├── 001-fastapi-backend.md
│       ├── 002-duckdb-migration.md
│       ├── 003-typescript-frontend.md
│       ├── 004-docker-deployment.md
│       ├── 005-retention-strategy.md
│       ├── 006-react-aria-components.md
│       └── 007-victory-charts.md
├── design/                            # UI/UX & accessibility standards
│   └── inclusive-design.md            # Accessibility & WCAG 2.2 AA compliance
├── technical/                         # Implementation guides
│   ├── api-reference.md               # REST API documentation
│   ├── cli-reference.md               # CLI command reference
│   ├── database-schema.md             # Database schema & queries
│   ├── deployment-guide.md            # Installation & deployment
│   └── github-actions-overview.md    # CI/CD automation & testing
└── archive/                           # Historical docs (Phase 1-2)
    ├── requirements.md.old
    ├── specifications.md.old
    ├── architecture.md.old
    └── peer-review.md
```

---

## 🚀 Quick Start

**New to the project?** Start here:

1. **[Product Requirements (PRD)](product/requirements.md)** - Understand what the Weather App does and why
2. **[Architecture Overview](architecture/overview.md)** - Learn how the system is designed
3. **[Deployment Guide](technical/deployment-guide.md)** - Install and run the application

**Already familiar?** Jump to:

- **[CLI Reference](technical/cli-reference.md)** - Command-line tool usage
- **[API Reference](technical/api-reference.md)** - REST API endpoints
- **[Database Schema](technical/database-schema.md)** - Database structure & queries

---

## 📚 Documentation Types

### 1. Product Documentation

**Purpose:** Business context, user needs, project goals

**[Product Requirements (PRD)](product/requirements.md)**
- Executive summary
- Problem statement & JTBD
- User personas
- Functional & non-functional requirements
- Success metrics
- Out of scope items

**When to read:** You want to understand the "why" behind the project

---

### 2. Architecture Documentation

**Purpose:** System design, technology choices, trade-offs

**[Architecture Overview](architecture/overview.md)**
- Technology stack
- System diagrams (C4 model)
- Data flow
- Database schema
- API design
- Deployment architecture
- Performance benchmarks

**[Architecture Decision Records (ADRs)](architecture/decisions/)**
- [ADR-001: FastAPI Backend](architecture/decisions/001-fastapi-backend.md) - Why FastAPI over Flask/Django
- [ADR-002: DuckDB Migration](architecture/decisions/002-duckdb-migration.md) - Why DuckDB over SQLite (10-100x faster)
- [ADR-003: TypeScript Frontend](architecture/decisions/003-typescript-frontend.md) - Why TypeScript over JavaScript
- [ADR-004: Docker Deployment](architecture/decisions/004-docker-deployment.md) - Why Docker Compose
- [ADR-005: Retention Strategy](architecture/decisions/005-retention-strategy.md) - Why 50-year full-resolution
- [ADR-006: React Aria Components](architecture/decisions/006-react-aria-components.md) - Why React Aria for accessibility
- [ADR-007: Victory Charts](architecture/decisions/007-victory-charts.md) - Why Victory over Recharts

**When to read:** You want to understand the "how" and "why" of technical decisions

---

### 3. Design Documentation

**Purpose:** UI/UX standards, accessibility, inclusive design

**[Inclusive Design Standards](design/inclusive-design.md)**
- WCAG 2.2 Level AA compliance
- HCD × WCAG strategic approach (POUR principles)
- Component accessibility guidelines
- Testing strategy (automated + manual)
- Recommended libraries and tools
- Plain language standards

**[Frontend Development Guidelines](design/frontend-guidelines.md)**
- Semantic design tokens (no hard-coded colors)
- TypeScript type safety requirements
- Component structure and file organization
- Data fetching patterns and API client
- Dashboard layout and chart specifications
- Responsive design standards
- Performance optimization

**[Design Token System](design/design-tokens.md)**
- Color palette architecture
- Semantic token mapping
- Victory Charts theme configuration
- Accessibility validation (WCAG 2.2 AA contrast)
- Palette testing and selection guide

**When to read:** You want to build accessible, inclusive user interfaces

---

### 4. Technical Documentation

**Purpose:** Implementation details, usage guides, reference material

**[API Reference](technical/api-reference.md)**
- REST API endpoints
- Request/response schemas
- Error codes
- Code examples (JavaScript, Python, curl)
- OpenAPI schema

**[CLI Reference](technical/cli-reference.md)**
- Command-line tool usage
- `init-db`, `fetch`, `backfill`, `info`, `export`
- Scheduling automation (cron, systemd, Task Scheduler)
- Troubleshooting

**[Database Schema](technical/database-schema.md)**
- Table structure
- Column definitions
- Query patterns
- Backup & restore
- Performance benchmarks

**[Deployment Guide](technical/deployment-guide.md)**
- Installation (Docker Compose, Native Python)
- Configuration
- Automated data collection
- Monitoring
- Updates & maintenance
- Platform-specific notes (Raspberry Pi, Windows, macOS)

**[CI/CD Automation](technical/github-actions-overview.md)**
- Streamlined GitHub Actions workflows (main-ci.yml, platform-builds.yml)
- Quality gates and testing requirements
- Local development testing
- Comprehensive troubleshooting guide
- Migration guide from old workflows

**When to read:** You want to install, configure, or use the application

---

## 🎯 Use Cases

### "I want to install and run the Weather App"

1. Read: [Deployment Guide](technical/deployment-guide.md)
2. Follow: Quick Start section (5 minutes with Docker)
3. Reference: [CLI Reference](technical/cli-reference.md) for data collection

### "I want to build a dashboard that displays weather data"

1. Read: [API Reference](technical/api-reference.md)
2. Review: Data models (WeatherReading, WeatherStats)
3. Use: Code examples (JavaScript/TypeScript, Python)

### "I want to understand why DuckDB was chosen over SQLite"

1. Read: [ADR-002: DuckDB Migration](architecture/decisions/002-duckdb-migration.md)
2. See: Performance benchmarks (10-100x speedup)
3. Understand: Trade-offs and alternatives considered

### "I want to contribute to the project"

1. Read: [Architecture Overview](architecture/overview.md) - System design
2. Read: All [ADRs](architecture/decisions/) - Understand technology choices
3. Reference: [Technical Guides](technical/) - Implementation details

### "I want to understand the business case for this project"

1. Read: [Product Requirements (PRD)](product/requirements.md)
2. Review: User personas, JTBD, success metrics
3. Understand: Goals and out-of-scope items

---

## 📦 Implementation Status

### Phase 1 ✅ Complete (December 2025)
- CLI with Click framework
- DuckDB database integration
- Ambient Weather API client
- Basic fetch and backfill commands

### Phase 2 ✅ Complete (January 2026)
- FastAPI backend with OpenAPI schema
- React + TypeScript frontend
- Interactive charts with Victory
- Docker Compose deployment
- End-to-end type safety
- **Current Version:** 2.0

### Phase 3 🔄 Planned (Q1 2026)
- Multi-station support
- Built-in scheduler (APScheduler)
- Web UI configuration
- User authentication
- Real-time WebSocket updates

---

## 🔍 Finding Information

### By Topic

| Topic | Document |
|-------|----------|
| **Installation** | [Deployment Guide](technical/deployment-guide.md) |
| **API Usage** | [API Reference](technical/api-reference.md) |
| **CLI Commands** | [CLI Reference](technical/cli-reference.md) |
| **Database Queries** | [Database Schema](technical/database-schema.md) |
| **System Design** | [Architecture Overview](architecture/overview.md) |
| **Technology Choices** | [ADRs](architecture/decisions/) |
| **Project Goals** | [Product Requirements](product/requirements.md) |
| **Frontend Development** | [Frontend Guidelines](design/frontend-guidelines.md) |
| **Dashboard Layout** | [Frontend Guidelines - Dashboard Section](design/frontend-guidelines.md#dashboard-layout--architecture) |
| **Accessibility** | [Inclusive Design](design/inclusive-design.md) |
| **Design Tokens** | [Design Token System](design/design-tokens.md) |

### By Role

| Role | Recommended Reading |
|------|---------------------|
| **End User** | [Deployment Guide](technical/deployment-guide.md), [CLI Reference](technical/cli-reference.md) |
| **Frontend Developer** | [Frontend Guidelines](design/frontend-guidelines.md), [API Reference](technical/api-reference.md), [Design Tokens](design/design-tokens.md) |
| **UI/UX Designer** | [Inclusive Design](design/inclusive-design.md), [Design Token System](design/design-tokens.md), [Frontend Guidelines](design/frontend-guidelines.md) |
| **Backend Developer** | [Database Schema](technical/database-schema.md), [ADRs](architecture/decisions/), [Architecture Overview](architecture/overview.md) |
| **DevOps Engineer** | [Deployment Guide](technical/deployment-guide.md), [ADR-004: Docker Deployment](architecture/decisions/004-docker-deployment.md) |
| **Product Manager** | [Product Requirements](product/requirements.md) |
| **Architect** | [Architecture Overview](architecture/overview.md), All [ADRs](architecture/decisions/) |

---

## 📝 Document Conventions

### Diagrams

- **C4 Model:** System Context → Container → Component
- **ASCII Diagrams:** For text-based documentation
- **Mermaid:** For complex flow diagrams (future)

### Code Examples

- **Language Tags:** `python`, `typescript`, `bash`, `sql`
- **Full Examples:** Runnable snippets with comments
- **Platform-Specific:** Clearly marked (Windows, macOS, Linux)

### File Paths

- **Absolute Paths:** When referencing specific files in repo
- **Relative Paths:** When showing user configurations
- **Placeholders:** Clearly marked with `{placeholder}` or `<placeholder>`

---

## 🔄 Document Updates

### Versioning

- Documents track version in frontmatter
- Major changes trigger version bump
- Changelog at bottom of each document

### Maintenance

| Document | Update Frequency | Owner |
|----------|------------------|-------|
| Product Requirements | Per phase (quarterly) | Product |
| Architecture Overview | Per phase (quarterly) | Architecture |
| ADRs | On decision (as needed) | Architecture |
| API Reference | Per release (monthly) | Backend |
| CLI Reference | Per release (monthly) | Backend |
| Database Schema | Per migration (rare) | Backend |
| Deployment Guide | Per release (monthly) | DevOps |

---

## 🤝 Contributing to Documentation

### Adding New Documentation

1. **Product Docs:** Add to `product/`
2. **Architecture Decisions:** Add new ADR to `architecture/decisions/` following template
3. **Technical Guides:** Add to `technical/`

### ADR Template

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

## Consequences
What becomes easier or more difficult to do because of this change?

## Alternatives Considered
What other options were evaluated?
```

### Updating Existing Documentation

1. Make changes
2. Update version/date in frontmatter
3. Add changelog entry at bottom
4. Submit PR with clear description

---

## 📧 Getting Help

**Questions about:**
- **Installation/Deployment:** See [Deployment Guide](technical/deployment-guide.md) Troubleshooting section
- **API Usage:** See [API Reference](technical/api-reference.md) Code Examples
- **Architecture Decisions:** Read relevant [ADR](architecture/decisions/)
- **Bug Reports:** GitHub Issues

---

## 🗂️ Archive

Historical documentation from Phase 1-2 is available in [archive/](archive/) for reference:
- `requirements.md.old` - Original Phase 1 requirements
- `specifications.md.old` - Detailed Phase 1-2 specifications
- `architecture.md.old` - Comprehensive Phase 1-2 architecture doc
- `peer-review.md` - Principal Architect review (Phase 2 guidance)

---

## 📚 Learning Resources

### Framework & Library Documentation

**Backend (Python)**
- [FastAPI Documentation](https://fastapi.tiangolo.com/) - Modern Python web framework
- [DuckDB Documentation](https://duckdb.org/docs/) - High-performance analytics database
- [Pydantic Documentation](https://docs.pydantic.dev/) - Data validation and settings
- [APScheduler Documentation](https://apscheduler.readthedocs.io/) - Task scheduling library
- [Click Documentation](https://click.palletsprojects.com/) - CLI framework

**Frontend (TypeScript/React)**
- [React Documentation](https://react.dev/) - UI framework
- [TypeScript Documentation](https://www.typescriptlang.org/docs/) - Type-safe JavaScript
- [Vite Documentation](https://vitejs.dev/) - Build tool and dev server
- [React Aria Documentation](https://react-spectrum.adobe.com/react-aria/) - Accessible component hooks (Adobe)
- [Victory Charts Documentation](https://commerce.nearform.com/open-source/victory/) - Accessible charting library
- [MDN CSS Custom Properties](https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties) - Design token system

**DevOps & Tools**
- [Docker Documentation](https://docs.docker.com/) - Containerization
- [Docker Compose Documentation](https://docs.docker.com/compose/) - Multi-container apps
- [Git Documentation](https://git-scm.com/doc) - Version control

---

## Document Changelog

- **2026-01-06:** Consolidated CI/CD documentation (60-70% duplication removed)
  - Merged ci-cd.md, cross-platform-ci.md into single github-actions-overview.md
  - Archived old workflow documentation to docs/archive/ci-cd/
  - Streamlined from 3 overlapping docs to 1 comprehensive guide
- **2026-01-03:** Added CI/CD automation documentation and GitHub Actions workflows
  - Created comprehensive CI/CD guide (docs/technical/github-actions-overview.md)
  - Added Backend CI, Frontend CI & Accessibility, and Documentation CI workflows
  - Included accessibility testing requirements (axe-core, Lighthouse, ESLint jsx-a11y)
- **2026-01-03:** Added ADR-006 (React Aria) and ADR-007 (Victory Charts) for Phase 3 Web UI
- **2026-01-03:** Updated Learning Resources with React Aria and Victory Charts documentation
- **2026-01-03:** Added design/ folder with Inclusive Design standards (WCAG 2.2 AA)
- **2026-01-03:** Added Learning Resources section with framework documentation links
- **2026-01-02:** Initial documentation index created during reorganization
- **2026-01-02:** Adopted ADR pattern for architecture decisions
