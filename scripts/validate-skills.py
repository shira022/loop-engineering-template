#!/usr/bin/env python3
"""
Validate all skill SKILL.md files in .agents/skills/ for:
- Required YAML frontmatter fields (name, description, tags, category)
- Valid YAML syntax
- Correct file structure
- Token count (warning if >5000)
- Description length (warning if <10 chars)
- Directory name vs frontmatter name match (error if mismatch)
- Progressive disclosure suggestion
- Eval file presence check

Exit code: 0 = all valid, 1 = errors found
"""
import sys
import os
import yaml
from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parent.parent / ".agents" / "skills"
REQUIRED_FIELDS = ["name", "description", "tags", "category"]
VALID_CATEGORIES = {"development", "meta", "testing", "documentation", "management"}


def validate_skill(skill_path: Path) -> tuple[list[str], list[str], list[str]]:
    errors = []
    warnings = []
    infos = []
    skill_file = skill_path / "SKILL.md"

    if not skill_file.exists():
        errors.append(f"  ❌ Missing SKILL.md in {skill_path.name}")
        return errors, warnings, infos

    content = skill_file.read_text(encoding="utf-8")

    if not content.startswith("---"):
        errors.append(f"  ❌ {skill_path.name}/SKILL.md: Missing YAML frontmatter (must start with '---')")
        return errors, warnings, infos

    parts = content.split("---")
    if len(parts) < 3:
        errors.append(f"  ❌ {skill_path.name}/SKILL.md: Malformed YAML frontmatter (need opening and closing '---')")
        return errors, warnings, infos

    frontmatter_str = parts[1]
    body = "---".join(parts[2:])

    try:
        frontmatter = yaml.safe_load(frontmatter_str)
    except yaml.YAMLError as e:
        errors.append(f"  ❌ {skill_path.name}/SKILL.md: Invalid YAML: {e}")
        return errors, warnings, infos

    if not isinstance(frontmatter, dict):
        errors.append(f"  ❌ {skill_path.name}/SKILL.md: Frontmatter is not a dictionary")
        return errors, warnings, infos

    for field in REQUIRED_FIELDS:
        if field not in frontmatter:
            errors.append(f"  ❌ {skill_path.name}/SKILL.md: Missing required field '{field}'")
        elif field == "category" and frontmatter.get(field) not in VALID_CATEGORIES:
            errors.append(f"  ❌ {skill_path.name}/SKILL.md: Invalid category '{frontmatter.get(field)}'. Valid: {', '.join(sorted(VALID_CATEGORIES))}")

    name = frontmatter.get("name", "")
    if name and not all(c.isalnum() or c in "-_" for c in name):
        warnings.append(f"  ⚠️  {skill_path.name}/SKILL.md: name '{name}' contains special characters (expected kebab-case)")

    body_stripped = body.strip()
    token_estimate = len(body_stripped) // 4

    if token_estimate > 5000:
        warnings.append(f"  ⚠️  {skill_path.name}/SKILL.md: Estimated token count is {token_estimate} (exceeds 5000)")

    desc = frontmatter.get("description", "")
    if len(desc) < 10:
        warnings.append(f"  ⚠️  {skill_path.name}/SKILL.md: Description too short ({len(desc)} chars, minimum 10)")

    if name and name != skill_path.name:
        errors.append(f"  ❌ {skill_path.name}/SKILL.md: Directory name '{skill_path.name}' does not match frontmatter name '{name}'")

    body_lines = len(body_stripped.splitlines())
    has_refs = (skill_path / "references").is_dir()
    has_scripts = (skill_path / "scripts").is_dir()
    if (body_lines > 500 or token_estimate > 5000) and not has_refs and not has_scripts:
        warnings.append(f"  💡 {skill_path.name}/SKILL.md: Large skill ({body_lines} lines, ~{token_estimate} tokens). Consider using references/ or scripts/ subdirectories for progressive disclosure")

    eval_file = skill_path / "evals" / "evals.json"
    if eval_file.exists():
        infos.append(f"  ℹ️  {skill_path.name}: Has evals/evals.json")
    else:
        infos.append(f"  ℹ️  {skill_path.name}: No evals/evals.json")

    return errors, warnings, infos


def main():
    if not SKILLS_DIR.exists():
        print(f"⚠️  Skills directory not found: {SKILLS_DIR}")
        print("Make sure you're running from the project root.")
        sys.exit(1)

    print(f"🔍 Scanning skills in {SKILLS_DIR}...\n")

    all_errors = []
    all_warnings = []
    all_infos = []
    validated_count = 0
    skills_with_errors = 0

    # Skip project-bootstrapper which is intentionally self-destructed after use
    EXCLUDED_SKILLS = {"project-bootstrapper"}

    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir():
            continue
        if skill_dir.name in EXCLUDED_SKILLS:
            all_infos.append(f"  ℹ️  {skill_dir.name}: Skipped (intentionally removed after bootstrap)")
            continue
        validated_count += 1
        errors, warnings, infos = validate_skill(skill_dir)

        all_errors.extend(errors)
        all_warnings.extend(warnings)
        all_infos.extend(infos)

        if errors:
            skills_with_errors += 1
            for e in errors:
                print(e)
            for w in warnings:
                print(w)
            for i in infos:
                print(i)
        else:
            print(f"  ✅ {skill_dir.name}")
            for w in warnings:
                print(w)
            for i in infos:
                print(i)

    print(f"\n---")
    pass_count = validated_count - skills_with_errors
    pass_rate = (pass_count / validated_count * 100) if validated_count > 0 else 0
    print(f"Validated: {validated_count} skills")
    print(f"Pass rate: {pass_rate:.1f}%")
    print(f"Errors:    {len(all_errors)}")
    print(f"Warnings:  {len(all_warnings)}")
    print(f"Infos:     {len(all_infos)}")

    if all_errors:
        sys.exit(1)
    else:
        print("🎉 All skills are valid!")
        sys.exit(0)


if __name__ == "__main__":
    main()
