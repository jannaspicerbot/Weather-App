# Best Practices for Managing Project Requirements with Claude Code

## Executive Summary

**The Problem:** Large, comprehensive instruction files lead to:
- Context window waste (Claude loads everything, uses 10%)
- Instruction fatigue (Claude may overlook buried rules)
- Maintenance burden (updating scattered requirements)
- Slower performance (processing irrelevant context)

**The Solution:** **Hierarchical documentation with targeted loading**

```
CLAUDE.md (200-500 lines)
├── Core principles & workflows
├── Critical non-negotiables
└── Links to specialized docs

Specialized docs (loaded on-demand)
├── ACCESSIBILITY.md (when working on UI)
├── API-STANDARDS.md (when working on endpoints)
├── DATABASE-PATTERNS.md (when working on queries)
└── etc.
```

---

## Recommended Documentation Architecture

### Hub-and-Spoke Model

**Hub: CLAUDE.md** (The Single Source of Truth)
- ~300-500 lines maximum
- High-level principles
- Critical non-negotiable rules
- Decision framework for when to consult specialized docs
- Links to everything else

**Spokes: Specialized Documentation** (Loaded contextually)
- Deep-dive guides for specific domains
- Loaded only when relevant to current task
- Can be comprehensive without wasting context

---

## What Belongs in CLAUDE.md

### ✅ Include in Main File

**1. Critical Workflow Rules** (Frequently violated if not visible)
```markdown
## Non-Negotiable Rules

1. ALWAYS create feature branches (never commit to main)
2. ALWAYS run pre-commit checks before pushing
3. ALWAYS include type hints (Python) / types (TypeScript)
4. ALWAYS test keyboard navigation for UI components
```

**2. Decision Framework** (Help Claude know when to dive deeper)
```markdown
## When to Consult Specialized Docs

Working on...
- UI components → Read ACCESSIBILITY.md first
- API endpoints → Read API-STANDARDS.md first
- Database queries → Read DATABASE-PATTERNS.md first
- Complex business logic → Read ARCHITECTURE.md first
```

**3. Quick Reference** (Most common patterns)
```markdown
## Quick Patterns

### Error Handling
try:
    result = operation()
    if not result:
        raise HTTPException(status_code=404, detail="Not found")
except Exception as e:
    logger.error(f"Error: {e}")
    raise HTTPException(status_code=500, detail="Internal error")

### Component Props
interface ComponentProps {
  data: DataType[];
  onUpdate: (data: DataType) => void;
  isLoading?: boolean;
}
```

**4. Tool Usage** (Where to find what)
```markdown
## Essential Commands

Git workflow: See "Git Rules" section above
Testing: `pytest tests/` (Python), `npm test` (TypeScript)
Formatting: `black .` (Python), `npm run lint:fix` (TypeScript)
Docs location: docs/README.md for full navigation
```

### ❌ Move to Specialized Docs

**1. Comprehensive Standards** (Too detailed for every session)
- Full WCAG 2.2 guidelines → `docs/standards/ACCESSIBILITY.md`
- Complete API specification → `docs/standards/API-STANDARDS.md`
- All database patterns → `docs/standards/DATABASE-PATTERNS.md`

**2. Examples & Recipes** (Reference when needed)
- 10+ code examples → `docs/examples/`
- Component cookbook → `docs/components/`
- Architecture patterns → `docs/architecture/patterns/`

**3. Historical Context** (Rarely needed during implementation)
- ADRs (Architecture Decision Records) → `docs/architecture/decisions/`
- Migration guides → `docs/guides/migrations/`
- Changelog → `CHANGELOG.md`

---

## Optimal File Sizes for Claude Code

### Context Window Economics

Claude Sonnet 4 has ~200k token context window, but:
- **Effective working memory:** ~50-100k tokens (rest is "available but not active")
- **Instruction processing:** First ~10k tokens get most attention
- **Pattern recognition:** Works best with focused, relevant context

### Recommended Sizes

| Document Type | Optimal Size | Max Size | Rationale |
|---------------|--------------|----------|-----------|
| **CLAUDE.md** | 300-500 lines | 800 lines | Core reference, always loaded |
| **Specialized standards** | 500-1000 lines | 2000 lines | Domain-specific, loaded when needed |
| **Code files for review** | 100-300 lines | 1000 lines | Anything larger needs chunking |
| **Examples/recipes** | 50-200 lines | 500 lines | Quick reference patterns |

### Anti-Pattern: The Monolithic Guide

```markdown
❌ BAD: CLAUDE.md (5,000 lines)
- Everything about everything
- Claude loads it all, uses 5%
- Rules buried in noise
- Slow to scan and reference
```

