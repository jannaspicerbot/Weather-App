# Git Hooks

This directory contains Git hooks that help maintain repository security and code quality.

## Available Hooks

### pre-commit

Prevents accidentally committing sensitive files to version control.

**What it does:**
- ❌ **Blocks** commits containing `.env` files
- ⚠️ **Warns** about other potential secret files (`secrets.py`, `*.pem`, `*.key`, `credentials.json`)
- 📝 **Provides** clear error messages with remediation steps

**Why it's important:**
- Provides defense-in-depth beyond `.gitignore`
- Catches accidental force-adds (`git add -f`)
- Helps prevent credential leaks before they reach version control

## Installation

These hooks are **not automatically installed** when you clone the repository. You must manually copy them to your local `.git/hooks` directory.

### Linux/macOS

```bash
# From repository root
cp scripts/git-hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### Windows

```powershell
# From repository root
Copy-Item scripts/git-hooks/pre-commit .git/hooks/pre-commit
```

## Testing the Hook

Test that the pre-commit hook is working:

```bash
# Try to stage .env file (should be blocked by .gitignore first)
git add .env

# If somehow staged, the hook will prevent commit
git commit -m "Test commit"
# Expected: Hook blocks the commit with error message
```

## Bypassing Hooks (Use with Caution)

In rare cases where you need to bypass the hook:

```bash
# Skip all hooks for this commit (NOT RECOMMENDED)
git commit --no-verify -m "Your message"
```

**⚠️ Warning:** Only bypass hooks if you're absolutely certain the commit is safe. This defeats the security protection.

## Updating Hooks

If hooks are updated in the repository:

```bash
# Re-copy the updated hook
cp scripts/git-hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit  # Linux/macOS only
```

## Adding New Hooks

When contributing new Git hooks:

1. **Create the hook** in `scripts/git-hooks/`
2. **Make it executable**: `chmod +x scripts/git-hooks/<hook-name>`
3. **Document it** in this README
4. **Update** [docs/CONTRIBUTING.md](../../docs/CONTRIBUTING.md) with installation instructions
5. **Test** the hook locally before committing

## Best Practices

- **Never commit sensitive data** - The hook is a safety net, not a replacement for good practices
- **Keep hooks fast** - Slow hooks disrupt development workflow
- **Provide clear messages** - Help developers understand and fix issues
- **Make hooks optional** - Don't force developers to use hooks, but encourage it

## References

- [Git Hooks Documentation](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks)
- [Credential Security Guide](../../docs/technical/deployment-guide.md#credential-security)
- [Contributing Guide](../../docs/CONTRIBUTING.md#security-best-practices)

---

**Last Updated:** January 6, 2026
