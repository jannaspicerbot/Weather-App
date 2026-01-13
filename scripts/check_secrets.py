#!/usr/bin/env python3
"""Pre-commit hook to prevent committing sensitive files.

Called by pre-commit framework to block .env, credentials.json, and secrets.py.
"""

import subprocess
import sys


def main():
    """Check if sensitive files are staged for commit."""
    # Get list of staged files
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
    )

    staged_files = result.stdout.strip().split("\n") if result.stdout.strip() else []

    # Patterns to block
    blocked_patterns = [".env", "credentials.json", "secrets.py"]

    # Check for sensitive files
    blocked_files = []
    for f in staged_files:
        for pattern in blocked_patterns:
            if f == pattern or f.endswith("/" + pattern):
                blocked_files.append(f)

    if blocked_files:
        print("")
        print("ERROR: Attempting to commit sensitive file(s)!")
        print("")
        print("The following sensitive files were detected:")
        for f in blocked_files:
            print(f"  - {f}")
        print("")
        print("To fix: git reset HEAD <file>")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
