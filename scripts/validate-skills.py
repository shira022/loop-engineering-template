#!/usr/bin/env python3
"""
Validate all skill SKILL.md files in .agents/skills/ for:
- Required YAML frontmatter fields (name, description, tags, category)
- Valid YAML syntax
- Correct file structure

Exit code: 0 = all valid, 1 = errors found
"""
import sys
import os
import yaml
from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parent.parent / ".agents" / "skills"
REQUIRED_FIELDS = ["name", "description", "tags", "category"]
VALID_CATEGORIES = {"development", "meta", "testing", "documentation", "management"}


def validate_skill(skill_path: Path) -> list[str]:
    errors = []
    skill_file = skill_path / "SKILL.md"

    if not skill_file.exists():
        errors.append(f"  ❌ Missing SKILL.md in {skill_path.name}")
        return errors

    content = skill_file.read_text(encoding="utf-8")

    # Check YAML frontmatter (between --- delimiters)
    if not content.startswith("---"):
        errors.append(f"  ❌ {skill_path.name}/SKILL.md: Missing YAML frontmatter (must start with '---')")
        return errors

    # Extract frontmatter
    parts = content.split("---")
    if len(parts) < 3:
        errors.append(f"  ❌ {skill_path.name}/SKILL.md: Malformed YAML frontmatter (need opening and closing '---')")
        return errors

    frontmatter_str = parts[1]

    try:
        frontmatter = yaml.safe_load(frontmatter_str)
    except yaml.YAMLError as e:
        errors.append(f"  ❌ {skill_path.name}/SKILL.md: Invalid YAML: {e}")
        return errors

    if not isinstance(frontmatter, dict):
        errors.append(f"  ❌ {skill_path.name}/SKILL.md: Frontmatter is not a dictionary")
        return errors

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in frontmatter:
            errors.append(f"  ❌ {skill_path.name}/SKILL.md: Missing required field '{field}'")
        elif field == "category" and frontmatter.get(field) not in VALID_CATEGORIES:
            errors.append(f"  ❌ {skill_path.name}/SKILL.md: Invalid category '{frontmatter.get(field)}'. Valid: {', '.join(sorted(VALID_CATEGORIES))}")

    # Check name format (kebab-case)
    name = frontmatter.get("name", "")
    if name and not all(c.isalnum() or c in "-_" for c in name):
        errors.append(f"  ⚠️  {skill_path.name}/SKILL.md: name '{name}' contains special characters (expected kebab-case)")

    return errors


def main():
    if not SKILLS_DIR.exists():
        print(f"⚠️  Skills directory not found: {SKILLS_DIR}")
        print("Make sure you're running from the project root.")
        sys.exit(1)

    print(f"🔍 Scanning skills in {SKILLS_DIR}...\n")

    all_errors = []
    validated_count = 0

    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir():
            continue
        validated_count += 1
        errors = validate_skill(skill_dir)
        if errors:
            all_errors.extend(errors)
            for e in errors:
                print(e)
        else:
            print(f"  ✅ {skill_dir.name}")

    print(f"\n---")
    print(f"Validated: {validated_count} skills")
    print(f"Errors:    {len(all_errors)}")

    if all_errors:
        sys.exit(1)
    else:
        print("🎉 All skills are valid!")
        sys.exit(0)


if __name__ == "__main__":
    main()
