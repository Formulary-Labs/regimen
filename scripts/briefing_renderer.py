#!/usr/bin/env python3
"""
Daily Briefing Renderer
=======================
Reads a program pipeline run JSON file and produces a clean,
human-readable markdown briefing digest.

Usage:
    python briefing_renderer.py --run path/to/run.json
    python briefing_renderer.py --run path/to/run.json --output path/to/briefing.md
    python briefing_renderer.py --run path/to/run.json --stdout

Dependencies:
    pip install rich          # optional — for terminal preview
    Standard library only for markdown file output

Repo path: /scripts/briefing_renderer.py
"""

import json
import argparse
import sys
from datetime import datetime, date
from pathlib import Path

try:
    from rich.console import Console
    from rich.markdown import Markdown
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_run(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def fmt_date(date_str: str | None) -> str:
    if not date_str:
        return "TBD"
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
        today = date.today()
        delta = (d - today).days
        if delta == 0:
            return f"{date_str} (**TODAY**)"
        elif delta < 0:
            return f"{date_str} (**{abs(delta)}d overdue**)"
        elif delta <= 3:
            return f"{date_str} (in {delta}d ⚠️)"
        else:
            return date_str
    except ValueError:
        return date_str


def health_badge(health: str) -> str:
    return {
        "green":   "🟢 GREEN",
        "yellow":  "🟡 YELLOW",
        "red":     "🔴 RED",
        "unknown": "⚪ UNKNOWN",
    }.get(health.lower(), f"⚪ {health.upper()}")


def priority_badge(priority: str) -> str:
    return {
        "high":   "🔴 HIGH",
        "medium": "🟡 MEDIUM",
        "low":    "🟢 LOW",
    }.get(priority.lower(), priority)


def status_badge(status: str) -> str:
    return {
        "yellow": "🟡 YELLOW",
        "red":    "🔴 RED",
    }.get(status.lower(), status)


def safe_get(d: dict, *keys, default=""):
    """Safely traverse nested dict keys."""
    for key in keys:
        if not isinstance(d, dict):
            return default
        d = d.get(key, default)
    return d if d is not None else default


# ---------------------------------------------------------------------------
# Section renderers
# ---------------------------------------------------------------------------

def render_header(run: dict) -> str:
    manifest = run.get("run_manifest", {})
    state = run.get("program_state", {})
    run_date = manifest.get("run_date", "Unknown")
    program = manifest.get("program_name", "Unknown Program")
    pm = manifest.get("pm_name", "")
    health = state.get("overall_health", "unknown")
    one_liner = state.get("one_line_status", "")
    prior = manifest.get("prior_run_date")

    lines = [
        f"# Daily Briefing — {program}",
        f"**Date:** {run_date}  ",
        f"**PM:** {pm}  " if pm else "",
        f"**Program Health:** {health_badge(health)}  ",
        f"**Status:** {one_liner}  " if one_liner else "",
        f"**Prior Run:** {prior}" if prior else "**Prior Run:** None (first run)",
        "",
        "---",
        "",
    ]
    return "\n".join(l for l in lines if l is not None)


def render_run_manifest(run: dict) -> str:
    manifest = run.get("run_manifest", {})
    routing = manifest.get("routing_plan", {})

    lines = ["## Run Manifest", ""]
    for spec, result in routing.items():
        icon = "✅" if result == "completed" else "⏭️"
        lines.append(f"- {icon} **{spec.capitalize()}:** {result}")

    notes = manifest.get("run_notes", "")
    if notes:
        lines += ["", f"_{notes}_"]

    lines += ["", "---", ""]
    return "\n".join(lines)


def render_decision_queue(run: dict) -> str:
    queue = safe_get(run, "monitoring_output", "decision_queue", default=[])

    lines = ["## 🎯 Decision Queue", ""]

    if not queue:
        lines += ["_No decisions required today._", "", "---", ""]
        return "\n".join(lines)

    lines.append(f"**{len(queue)} item(s) require your action today.**")
    lines.append("")

    for i, item in enumerate(queue, 1):
        lines += [
            f"### {i}. {item.get('item', 'Unnamed item')}",
            f"- **Action needed:** {item.get('action_needed', 'See notes')}",
            f"- **Owner:** {item.get('owner', 'Unknown')}",
            f"- **Due:** {fmt_date(item.get('due'))}",
            f"- **Priority:** {priority_badge(item.get('priority', 'medium'))}",
            "",
        ]

    lines += ["---", ""]
    return "\n".join(lines)


def render_summary_view(run: dict) -> str:
    summary = safe_get(run, "monitoring_output", "summary_view", default={})

    lines = ["## 📊 Summary View", ""]

    if not summary:
        lines += ["_No monitoring data available._", "", "---", ""]
        return "\n".join(lines)

    fields = [
        ("Items due in horizon",       "items_due_in_horizon"),
        ("Items Yellow",                "items_yellow"),
        ("Items Red",                   "items_red"),
        ("Owners with no recent update","owners_no_recent_update"),
        ("Upcoming milestones",         "upcoming_milestones"),
    ]

    for label, key in fields:
        val = summary.get(key, 0)
        flag = " ⚠️" if key in ("items_red",) and val > 0 else ""
        flag = flag or (" 👀" if key in ("items_yellow", "owners_no_recent_update") and val > 0 else "")
        lines.append(f"- **{label}:** {val}{flag}")

    lines += ["", "---", ""]
    return "\n".join(lines)


def render_watch_list(run: dict) -> str:
    watch = safe_get(run, "monitoring_output", "watch_list", default=[])

    lines = ["## 👀 Watch List", ""]

    if not watch:
        lines += ["_Nothing on the watch list._", "", "---", ""]
        return "\n".join(lines)

    for item in watch:
        lines += [
            f"- **{item.get('item', 'Unknown')}**",
            f"  - Owner: {item.get('owner', 'Unknown')}",
            f"  - Risk: {item.get('risk', 'Unspecified')}",
            f"  - Check in by: {fmt_date(item.get('check_in_by'))}",
            "",
        ]

    lines += ["---", ""]
    return "\n".join(lines)


def render_escalations(run: dict) -> str:
    items = safe_get(run, "monitoring_output", "escalation_items", default=[])

    lines = ["## 🚨 Escalations", ""]

    if not items:
        lines += ["_No active escalations._", "", "---", ""]
        return "\n".join(lines)

    for item in items:
        lines += [
            f"- **{item.get('item', 'Unknown')}** — {status_badge(item.get('status', ''))}",
            f"  - Trigger: {item.get('trigger', 'See notes')}",
            f"  - Action: {item.get('action', 'See notes')}",
            "",
        ]

    lines += ["---", ""]
    return "\n".join(lines)


def render_vendor_snapshot(run: dict) -> str:
    vendor = run.get("vendor_output", {})
    if not vendor or vendor.get("source") == "null":
        return ""

    scorecard = vendor.get("scorecard", {})
    remediation = vendor.get("remediation_plan", {})
    vendor_name = vendor.get("vendor_name", "Unknown Vendor")
    overall = scorecard.get("overall", 0)
    trend = scorecard.get("trend", "unknown")

    trend_icon = {
        "improving": "📈",
        "stable": "➡️",
        "declining": "📉",
        "insufficient_data": "❓",
    }.get(trend, "❓")

    lines = [
        "## 🤝 Vendor Snapshot",
        "",
        f"**Vendor:** {vendor_name}  ",
        f"**Overall Score:** {overall}/5 {trend_icon} ({trend})",
        "",
    ]

    if remediation.get("required"):
        checkpoint = fmt_date(remediation.get("checkpoint_date"))
        lines += [
            "⚠️ **Active Remediation Plan**",
            f"- Checkpoint: {checkpoint}",
            f"- Open actions: {len(remediation.get('corrective_actions', []))}",
            "",
        ]

    lines += ["---", ""]
    return "\n".join(lines)


def render_communications(run: dict) -> str:
    monitoring_comms = safe_get(run, "monitoring_output", "draft_communications", default=[])
    vendor_comms = safe_get(run, "vendor_output", "draft_communications", default=[])
    all_comms = monitoring_comms + vendor_comms

    lines = ["## 📬 Communications to Send Today", ""]

    if not all_comms:
        lines += ["_No communications queued._", "", "---", ""]
        return "\n".join(lines)

    for i, comm in enumerate(all_comms, 1):
        lines += [
            f"### {i}. {comm.get('type', 'Communication').replace('_', ' ').title()}",
            f"- **To:** {comm.get('to', 'Unknown')}",
            f"- **Channel:** {comm.get('channel', 'Unknown')}",
            f"- **Subject:** {comm.get('subject', 'See draft')}",
            "",
            "<details><summary>View draft</summary>",
            "",
            f"{comm.get('body', '_No body._')}",
            "",
            "</details>",
            "",
        ]

    lines += ["---", ""]
    return "\n".join(lines)


def render_calendar(run: dict) -> str:
    events = safe_get(run, "monitoring_output", "calendar_events", default=[])

    lines = ["## 📅 Calendar Events to Create", ""]

    if not events:
        lines += ["_No calendar events to create._", "", "---", ""]
        return "\n".join(lines)

    for event in events:
        rec = event.get("recurrence", "none")
        pm_flag = " ✋ PM action required" if event.get("pm_action_required") else ""
        lines += [
            f"- **{event.get('title', 'Untitled')}**",
            f"  - Date: {fmt_date(event.get('date'))}",
            f"  - Recurrence: {rec}",
            f"  - Owner: {event.get('owner', 'Unknown')}{pm_flag}",
        ]
        if event.get("notes"):
            lines.append(f"  - Notes: {event['notes']}")
        lines.append("")

    lines += ["---", ""]
    return "\n".join(lines)


def render_flags(run: dict) -> str:
    flags = run.get("flags", {})
    all_flags = []

    flag_labels = {
        "owner_needed":            "OWNER NEEDED",
        "date_needed":             "DATE NEEDED",
        "escalation_path_needed":  "ESCALATION PATH NEEDED",
        "inferred":                "INFERRED",
        "conflicts":               "CONFLICT — VERIFY",
        "insufficient_data":       "INSUFFICIENT DATA",
        "unresolved_from_prior_run": "UNRESOLVED FROM PRIOR RUN",
    }

    for key, label in flag_labels.items():
        for item in flags.get(key, []):
            all_flags.append(f"- `[{label}]` {item}")

    lines = ["## 🚩 Flags Requiring Resolution", ""]

    if not all_flags:
        lines += ["_No open flags._", "", "---", ""]
    else:
        lines += all_flags + ["", "---", ""]

    return "\n".join(lines)


def render_next_run(run: dict) -> str:
    rec = run.get("next_run_recommendation", {})

    lines = ["## 🔁 Next Run Recommendation", ""]

    if not rec:
        lines += ["_No recommendation available._", ""]
        return "\n".join(lines)

    lines += [
        f"- **Suggested date:** {fmt_date(rec.get('suggested_date'))}",
        f"- **Intent:** {rec.get('suggested_intent', 'Unknown')}",
        f"- **Reason:** {rec.get('reason', 'See flags')}",
        "",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main renderer
# ---------------------------------------------------------------------------

def render_briefing(run: dict) -> str:
    sections = [
        render_header(run),
        render_run_manifest(run),
        render_decision_queue(run),
        render_summary_view(run),
        render_watch_list(run),
        render_escalations(run),
        render_vendor_snapshot(run),
        render_communications(run),
        render_calendar(run),
        render_flags(run),
        render_next_run(run),
    ]
    return "\n".join(s for s in sections if s)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Render a program pipeline run JSON as a markdown briefing.")
    parser.add_argument("--run", required=True, help="Path to the pipeline run JSON file")
    parser.add_argument("--output", help="Path to write markdown output (default: briefing_YYYY-MM-DD.md next to run file)")
    parser.add_argument("--stdout", action="store_true", help="Print markdown to stdout instead of writing a file")
    parser.add_argument("--preview", action="store_true", help="Render a rich terminal preview (requires 'rich')")
    args = parser.parse_args()

    run_path = Path(args.run)
    if not run_path.exists():
        print(f"ERROR: Run file not found: {args.run}", file=sys.stderr)
        sys.exit(1)

    run = load_run(run_path)
    briefing = render_briefing(run)

    if args.stdout:
        print(briefing)
        return

    if args.preview:
        if RICH_AVAILABLE:
            console = Console()
            console.print(Markdown(briefing))
        else:
            print("WARNING: 'rich' not installed. Install with: pip install rich")
            print(briefing)
        return

    if args.output:
        out_path = Path(args.output)
    else:
        run_date = run.get("run_manifest", {}).get("run_date", date.today().isoformat())
        program = run.get("run_manifest", {}).get("program_name", "program").lower().replace(" ", "_")
        out_path = run_path.parent / f"briefing_{program}_{run_date}.md"

    out_path.write_text(briefing, encoding="utf-8")
    print(f"Briefing written to: {out_path}")


if __name__ == "__main__":
    main()