```markdown
✅ GOOD: CLAUDE.md (400 lines) + Specialized docs
- Core principles and decision tree
- "For X, see Y" instructions
- Claude loads only what's needed
- Fast, focused, effective
```

---

## Preventing Claude from Forgetting Rules

### Problem: "Out of Sight, Out of Mind"

Claude can forget rules when:
1. **Too much context** - Rule buried in 10k lines of instructions
2. **Contradictory patterns** - Code doesn't follow stated rules
3. **Infrequent use** - Rule only applies to rare situations
4. **Multi-turn conversations** - Earlier instructions fade

### Solution 1: Enforcement Layers

```
Layer 1: CLAUDE.md (always present)
├── Critical rules repeated at top
└── "Before you start" checklist

Layer 2: Pre-commit hooks (automated)
├── black, ruff, mypy (Python)
├── eslint, prettier (TypeScript)
└── pre-commit.yaml with all checks

Layer 3: CI/CD (gatekeeper)
├── GitHub Actions runs all checks
├── Blocks merge if violations
└── Clear error messages

Layer 4: Pull request template
├── Checklist for reviewer
└── Forces human verification
```

### Solution 2: Just-In-Time Reminders

**Pattern: Contextual Loading**

```bash
# User request
"Add a new API endpoint for exporting weather data as CSV"

# Claude's first action (in its planning)
1. Load CLAUDE.md (always)
2. Identify domain: API endpoints
3. Load API-STANDARDS.md (contextual)
4. Load docs/examples/api-export-patterns.md (specific pattern)
5. Implement following all three sources
```

**Implementation:**

```markdown
# CLAUDE.md

## Working on API Endpoints?

**STOP** - Before implementing, read these docs:
1. docs/standards/API-STANDARDS.md - Required patterns
2. docs/examples/api-patterns.md - Common patterns
3. Checklist:
   - [ ] Type hints for all parameters
   - [ ] Response models defined (Pydantic)
   - [ ] Error handling (404, 500)
   - [ ] OpenAPI documentation
   - [ ] Integration test written
```

### Solution 3: Critical Rules Repetition

**Pattern: Strategic Redundancy**

Place non-negotiable rules in **multiple** locations:

```
1. CLAUDE.md (top of file)
2. Specialized doc (relevant section)
3. Code comments (where violations likely)
4. PR template (human reviewer check)
```

**Example:**

```markdown
# CLAUDE.md (Line 10)
## ⚠️ CRITICAL: Git Workflow
NEVER commit directly to main. ALWAYS create feature branch first.

# API-STANDARDS.md (Line 5)
## ⚠️ Before You Start
Remember: Create feature branch first (see CLAUDE.md git workflow)

# weather_app/api/routes.py (Line 1)
# IMPORTANT: This file is in main branch protection. Always work in feature branches.

# .github/pull_request_template.md
- [ ] Created from feature branch (not main)
```

### Solution 4: Active Voice Instructions

```markdown
❌ PASSIVE (Easy to overlook)
"Type hints should be used for function parameters"
"Accessibility is important and should be considered"

✅ ACTIVE (Hard to ignore)
"ADD type hints to every function parameter"
"RUN axe-core tests before submitting PR"
"ALWAYS test keyboard navigation for UI components"
```

### Solution 5: Failure Mode Documentation

**Pattern: Explicit "If You Forget" Sections**

```markdown
## Common Mistakes & How to Fix

### Forgot to Create Feature Branch
**Symptom:** Already made commits on main
**Fix:**
```bash
git branch feature/my-feature  # Create branch with current work
git reset --hard origin/main   # Reset main to clean state
git checkout feature/my-feature # Switch to feature branch
```

### Forgot Type Hints
**Symptom:** mypy errors in CI
**Fix:** Run `mypy weather_app/` locally and add missing types

### Forgot Accessibility Tests
**Symptom:** PR blocked by CI (axe-core failures)
**Fix:** See docs/standards/ACCESSIBILITY.md for patterns
```

---

## Recommended File Structure

