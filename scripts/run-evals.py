#!/usr/bin/env python3
"""Run skill evaluations using evals/evals.json."""
import sys, json, argparse
from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parent.parent / ".agents" / "skills"

def validate_eval(skill_name, eval_data):
    errors = []
    for field in ["id", "prompt", "expected_output"]:
        if field not in eval_data:
            errors.append(f"  [ERROR] {skill_name}: eval #{eval_data.get('id', '?')} missing '{field}'")
    if "assertions" in eval_data:
        if not isinstance(eval_data["assertions"], list) or len(eval_data["assertions"]) == 0:
            errors.append(f"  [WARN] {skill_name}: eval #{eval_data.get('id', '?')} has empty/non-list assertions")
    return errors

def run_skill(name, path):
    errors = []
    ef = path / "evals" / "evals.json"
    if not ef.exists(): return errors
    try:
        data = json.loads(ef.read_text())
    except json.JSONDecodeError as e:
        errors.append(f"  [ERROR] {name}/evals/evals.json: invalid JSON: {e}")
        return errors
    if "skill_name" not in data: errors.append(f"  [ERROR] {name}/evals/evals.json: missing 'skill_name'")
    if "evals" not in data: errors.append(f"  [ERROR] {name}/evals/evals.json: missing 'evals' array"); return errors
    for e in data["evals"]:
        errors.extend(validate_eval(name, e))
    if not errors: print(f"  [OK] {name}: {len(data['evals'])} eval(s) valid")
    return errors

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill", help="Run eval for a specific skill only")
    args = parser.parse_args()
    if not SKILLS_DIR.exists(): print("Skills directory not found"); sys.exit(1)
    print("Running evaluations...\n")
    all_errors, count = [], 0
    for d in sorted(SKILLS_DIR.iterdir()):
        if not d.is_dir(): continue
        if args.skill and d.name != args.skill: continue
        count += 1
        all_errors.extend(run_skill(d.name, d))
    print(f"\n---\nChecked: {count} skills, Issues: {len(all_errors)}")
    sys.exit(1 if all_errors else 0)

if __name__ == "__main__":
    main()
