# GitHub Actions Workflows

## Active Workflows

### Backend CI (`backend-ci.yml`)
- **Status**: ✅ Active
- **Triggers**: Push/PR to `main`/`develop` affecting Python code
- **Jobs**: Lint, Test (multi-platform), Security, API Tests

### Documentation CI (`docs-ci.yml`)
- **Status**: ✅ Active
- **Triggers**: Push/PR to `main`/`develop` affecting documentation
- **Jobs**: Markdown lint, link check, ADR validation, spell check, structure validation

## Disabled Workflows (Phase 3)

### Frontend CI & Accessibility (`frontend-ci.yml.disabled`)
- **Status**: ⏸️ Disabled (Phase 2 - backend only)
- **Reason**: Frontend doesn't exist yet (will be built in Phase 3)
- **To Enable**: Rename `frontend-ci.yml.disabled` → `frontend-ci.yml` when frontend development begins
- **Jobs**: Lint, Test, Accessibility (axe-core, Lighthouse), Build

**Note**: This workflow will be re-enabled in Phase 3 when we start building the React frontend with React Aria + Victory Charts.

## Documentation

See [docs/technical/ci-cd.md](../../docs/technical/ci-cd.md) for complete CI/CD documentation.
