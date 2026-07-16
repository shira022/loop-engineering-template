---
type: learning
date: 2026-07-16
source: skill-crafter / meta
priority: high
---

# 2026-07-16: Skill Frontmatter Standardization Pattern

## What I Learned

All 8 skills in the template need consistent frontmatter fields (`version`, `metadata.depends_on`, `compatibility`, `metadata.hermes.tags`) to ensure cross-agent compatibility. Duplicate version fields (top-level + metadata) cause confusion and should be eliminated.

## Pattern

When standardizing multiple similar files (SKILL.md frontmatters), batch-edit using find-and-replace with context-aware matching rather than rewriting entire files. Always validate with `validate-skills.py` after editing.

## Reusable For

- Onboarding new skills into the template
- Bulk frontmatter updates
- Ensuring agentskills.io compliance

## Files Changed

- 8 SKILL.md frontmatters updated
- 4 evals/evals.json created
- All validated with zero errors