```
project/
├── CLAUDE.md                          # 300-500 lines: Core guide
│
├── docs/
│   ├── README.md                      # Navigation hub
│   │
│   ├── standards/                     # Detailed standards (load contextually)
│   │   ├── ACCESSIBILITY.md           # ~1000 lines: WCAG 2.2 implementation
│   │   ├── API-STANDARDS.md           # ~800 lines: FastAPI patterns
│   │   ├── DATABASE-PATTERNS.md       # ~600 lines: DuckDB best practices
│   │   ├── TESTING.md                 # ~700 lines: Testing strategies
│   │   └── SECURITY.md                # ~500 lines: Security requirements
│   │
│   ├── examples/                      # Code recipes (reference as needed)
│   │   ├── api-patterns.md            # Common API implementations
│   │   ├── component-patterns.md      # React component recipes
│   │   └── database-queries.md        # SQL query examples
│   │
│   ├── architecture/                  # Historical/planning docs
│   │   ├── overview.md                # High-level system design
│   │   └── decisions/                 # ADRs (load rarely)
│   │       ├── 001-fastapi.md
│   │       └── 002-duckdb.md
│   │
│   └── guides/                        # Task-specific tutorials
│       ├── adding-endpoints.md        # Step-by-step guides
│       └── deployment.md
│
├── .github/
│   ├── pull_request_template.md       # Checklist reminder
│   └── workflows/
│       └── ci.yml                     # Automated enforcement
│
└── .pre-commit-config.yaml            # Local enforcement
```

---

## Practical Example: Refactoring Your Project

### Current State Analysis

Your current `CLAUDE.md` (1,209 lines) contains:

**Should stay in CLAUDE.md:**
- Git workflow (lines 75-170) ✅
- Model selection (lines 10-62) ✅
- Core principles (lines 65-73) ✅
- Quick reminders (lines 1189-1202) ✅

**Should move to specialized docs:**
- Python best practices (lines 193-268) → `docs/standards/PYTHON-STANDARDS.md`
- React best practices (lines 271-397) → `docs/standards/REACT-STANDARDS.md`
- Testing comprehensive guide (lines 897-1050) → `docs/standards/TESTING.md`
- Performance tips (lines 1097-1139) → `docs/guides/PERFORMANCE.md`
- Security section (lines 1052-1080) → `docs/standards/SECURITY.md`

### Recommended Refactor

**New CLAUDE.md Structure** (~400 lines):

```markdown
# Claude Code Guidelines

## Quick Start Checklist
- [ ] On feature branch? (check with `git branch --show-current`)
- [ ] Loaded relevant standards doc? (see "When to Load" below)
- [ ] Understand the requirement? (ask questions if not)

## Critical Non-Negotiables
1. Git workflow (never commit to main)
2. Type safety (Python type hints, TypeScript types)
3. Testing (write tests for new features)
4. Accessibility (keyboard nav + screen reader)

## When to Load Specialized Docs

**Before starting work, read the relevant guide:**

| Working on... | Load this doc | Contains |
|---------------|---------------|----------|
| API endpoints | docs/standards/API-STANDARDS.md | FastAPI patterns, error handling, OpenAPI |
| UI components | docs/standards/REACT-STANDARDS.md + ACCESSIBILITY.md | Component patterns, WCAG 2.2 |
| Database queries | docs/standards/DATABASE-PATTERNS.md | DuckDB best practices, query optimization |
| Test writing | docs/standards/TESTING.md | pytest patterns, test strategy |
| Performance issues | docs/guides/PERFORMANCE.md | Profiling, optimization techniques |

## Quick Reference Patterns

[Most common patterns - 10-15 examples, ~100 lines]

## Model Selection Guide

[Simplified table - ~50 lines]

## Git Workflow

[Critical workflow - ~100 lines]

## Common Mistakes & Fixes

[Failure modes - ~50 lines]

## Links to Everything Else

- Architecture overview: docs/architecture/overview.md
- All standards: docs/standards/README.md
- Code examples: docs/examples/README.md
- Contributing: docs/CONTRIBUTING.md
```

**New docs/standards/API-STANDARDS.md** (~800 lines):

```markdown
# API Standards & Patterns

## Overview
FastAPI best practices for this project.
See CLAUDE.md for when to consult this doc.

## Required Patterns

### Every Endpoint Must Have
1. Type hints (request/response)
2. Response model (Pydantic)
3. Error handling (404, 500 at minimum)
4. OpenAPI documentation (docstring)
5. Integration test

### Standard Error Handling
[Detailed pattern - 100 lines]

### Authentication & Authorization
[Patterns - 100 lines]

### Request Validation
[Patterns - 100 lines]

### Response Formatting
[Patterns - 100 lines]

### Database Integration
[Patterns - 100 lines]

### Testing Patterns
[Patterns - 100 lines]

### Real Examples from This Project
[5-10 examples from actual codebase - 300 lines]
```

---

## Effective Instruction Patterns

### Pattern 1: Command-Based Instructions

```markdown
❌ WEAK
"It's generally recommended to use type hints"

✅ STRONG
"ADD type hints to all function parameters and returns"
```

### Pattern 2: Conditional Loading Instructions

