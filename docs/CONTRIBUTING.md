# Contributing to Weather App

This guide explains how to contribute code and documentation to the Weather App project.

---

## 🚀 Quick Start for Contributors

1. **Fork and clone** the repository
2. **Install the pre-commit hook** (see [Security](#-security) below)
3. **Create a feature branch** from `main`
4. **Read the relevant standards** before coding (see [Documentation](#-documentation) below)
5. **Submit a pull request** with your changes

---

## 📖 Documentation

### Finding What You Need

| I want to... | Read this |
|--------------|-----------|
| Understand the system architecture | [architecture/overview.md](architecture/overview.md) |
| Learn the documentation philosophy | [DOCUMENTATION-STRATEGY.md](DOCUMENTATION-STRATEGY.md) |
| Follow API coding standards | [standards/API-STANDARDS.md](standards/API-STANDARDS.md) |
| Follow React coding standards | [standards/REACT-STANDARDS.md](standards/REACT-STANDARDS.md) |
| Ensure accessibility compliance | [standards/ACCESSIBILITY.md](standards/ACCESSIBILITY.md) |
| Write tests | [standards/TESTING.md](standards/TESTING.md) |
| See code examples | [examples/](examples/) |
| Add a new API endpoint | [guides/adding-endpoints.md](guides/adding-endpoints.md) |
| Add a new UI component | [guides/adding-components.md](guides/adding-components.md) |

### Updating Documentation

When contributing, update documentation as needed:

| Change Type | Documentation Updates Required |
|-------------|-------------------------------|
| **New feature** | Update relevant technical guide, add examples |
| **API change** | Update [technical/api-reference.md](technical/api-reference.md) |
| **Breaking change** | Create ADR in [architecture/decisions/](architecture/decisions/), update migration guide |
| **Bug fix** | Usually none, unless it changes documented behavior |

For the ADR template and documentation best practices, see [DOCUMENTATION-STRATEGY.md](DOCUMENTATION-STRATEGY.md).

---

## 💻 Code Comments

Write clear code comments that explain **why**, not what:

```python
# ✅ GOOD - Explains reasoning
def calculate_dew_point(temp_f: float, humidity: float) -> float:
    """
    Calculate dew point using Magnus formula.

    Uses the simplified Magnus formula which is accurate for
    typical weather conditions (temp: -40°F to 122°F, RH: 1-100%).
    """
    # Magnus formula constants (empirically derived)
    a = 17.27
    b = 237.7
    ...

# ❌ BAD - Just restates code
def calc(t, h):
    # Convert to celsius
    tc = (t - 32) * 5/9
    # Return result
    return result
```

---

## 🔒 Security

### Pre-Commit Hook Installation

Install the pre-commit hook to prevent accidentally committing sensitive files:

**Linux/macOS:**
```bash
cp scripts/git-hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

**Windows:**
```powershell
Copy-Item scripts/git-hooks/pre-commit .git/hooks/pre-commit
```

The hook blocks commits containing `.env` files and warns about other potential secrets.

### Credential Management

- ✅ Use `.env` file for local development (in `.gitignore`)
- ✅ Use `.env.example` for documenting required variables
- ❌ Never hardcode API keys in source code
- ❌ Never commit `.env` files

See [technical/deployment-guide.md](technical/deployment-guide.md#credential-security) for credential rotation instructions.

---

**Last Updated:** January 14, 2026
