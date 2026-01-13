<!--
Pull Request Template for Weather App
This template ensures all PRs meet project standards.
Delete sections that don't apply to your PR.
-->

## Description

<!-- Provide a clear and concise description of what this PR does -->

### What does this PR do?
<!-- Example: Adds CSV export functionality to weather API -->


### Why is this change needed?
<!-- Example: Users requested ability to export data for external analysis -->


### Related Issues
<!-- Link to related issues. Example: Closes #123, Relates to #456 -->


---

## Type of Change

<!-- Check all that apply -->

- [ ] 🐛 Bug fix (non-breaking change that fixes an issue)
- [ ] ✨ New feature (non-breaking change that adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📝 Documentation update
- [ ] ♻️ Refactoring (no functional changes)
- [ ] 🎨 Style/formatting changes
- [ ] ⚡ Performance improvement
- [ ] ✅ Test updates
- [ ] 🔧 Configuration changes
- [ ] 🏗️ Infrastructure/build changes

---

## Checklist

### Required for ALL Pull Requests

- [ ] **Created from feature branch** (not `main`)
- [ ] **Branch name follows convention** (`feature/`, `bugfix/`, `refactor/`, etc.)
- [ ] **Commit messages are descriptive** (not "updates" or "fixes")
- [ ] **Code follows project style guidelines**
  - [ ] Python: `black`, `ruff`, `mypy` all pass
  - [ ] TypeScript: `eslint`, `prettier` all pass
- [ ] **No console errors or warnings**
- [ ] **Self-reviewed code** before requesting review

### Testing Requirements

- [ ] **All existing tests pass**
  - [ ] Backend: `pytest tests/ -v`
  - [ ] Frontend: `npm test`
- [ ] **New tests added** for new functionality
- [ ] **Tests cover edge cases** (empty data, errors, invalid input)
- [ ] **Manual testing completed**
  - [ ] Tested locally in dev environment
  - [ ] Verified in multiple browsers (if UI change)

### Documentation Requirements

- [ ] **Code is documented**
  - [ ] Python: Docstrings for new functions
  - [ ] TypeScript: JSDoc comments for complex logic
- [ ] **README updated** (if installation/setup changed)
- [ ] **API documentation updated** (if endpoints changed)
- [ ] **CHANGELOG.md updated** (if user-facing change)

### Type Safety Requirements

- [ ] **Type hints added** (Python functions)
- [ ] **Types defined** (TypeScript interfaces/types)
- [ ] **No `any` types** in TypeScript (unless absolutely necessary)
- [ ] **Pydantic models** for API request/response validation

---

## For API Changes (FastAPI)

<!-- Skip this section if not modifying API -->

- [ ] **Follows API-STANDARDS.md** patterns
- [ ] **Type hints** for all parameters and returns
- [ ] **Response model** defined (Pydantic)
- [ ] **Error handling** implemented (404, 500 at minimum)
- [ ] **Input validation** (Query parameters, request body)
- [ ] **Integration test** written and passing
- [ ] **OpenAPI docs** generated correctly (`/docs` endpoint)
- [ ] **Tested in Swagger UI** manually

### API Checklist Details

**Endpoint:** `[METHOD] /api/endpoint/path`

**Request validation:**
- [ ] Query parameters validated
- [ ] Request body validated (if POST/PUT)
- [ ] Path parameters validated

**Response codes implemented:**
- [ ] 200/201 - Success
- [ ] 400 - Bad request (invalid input)
- [ ] 404 - Not found (no data)
- [ ] 500 - Server error (unexpected)

**Security:**
- [ ] No sensitive data in error messages
- [ ] Parameterized SQL queries (no SQL injection)
- [ ] Authentication/authorization (if required)

---

## For UI Changes (React)

<!-- Skip this section if not modifying UI -->

- [ ] **Follows REACT-STANDARDS.md** patterns
- [ ] **Follows ACCESSIBILITY.md** requirements (REQUIRED)
- [ ] **TypeScript types** for all props and state
- [ ] **Loading and error states** implemented
- [ ] **Responsive design** (mobile, tablet, desktop)
- [ ] **Component tests** written
- [ ] **Accessibility tests** passing (`npm run test:a11y`)

### Accessibility Checklist (REQUIRED for UI)

- [ ] **Keyboard navigation works**
  - [ ] Tab through all interactive elements
  - [ ] Enter/Space activates buttons
  - [ ] Escape closes modals/dropdowns
- [ ] **Screen reader tested**
  - [ ] Tested with VoiceOver (Mac) or NVDA (Windows)
  - [ ] All content announced correctly
  - [ ] State changes announced
- [ ] **Color contrast ≥ 4.5:1** for text
- [ ] **Touch targets ≥ 44×44px** on mobile
- [ ] **Focus indicators visible** (not removed)
- [ ] **No keyboard traps** (can navigate away from all elements)
- [ ] **ARIA attributes** used correctly (only when semantic HTML insufficient)
- [ ] **Images have alt text** (or `alt=""` if decorative)

### Visual Testing

- [ ] **Tested in multiple browsers**
  - [ ] Chrome
  - [ ] Firefox
  - [ ] Safari
- [ ] **Tested at multiple viewport sizes**
  - [ ] Mobile (320px - 767px)
  - [ ] Tablet (768px - 1023px)
  - [ ] Desktop (1024px+)
- [ ] **Tested with browser zoom** (200% zoom works)
- [ ] **No horizontal scrolling** at standard viewport sizes

---

## For Database Changes (DuckDB)

<!-- Skip this section if not modifying database -->

- [ ] **Follows DATABASE-PATTERNS.md**
- [ ] **Parameterized queries** (NEVER string formatting)
- [ ] **Type validation** with Pydantic models
- [ ] **Connection management** uses context managers
- [ ] **Error handling** for database operations
- [ ] **Migration script** created (if schema change)
- [ ] **Indexes added** for new query patterns
- [ ] **Query performance** tested with EXPLAIN ANALYZE

### Schema Changes

**If modifying schema:**
- [ ] Migration script in `migrations/` directory
- [ ] Migration tested on clean database
- [ ] Rollback procedure documented
- [ ] Backward compatibility considered

**Tables affected:**
<!-- List tables modified, added, or deleted -->

---

## Performance Considerations

<!-- Answer these questions if your change could affect performance -->

**Does this change affect performance?**
- [ ] No performance impact
- [ ] Yes, performance tested (details below)

**If yes, provide details:**
- **What was tested:**
- **Benchmark results:**
- **Optimization applied:**

---

## Security Considerations

<!-- Check if any apply -->

- [ ] This PR does NOT handle sensitive data
- [ ] This PR handles sensitive data and:
  - [ ] No sensitive data logged
  - [ ] No sensitive data in error messages
  - [ ] Input properly validated
  - [ ] SQL injection prevented (parameterized queries)
  - [ ] XSS prevented (proper escaping)

---

## Breaking Changes

<!-- If this is a breaking change, describe the impact -->

**Does this PR include breaking changes?**
- [ ] No
- [ ] Yes (describe below)

**If yes, describe:**
- **What breaks:**
- **Migration path:**
- **Users affected:**

---

## Screenshots / Videos

<!-- For UI changes, include before/after screenshots or videos -->

**Before:**
<!-- Screenshot of current state -->

**After:**
<!-- Screenshot of new state -->

**Mobile view:**
<!-- Screenshot on mobile if relevant -->

---

## Testing Instructions

<!-- Provide step-by-step instructions for reviewers to test this PR -->

### Prerequisites
<!-- Example: Ensure database is seeded with test data -->


### Steps to Test
1.
2.
3.

### Expected Behavior
<!-- What should happen when testing -->


### Edge Cases to Test
<!-- Specific scenarios reviewers should try -->
- [ ] Empty data
- [ ] Invalid input
- [ ] Network error
- [ ] Large dataset

---

## Deployment Notes

<!-- Information needed for deployment -->

**Environment variables:**
<!-- List any new or modified environment variables -->
- [ ] No new environment variables
- [ ] New variables (document in `.env.example`):

**Database migrations:**
- [ ] No migration needed
- [ ] Migration included (run before deployment)

**Configuration changes:**
- [ ] No config changes
- [ ] Config updated (document in DEPLOYMENT.md)

**Dependencies:**
- [ ] No new dependencies
- [ ] New dependencies added:
  - Backend:
  - Frontend:

---

## Reviewer Notes

<!-- Additional context for reviewers -->

### Areas of Focus
<!-- Where should reviewers pay special attention? -->


### Known Limitations
<!-- Any known issues or limitations in this PR? -->


### Future Work
<!-- Related work that will be done in future PRs -->


---

## Post-Merge Checklist

<!-- Complete after PR is merged -->

- [ ] Delete feature branch
- [ ] Verify deployment successful (if applicable)
- [ ] Update related documentation
- [ ] Close related issues
- [ ] Notify stakeholders (if needed)

---

## Additional Comments

<!-- Any other information relevant to this PR -->


---

<!--
For questions about PR requirements:
- Standards: See docs/standards/README.md
- Git workflow: See CLAUDE.md section on Git
- Accessibility: See docs/standards/ACCESSIBILITY.md
- Testing: See docs/standards/TESTING.md
-->