```markdown
## Before Implementing UI Components

REQUIRED READING:
1. docs/standards/ACCESSIBILITY.md (WCAG 2.2 checklist)
2. docs/standards/REACT-STANDARDS.md (Component patterns)

REQUIRED CHECKS:
- [ ] Keyboard navigation works
- [ ] Screen reader announces correctly
- [ ] Color contrast ≥ 4.5:1
- [ ] Touch targets ≥ 44×44px
```

### Pattern 3: Layered Authority

```markdown
# CLAUDE.md (Layer 1: Always enforce)
NEVER commit to main branch.

# API-STANDARDS.md (Layer 2: Domain enforce)
When implementing endpoints, remember git workflow (see CLAUDE.md).

# Code comments (Layer 3: Context enforce)
# This route is protected. Remember to work in feature branch.
```

### Pattern 4: Decision Trees

```markdown
## Need to Add a New Feature?

START HERE:
1. Is it UI-related?
   YES → Read ACCESSIBILITY.md + REACT-STANDARDS.md
   NO → Continue

2. Is it an API endpoint?
   YES → Read API-STANDARDS.md
   NO → Continue

3. Is it database-related?
   YES → Read DATABASE-PATTERNS.md
   NO → Continue

4. Is it complex business logic?
   YES → Read ARCHITECTURE.md, discuss approach first
   NO → Proceed with implementation
```

---

## Testing Your Documentation Structure

### Effectiveness Metrics

**Good documentation structure shows:**

1. **Fast time-to-context** - Claude loads only what's needed
   - Measure: Token count in first request
   - Target: <20k tokens for typical task

2. **Low violation rate** - Rules followed consistently
   - Measure: CI failures, PR feedback
   - Target: <10% of PRs have basic violations

3. **Efficient multi-turn conversations** - Rules persist across messages
   - Measure: How often Claude needs reminders
   - Target: Reminder needed <1x per 10-turn conversation

4. **Easy maintenance** - Updates in one place propagate correctly
   - Measure: Time to update standards
   - Target: <30 min to update major pattern

### A/B Test Framework

Try different structures and measure:

```markdown
Experiment 1: Monolithic CLAUDE.md (1,500 lines)
- Track: How often Claude violates git workflow
- Track: Average context size per request
- Track: Time to find specific pattern

Experiment 2: Hub-and-spoke (400 line hub + specialized docs)
- Track: Same metrics
- Compare: Which performs better?
```

---

## Common Pitfalls to Avoid

### Pitfall 1: "Documentation Sprawl"

```markdown
❌ BAD: 50 different docs with no navigation
docs/
├── accessibility-colors.md
├── accessibility-keyboard.md
├── accessibility-screen-readers.md
├── accessibility-aria.md
└── ... 46 more files

✅ GOOD: Consolidated with clear sections
docs/standards/
└── ACCESSIBILITY.md (with clear table of contents)
```

### Pitfall 2: "Stale Cross-References"

```markdown
❌ BAD: Hard-coded line numbers
"See lines 145-160 in api.py for pattern"

✅ GOOD: Semantic references
"See error_handler() function in weather_app/api/error_handlers.py"
```

### Pitfall 3: "The Everything Document"

```markdown
❌ BAD: CLAUDE.md tries to be comprehensive
- 2,000 lines covering everything
- Claude loads it all every time
- Rules buried in noise

✅ GOOD: CLAUDE.md is a smart router
- 400 lines of core + navigation
- Points to specialized docs
- Claude loads contextually
```

### Pitfall 4: "Hidden Requirements"

```markdown
❌ BAD: Requirements in random code comments
# Remember to always use UTC timestamps
# Also don't forget to validate email format
# BTW make sure to log errors

✅ GOOD: Requirements in discoverable docs
docs/standards/API-STANDARDS.md explicitly lists all requirements
Code comments reference the doc: "See API-STANDARDS.md section 3.2"
```

---

## Recommended Implementation Plan

### Phase 1: Audit Current State (1-2 hours)

1. **Inventory CLAUDE.md**: What's actually in there?
2. **Categorize content**: Core vs. specialized vs. examples
3. **Identify violations**: What rules get broken most often?
4. **Find duplication**: Same info in multiple places?

### Phase 2: Create Specialized Docs (3-5 hours)

1. **Extract domain-specific content** from CLAUDE.md
2. **Create standards docs**:
   - API-STANDARDS.md
   - REACT-STANDARDS.md
   - ACCESSIBILITY.md (you already have inclusive-design.md)
   - DATABASE-PATTERNS.md
   - TESTING.md

3. **Add navigation**: docs/standards/README.md as index

