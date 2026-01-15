# Documentation Standards - Index

Welcome to the Weather App documentation system. This directory contains all technical standards and guidelines for development.

---

## 📚 Documentation Structure

```
docs/
├── standards/
│   ├── README.md                    ← You are here
│   ├── ACCESSIBILITY.md             Load when building UI
│   ├── API-STANDARDS.md             Load when building APIs
│   ├── DATABASE-PATTERNS.md         Load when writing queries
│   ├── REACT-STANDARDS.md           Load when building components
│   └── TESTING.md                   Load when writing tests
├── examples/
│   ├── api-patterns.md              Real API examples
│   ├── component-patterns.md        Real component examples
│   └── query-patterns.md            Real query examples
├── architecture/
│   ├── overview.md                  System design
│   └── decisions/                   ADRs
└── guides/
    ├── adding-endpoints.md          Step-by-step guides
    ├── adding-components.md         Step-by-step UI guide
    └── PERFORMANCE.md               Performance optimization
```

---

## 🚀 Quick Start

**Always start with:** `CLAUDE.md` (project root)

The main CLAUDE.md file contains:
- Critical non-negotiable rules
- Decision tree for which docs to load
- Quick reference patterns
- Links to everything else

**Then load contextually based on your task** (see decision tree below).

---

## 📖 When to Load Each Document

### Decision Tree

```
What are you working on?

├─ Building API endpoints (FastAPI)
│  └─ READ: API-STANDARDS.md
│  └─ REFERENCE: examples/api-patterns.md
│
├─ Building UI components (React)
│  └─ READ: ACCESSIBILITY.md (REQUIRED for all UI)
│  └─ READ: REACT-STANDARDS.md
│  └─ REFERENCE: examples/component-patterns.md
│
├─ Writing database queries (DuckDB)
│  └─ READ: DATABASE-PATTERNS.md
│  └─ REFERENCE: examples/query-patterns.md
│
├─ Writing tests (pytest/Vitest)
│  └─ READ: TESTING.md
│
└─ Need architectural context
   └─ READ: architecture/overview.md
```

### Quick Reference Table

| Task | Required Reading | Examples |
|------|-----------------|----------|
| **New API endpoint** | API-STANDARDS.md | api-patterns.md |
| **New UI component** | ACCESSIBILITY.md + REACT-STANDARDS.md | component-patterns.md |
| **Database query** | DATABASE-PATTERNS.md | query-patterns.md |
| **Writing tests** | TESTING.md | Test examples in each standard doc |
| **Architecture decision** | architecture/overview.md | architecture/decisions/ |

---

## 📋 Standards Documents

### API-STANDARDS.md
**When:** Building FastAPI endpoints
**Contains:**
- Endpoint structure requirements
- Type safety & validation (Pydantic)
- Error handling patterns
- Response models
- Database integration
- Authentication patterns
- Testing requirements
- Performance optimization

**Key patterns:** Parameterized queries, error responses, pagination

---

### REACT-STANDARDS.md
**When:** Building React components
**Contains:**
- Component structure
- TypeScript patterns
- State management
- API integration hooks
- Styling with CSS tokens
- Accessibility integration
- Performance (memo, callback)
- Component testing

**Key patterns:** Props types, hooks, accessible components

---

### ACCESSIBILITY.md
**When:** Building ANY user interface
**MUST READ:** Before implementing any UI feature
**Contains:**
- WCAG 2.2 Level AA requirements
- Semantic HTML + manual ARIA patterns
- Keyboard navigation patterns
- Screen reader considerations
- Color contrast requirements
- Testing strategies

**Critical:** Every UI component must pass accessibility checklist

---

### DATABASE-PATTERNS.md
**When:** Writing DuckDB queries
**Contains:**
- Connection management
- Parameterized query patterns
- Schema design
- Performance optimization
- Batch operations
- Migration patterns
- Error handling

**Key patterns:** Async wrappers, aggregations, window functions

---

### TESTING.md
**When:** Writing tests
**Contains:**
- Testing philosophy & pyramid
- pytest patterns (backend)
- Vitest patterns (frontend)
- Integration testing
- Test fixtures
- Mocking strategies
- Coverage requirements

**Key patterns:** AAA pattern, fixtures, mocking

---

## 📁 Examples Directory

