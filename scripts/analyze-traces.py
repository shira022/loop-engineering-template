#!/usr/bin/env python3
"""
Agent Execution Trace Analyzer

Analyzes JSON trace files in the traces/ directory and produces
aggregated metrics about agent sessions.

Usage:
    python3 scripts/analyze-traces.py            # Analyze all traces
    python3 scripts/analyze-traces.py --json     # Output as JSON
    python3 scripts/analyze-traces.py --limit 10 # Show last 10 sessions
"""

import json
import sys
import os
import glob
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter, defaultdict

TRACES_DIR = Path(__file__).resolve().parent.parent / "traces"


def load_traces():
    """Load all JSON trace files sorted by timestamp (newest first)."""
    if not TRACES_DIR.exists():
        return []

    traces = []
    for f in sorted(TRACES_DIR.glob("*.json"), reverse=True):
        try:
            data = json.loads(f.read_text())
            data["_file"] = f.name
            traces.append(data)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"⚠️  Skipping {f.name}: {e}", file=sys.stderr)

    return traces


def analyze(traces, output_json=False, limit=None):
    """Analyze traces and print or return metrics."""
    if not traces:
        print("ℹ️  No trace files found.")
        return

    if limit:
        traces = traces[:limit]

    total = len(traces)
    total_tool_calls = sum(t.get("tool_calls", 0) for t in traces)
    total_tokens = sum(t.get("tokens_used", 0) for t in traces)

    # Skills loaded analysis
    skills_counter = Counter()
    for t in traces:
        for skill in t.get("skills_loaded", []):
            skills_counter[skill] += 1

    # Activity timeline
    dates = []
    for t in traces:
        started = t.get("started_at", "")
        if started:
            try:
                dt = datetime.fromisoformat(started)
                dates.append(dt.strftime("%Y-%m-%d"))
            except (ValueError, TypeError):
                pass

    day_counter = Counter(dates)

    # Session duration estimate
    durations = []
    for t in traces:
        start = t.get("started_at", "")
        end = t.get("completed_at", "")
        if start and end:
            try:
                s = datetime.fromisoformat(start)
                e = datetime.fromisoformat(end)
                durations.append((e - s).total_seconds() / 60)
            except (ValueError, TypeError):
                pass

    avg_duration = sum(durations) / len(durations) if durations else 0

    # Files created/modified
    all_files_created = []
    all_files_modified = []
    for t in traces:
        all_files_created.extend(t.get("files_created", []))
        all_files_modified.extend(t.get("files_modified", []))

    # --- Output ---
    if output_json:
        report = {
            "total_sessions": total,
            "total_tool_calls": total_tool_calls,
            "total_tokens_used": total_tokens,
            "avg_tool_calls_per_session": round(total_tool_calls / total, 1) if total else 0,
            "avg_tokens_per_session": round(total_tokens / total, 0) if total else 0,
            "avg_duration_minutes": round(avg_duration, 1),
            "total_files_created": len(all_files_created),
            "total_files_modified": len(all_files_modified),
            "skills_usage": dict(skills_counter.most_common()),
            "sessions_per_day": dict(sorted(day_counter.items())),
            "timeframe_days": len(day_counter),
        }
        print(json.dumps(report, indent=2))
        return

    # Human-readable output
    print(f"{'─' * 60}")
    print(f"  📊 Agent Session Analysis")
    print(f"{'─' * 60}")
    print(f"  Total sessions:             {total}")
    print(f"  Total tool calls:           {total_tool_calls}")
    print(f"  Total tokens used:          {total_tokens:,}")
    print(f"  Avg tool calls/session:     {total_tool_calls / total:.1f}" if total else "  N/A")
    print(f"  Avg tokens/session:         {total_tokens / total:,.0f}" if total else "  N/A")
    print(f"  Avg session duration:       {avg_duration:.1f} min" if durations else "  N/A")
    print(f"  Total files created:        {len(all_files_created)}")
    print(f"  Total files modified:       {len(all_files_modified)}")
    print(f"  Active days:                {len(day_counter)}")
    print()

    if skills_counter:
        print(f"{'─' * 60}")
        print(f"  🧠 Skills Used")
        print(f"{'─' * 60}")
        for skill, count in skills_counter.most_common(10):
            pct = count / total * 100
            bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
            print(f"  {skill:30s} {count:3d}× {bar} {pct:.0f}%")

    if day_counter:
        print()
        print(f"{'─' * 60}")
        print(f"  📅 Activity Timeline")
        print(f"{'─' * 60}")
        for date, count in sorted(day_counter.items()):
            bar = "▓" * count + "░" * (10 - count)
            print(f"  {date}  {bar} {count} sessions")

    if durations:
        print()
        print(f"{'─' * 60}")
        print(f"  ⏱️  Session Duration Distribution")
        print(f"{'─' * 60}")
        buckets = {"<5m": 0, "5-15m": 0, "15-30m": 0, "30-60m": 0, ">60m": 0}
        for d in durations:
            if d < 5: buckets["<5m"] += 1
            elif d < 15: buckets["5-15m"] += 1
            elif d < 30: buckets["15-30m"] += 1
            elif d < 60: buckets["30-60m"] += 1
            else: buckets[">60m"] += 1
        for bucket, count in buckets.items():
            if count > 0:
                bar = "▓" * count + "░" * (max(10 - count, 0))
                print(f"  {bucket:10s} {bar} {count} sessions")

    print()
    print(f"{'─' * 60}")
    print(f"  💡 Tip: Run with --json for machine-readable output")
    print(f"{'─' * 60}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze agent execution traces",
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of sessions")
    args = parser.parse_args()

    traces = load_traces()
    analyze(traces, output_json=args.json, limit=args.limit)


if __name__ == "__main__":
    main()