### Phase 3: Refactor CLAUDE.md (2-3 hours)

1. **Reduce to core** (~400 lines)
2. **Add decision tree**: "When to load X doc"
3. **Keep non-negotiables**: Critical rules stay
4. **Link to everything**: Clear pointers to specialized docs

### Phase 4: Enforce with Automation (2-3 hours)

1. **Pre-commit hooks**: Catch violations locally
2. **CI/CD checks**: Enforce in GitHub Actions
3. **PR template**: Human checklist

### Phase 5: Test and Iterate (Ongoing)

1. **Use with Claude Code**: Track what works
2. **Monitor violations**: What's still being broken?
3. **Adjust weights**: Move content up/down hierarchy
4. **Measure context usage**: Are we loading only what's needed?

---

## Example: Your Weather App

### Recommended Structure

```
Weather-App/
├── CLAUDE.md                                    # 400 lines
│   ├── Quick start checklist
│   ├── Critical non-negotiables (git, types, testing, a11y)
│   ├── When to load specialized docs (decision tree)
│   ├── Quick patterns (10-15 most common)
│   ├── Model selection (simplified table)
│   └── Links to everything
│
├── docs/
│   ├── README.md                                # Navigation hub
│   │
│   ├── standards/                               # Load contextually
│   │   ├── README.md                           # Index of standards
│   │   ├── API-STANDARDS.md                    # ~800 lines
│   │   ├── REACT-STANDARDS.md                  # ~600 lines
│   │   ├── ACCESSIBILITY.md                    # ~1000 lines (your existing inclusive-design.md)
│   │   ├── DATABASE-PATTERNS.md                # ~500 lines
│   │   ├── TESTING.md                          # ~700 lines
│   │   └── SECURITY.md                         # ~400 lines
│   │
│   ├── examples/                               # Reference as needed
│   │   ├── api-patterns.md                     # FastAPI examples
│   │   ├── component-patterns.md               # React examples
│   │   └── query-patterns.md                   # DuckDB examples
│   │
│   ├── architecture/                           # Your existing structure
│   │   ├── overview.md                         # High-level (load rarely)
│   │   └── decisions/                          # ADRs (load very rarely)
│   │
│   └── guides/                                 # Task tutorials
│       ├── adding-api-endpoints.md
│       ├── adding-ui-components.md
│       └── deployment.md
│
└── .github/
    ├── pull_request_template.md               # Reminder checklist
    └── workflows/ci.yml                       # Enforcement
```

### Specific Moves for Your Files

**From current CLAUDE.md → New structure:**

```
Lines 193-268 (Python patterns) → docs/standards/PYTHON-STANDARDS.md
Lines 271-397 (React patterns) → docs/standards/REACT-STANDARDS.md
Lines 400-670 (Database) → docs/standards/DATABASE-PATTERNS.md
Lines 897-1050 (Testing) → docs/standards/TESTING.md
Lines 1052-1080 (Security) → docs/standards/SECURITY.md
Lines 1097-1139 (Performance) → docs/guides/PERFORMANCE.md

Keep in CLAUDE.md:
Lines 10-62 (Model selection - simplify)
Lines 75-170 (Git workflow)
Lines 1189-1202 (Key reminders)
Add: Decision tree for when to load specialized docs
```

**Your inclusive-design.md:**
- Already well-structured at ~800 lines
- Rename to `docs/standards/ACCESSIBILITY.md`
- Reference from CLAUDE.md: "Working on UI? Load docs/standards/ACCESSIBILITY.md first"

**Your overview.md:**
- Good as-is in `docs/architecture/overview.md`
- Claude should load this rarely (only for architectural questions)
- Not needed for day-to-day feature implementation

---

## Key Takeaway

**Optimal structure for Claude Code:**

```
Small always-loaded hub (CLAUDE.md)
      ↓
  Decision framework ("If X, load Y")
      ↓
Specialized docs loaded contextually
      ↓
  Multiple enforcement layers
```

**Results:**
- ✅ Faster context loading (only what's needed)
- ✅ Better rule adherence (focused instructions)
- ✅ Easier maintenance (change in one place)
- ✅ Scales with project (add new docs without bloating hub)

**The golden rule:**
> If Claude doesn't need it for THIS task, don't load it.
> Make the decision tree explicit so Claude knows what to load WHEN.

---

**Next Steps for Your Project:**

1. **Quick win**: Move inclusive-design.md → docs/standards/ACCESSIBILITY.md
2. **High impact**: Create decision tree in CLAUDE.md "When to Load" section
3. **Long-term**: Extract specialized docs from current CLAUDE.md
4. **Measure**: Track violations before/after to verify improvement