### api-patterns.md
Real examples from this project:
- Complete endpoint implementations
- Error handling in practice
- Authentication flows
- Common query patterns

### component-patterns.md
Real examples from this project:
- Chart components
- Form components
- Data display components
- Accessible interactive elements

### query-patterns.md
Real examples from this project:
- Date range queries
- Aggregations
- Performance-optimized queries
- Complex joins

---

## 🏗️ Architecture Documentation

### overview.md
High-level system design:
- Technology stack rationale
- Component diagrams
- Data flow
- Deployment architecture

### decisions/ (ADRs)
Architecture Decision Records:
- ADR-001: FastAPI Backend
- ADR-002: DuckDB Migration
- ADR-003: TypeScript Frontend
- ADR-004: Docker Deployment
- ADR-005: Retention Strategy
- ADR-006: React Aria Components *(Superseded - see actual implementation)*
- ADR-007: Victory Charts

---

## 📚 Guides Directory

### adding-endpoints.md
Step-by-step guide for adding new API endpoints

### adding-components.md
Step-by-step guide for adding new UI components

### PERFORMANCE.md
Performance optimization guide

**Note:** For deployment instructions, see [docs/technical/deployment-guide.md](../technical/deployment-guide.md)

---

## 🎯 Using This Documentation System

### For New Features

1. **Start:** Read `CLAUDE.md` in project root
2. **Identify task:** Use decision tree to find relevant standard
3. **Load standard:** Read the appropriate standards document
4. **Reference examples:** Check examples/ for real implementations
5. **Implement:** Follow patterns from standards
6. **Verify:** Run checklist from standard doc
7. **Test:** Follow TESTING.md guidelines

### For Bug Fixes

1. **Understand issue:** Reproduce the bug
2. **Identify component:** Find which standard applies
3. **Load standard:** Read relevant patterns
4. **Fix:** Apply correct pattern
5. **Test:** Write test to prevent regression

### For Code Review

1. **Check compliance:** Does code follow standards?
2. **Verify patterns:** Are established patterns used?
3. **Check accessibility:** UI changes pass accessibility checklist?
4. **Review tests:** Adequate test coverage?
5. **Check documentation:** Is documentation updated?

---

## ✅ Checklists

### Before Starting Any Task

- [ ] Read CLAUDE.md
- [ ] Identify which standards apply
- [ ] Load relevant standard documents
- [ ] Review examples if available
- [ ] Understand acceptance criteria

### Before Submitting PR

- [ ] Code follows relevant standards
- [ ] All checklists in standards docs completed
- [ ] Tests written and passing
- [ ] Accessibility verified (for UI)
- [ ] Documentation updated if needed
- [ ] No console errors or warnings

---

## 🔄 Keeping Documentation Updated

### When to Update Standards

- New patterns emerge from development
- Best practices evolve
- Framework updates require changes
- Team identifies common mistakes

### How to Update

1. **Discuss change** with team
2. **Update relevant standard** document
3. **Update examples** if needed
4. **Update CLAUDE.md** if it affects decision tree
5. **Announce change** to team

---

## 📞 Questions?

- **Unclear requirements?** Check CLAUDE.md first
- **Pattern not documented?** Look in examples/
- **Need architectural context?** Read architecture/overview.md
- **Still unsure?** Ask before implementing

---

## 🎓 Learning Path

### For New Developers

**Week 1:**
- Read CLAUDE.md thoroughly
- Skim all standards documents
- Review examples/

**Week 2:**
- Deep dive into your primary area (API, UI, or Database)
- Read relevant ADRs
- Review test examples

**Week 3:**
- Start contributing
- Reference standards as needed
- Ask questions freely

### For Experienced Developers

- Use CLAUDE.md as quick reference
- Load standards contextually as needed
- Contribute to documentation improvements

---

## 📊 Documentation Metrics

**Optimal usage:**
- CLAUDE.md: Load every session (100%)
- Standards: Load contextually (40-60%)
- Examples: Reference as needed (20-30%)
- Architecture: Occasional reference (5-10%)

**Signs of good structure:**
- Fast time to find information
- Low violation rate in PRs
- New developers productive quickly
- Documentation stays updated

---

**Last Updated:** January 2026
**Maintained by:** Development Team
**Feedback:** Open PR to suggest improvements
