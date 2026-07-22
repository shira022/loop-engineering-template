#!/usr/bin/env python3
"""Validate config files: sub-agent definitions, schedules, MCP configs, and STATE.md."""
import sys, json, os, yaml
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
errors = []
warnings = []

def validate_sub_agents():
    agents_dir = BASE / ".agents" / "agents"
    if not agents_dir.exists():
        warnings.append("No .agents/agents/ directory found (optional)")
        return
    for f in sorted(agents_dir.glob("*.yaml")):
        if f.name == "_template.yaml":
            continue
        try:
            data = yaml.safe_load(f.read_text())
        except yaml.YAMLError as e:
            errors.append(f"agents/{f.name}: Invalid YAML: {e}")
            continue
        if not isinstance(data, dict):
            errors.append(f"agents/{f.name}: Not a dictionary")
            continue
        for field in ["name", "role", "description", "instructions"]:
            if field not in data:
                errors.append(f"agents/{f.name}: Missing required field '{field}'")
        role = data.get("role", "")
        valid_roles = {"explorer", "implementer", "verifier", "custom"}
        if role not in valid_roles:
            errors.append(f"agents/{f.name}: Invalid role '{role}'. Valid: {', '.join(sorted(valid_roles))}")
        tools = data.get("tools", {})
        if isinstance(tools, dict):
            denied = set(tools.get("denied", []))
            role_tool_check = {
                "explorer": {"write", "deploy"},
                "verifier": {"write", "deploy"},
            }
            expected_denied = role_tool_check.get(role, set())
            if role in role_tool_check and not expected_denied.issubset(denied):
                warnings.append(f"agents/{f.name}: {role} should deny {expected_denied}")
        if not errors:
            print(f"  ✅ agents/{f.name}")

def validate_schedules():
    config_dir = BASE / ".agents" / "config"
    if not config_dir.exists():
        warnings.append("No .agents/config/ directory found (optional)")
        return
    for f in sorted(config_dir.glob("*.yaml")):
        try:
            data = yaml.safe_load(f.read_text())
        except yaml.YAMLError as e:
            errors.append(f"config/{f.name}: Invalid YAML: {e}")
            continue
        if not isinstance(data, dict) or "schedules" not in data:
            errors.append(f"config/{f.name}: Missing top-level 'schedules' key")
            continue
        for i, sched in enumerate(data["schedules"]):
            for field in ["id", "name", "description", "cadence", "prompt"]:
                if field not in sched:
                    errors.append(f"config/{f.name}: schedule #{i} missing '{field}'")
            cadence = sched.get("cadence", "")
            if cadence not in ("on-pr", "continuous") and not any(c.isdigit() for c in cadence):
                warnings.append(f"config/{f.name}: schedule '{sched.get('id', i)}': cadence '{cadence}' doesn't look like cron or recognized keyword")
        if not any(e.startswith(f"config/{f.name}") for e in errors):
            print(f"  ✅ config/{f.name} ({len(data.get('schedules', []))} schedule(s))")

def validate_mcp():
    mcp_dir = BASE / ".mcp"
    if not mcp_dir.exists():
        warnings.append("No .mcp/ directory found (optional)")
        return
    for f in sorted(mcp_dir.glob("*.json")):
        if f.name == "database.json":
            continue
        try:
            data = json.loads(f.read_text())
        except json.JSONDecodeError as e:
            errors.append(f".mcp/{f.name}: Invalid JSON: {e}")
            continue
        if "mcpServers" not in data:
            errors.append(f".mcp/{f.name}: Missing 'mcpServers' key")
            continue
        for name, srv in data["mcpServers"].items():
            if "command" not in srv:
                errors.append(f".mcp/{f.name}: server '{name}' missing 'command'")
        print(f"  ✅ .mcp/{f.name}")

def validate_state_file():
    """Check STATE.md has placeholder values — warn before release if stale."""
    state_file = BASE / "STATE.md"
    if not state_file.exists():
        warnings.append("STATE.md not found (expected for template)")
        return
    content = state_file.read_text()
    # In a template, the state file should use placeholder dates
    if "2026" in content or "2025" in content:
        warnings.append("STATE.md contains hardcoded dates — reset to YYYY-MM-DD placeholders before release")

def main():
    print("🔍 Validating sub-agent definitions...")
    validate_sub_agents()
    print()
    print("🔍 Validating schedule configs...")
    validate_schedules()
    print()
    print("🔍 Validating MCP configs...")
    validate_mcp()
    print()
    print("🔍 Validating STATE.md...")
    validate_state_file()
    print()
    print(f"---\nErrors: {len(errors)}, Warnings: {len(warnings)}")
    for w in warnings:
        print(f"  ⚠️  {w}")
    for e in errors:
        print(f"  ❌ {e}")
    if errors:
        sys.exit(1)
    print("🎉 All configs valid!")

if __name__ == "__main__":
    main()
