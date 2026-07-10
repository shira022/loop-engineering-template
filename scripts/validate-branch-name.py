#!/usr/bin/env python3
"""
Branch name validator for Git Flow convention.

Usage:
    python3 scripts/validate-branch-name.py <branch-name>

Or as a pre-push hook:
    cp scripts/validate-branch-name.py .git/hooks/pre-push
    chmod +x .git/hooks/pre-push

Returns exit code 0 if valid, 1 if invalid.
"""

import re
import sys


def validate_branch(name: str) -> tuple[bool, str]:
    """
    Validate a branch name against Git Flow conventions.

    Returns (is_valid, message).
    """
    # Permanent branches
    if name in ("main", "develop"):
        return True, f"✅ Permanent branch: {name}"

    # Feature: feature/<issue-id>-<description> or feature/<description>
    if re.match(r"^feature/[a-z0-9][a-z0-9._/-]*$", name):
        return True, f"✅ Feature branch: {name}"

    # Bugfix: bugfix/<issue-id>-<description>
    if re.match(r"^bugfix/[a-z0-9][a-z0-9._/-]*$", name):
        return True, f"✅ Bugfix branch: {name}"

    # Release: release/<semver>
    if re.match(r"^release/\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?$", name):
        return True, f"✅ Release branch: {name}"

    # Hotfix: hotfix/<semver>-<short-desc> or hotfix/<short-desc>
    if re.match(r"^hotfix/[\w][\w./-]*$", name):
        return True, f"✅ Hotfix branch: {name}"

    # Support: support/<version>
    if re.match(r"^support/[\w][\w./-]*$", name):
        return True, f"✅ Support branch: {name}"

    # Special GitHub branches
    if name in ("gh-pages", "gh-readonly-queue"):
        return True, f"✅ Special branch: {name}"

    return False, (
        f"❌ Invalid branch name: {name}\n"
        f"   Expected one of:\n"
        f"     - main, develop\n"
        f"     - feature/<name>\n"
        f"     - bugfix/<name>\n"
        f"     - release/<version>\n"
        f"     - hotfix/<version>-<desc>\n"
        f"     - support/<version>"
    )


def main():
    if len(sys.argv) < 2:
        # Read from stdin (git pre-push hook format)
        for line in sys.stdin:
            parts = line.strip().split()
            if len(parts) >= 2:
                local_ref, local_oid, remote_ref, remote_oid = parts
                branch = local_ref.replace("refs/heads/", "")
                is_valid, msg = validate_branch(branch)
                if not is_valid:
                    print(msg)
                    return 1
        return 0

    name = sys.argv[1]
    is_valid, msg = validate_branch(name)
    print(msg)
    return 0 if is_valid else 1


if __name__ == "__main__":
    sys.exit(main())
