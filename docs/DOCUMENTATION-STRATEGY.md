# Documentation Strategy & Content Ownership

**Purpose:** Avoid duplication and clarify which document owns which content

---

## Document Purposes & Audiences

### [requirements.md](product/requirements.md) - Product Requirements Document (PRD)
**Audience:** Product owners, stakeholders, users, non-technical decision makers

**Owns:**
- ✅ **WHAT** we're building (features, user stories)
- ✅ **WHY** we're building it (business goals, problem statement)
- ✅ **WHEN** features are delivered (phase timeline, milestones)
- ✅ User personas and use cases
- ✅ Success metrics and acceptance criteria
- ✅ Non-functional requirements (performance targets, security goals)

**Does NOT contain:**
- ❌ Technology choices (e.g., "Victory Charts", "React Aria")
- ❌ Implementation details (e.g., "DuckDB columnar storage")
- ❌ System design diagrams
- ❌ Code examples

**Example Phase Description:**
```markdown
### Phase 2.5: Accessibility & UI Enhancement
**Goal:** Meet WCAG 2.2 Level AA accessibility standards

- Accessible data visualization components
- Keyboard navigation and screen reader support
```

---

### [architecture/overview.md](architecture/overview.md) - Architecture Overview
**Audience:** Developers, architects, technical contributors

**Owns:**
- ✅ **HOW** we're building it (technology stack, design patterns)
- ✅ Technology choices with rationale (Victory, React Aria, DuckDB)
- ✅ Migration history (tech stack evolution by phase)
- ✅ System context diagrams (C4 model)
- ✅ Component architecture and data flow
- ✅ Database schema and API design
- ✅ Deployment architecture

**Does NOT contain:**
- ❌ Business justification or user stories
- ❌ Detailed feature descriptions
- ❌ Success metrics or KPIs
- ❌ User personas

**Example Phase Description:**
```markdown
### Migration History

| Component | Phase 1 | Phase 2 | Phase 3 |
|-----------|---------|---------|---------|
| Charts    | Plotly  | Recharts| Victory |
```

---

### [architecture/decisions/*.md](architecture/decisions/) - Architecture Decision Records (ADRs)
**Audience:** Developers, future maintainers

**Owns:**
- ✅ **WHY** specific technology choices were made
- ✅ Detailed comparison of alternatives
- ✅ Trade-offs and consequences
- ✅ Code examples demonstrating the decision
- ✅ Benchmarks and validation results

**Does NOT contain:**
- ❌ Full system architecture (that's in overview.md)
- ❌ Business requirements (that's in requirements.md)

---

## Cross-Reference Strategy

Both PRD and Architecture Overview should link to each other for complementary information:

**In requirements.md:**
```markdown
> **Note:** For technology stack details by phase, see [Architecture Overview](../architecture/overview.md#migration-history)
```

**In architecture/overview.md:**
```markdown
> **Note:** For feature descriptions by phase, see [Product Requirements](../product/requirements.md#timeline--phases)
```

---

## Content Consolidation Rules

### ❌ AVOID: Duplicating Technology in Phase Descriptions

**Bad (Duplication):**
- requirements.md: "Phase 2.5: Victory Charts for visualization"
- architecture/overview.md: "Phase 2.5: Victory Charts for visualization"

**Good (Single Source of Truth):**
- requirements.md: "Phase 2.5: Accessible data visualization components"
- architecture/overview.md: "Phase 2.5: Victory Charts (WCAG 2.2 AA)"

### ✅ DO: Link Between Documents

When referencing implementation details in PRD:
```markdown
The dashboard uses accessible charting components (see [ADR-007: Victory Charts](../architecture/decisions/007-victory-charts.md) for technical details).
```

When referencing features in architecture docs:
```markdown
This technology supports Phase 3 multi-station requirements (see [Product Requirements](../product/requirements.md#phase-3)).
```

---

## Update Workflow

When technology changes (e.g., migrating from Recharts to Victory):

1. **Update ADR** - Document the decision with rationale
2. **Update architecture/overview.md** - Update tech stack tables
3. **Check requirements.md** - Ensure NO technology names are mentioned (only feature descriptions)
4. **Update code examples** - Update any example code in ADRs

When features change:

1. **Update requirements.md** - Update phase timeline and acceptance criteria
2. **Check architecture/overview.md** - Ensure no business justification or feature details
3. **Update ADRs if needed** - Only if technical decisions change

---

## Quick Reference

| Content Type | Owner Document | Cross-Reference From |
|-------------|----------------|---------------------|
| "What features by phase" | requirements.md | architecture/overview.md |
| "What tech stack by phase" | architecture/overview.md | requirements.md |
| "Why this technology" | ADRs | Both PRD and architecture |
| "User stories" | requirements.md | - |
| "System diagrams" | architecture/overview.md | - |
| "Business metrics" | requirements.md | - |
| "Performance benchmarks" | architecture/overview.md or ADRs | requirements.md |

---

## Document Changelog

- **2026-01-04:** Initial documentation strategy following consolidation of Victory/React Aria references
