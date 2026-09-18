#!/usr/bin/env python3
"""
Draft Email Formatter
=====================
Reads a program pipeline run JSON file and produces one markdown
file per draft communication in a /drafts output directory.

Files are named and organized for easy review, light editing, and sending.

Usage:
    python draft_formatter.py --run path/to/run.json
    python draft_formatter.py --run path/to/run.json --output path/to/drafts/
    python draft_formatter.py --run path/to/run.json --list

Dependencies:
    Standard library only

Repo path: /scripts/draft_formatter.py
"""

import json
import argparse
import sys
from datetime import date
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_run(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def safe_get(d: dict, *keys, default=""):
    for key in keys:
        if not isinstance(d, dict):
            return default
        d = d.get(key, default)
    return d if d is not None else default


def slugify(text: str) -> str:
    return (
        text.lower()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
        .replace(":", "")
        .replace("—", "")
        .replace("–", "")
        .strip("_")
    )


COMM_TYPE_LABELS = {
    "weekly_status_request":  "Weekly Status Request",
    "at_risk_nudge":          "At-Risk Nudge",
    "escalation_notice":      "Escalation Notice",
    "stakeholder_report":     "Stakeholder Status Report",
    "weekly_checkin":         "Vendor Weekly Check-In",
    "remediation_notice":     "Vendor Remediation Notice",
    "leadership_briefing":    "Leadership Briefing",
}

COMM_PRIORITY = {
    "escalation_notice":   1,
    "remediation_notice":  2,
    "at_risk_nudge":       3,
    "leadership_briefing": 4,
    "stakeholder_report":  5,
    "weekly_status_request": 6,
    "weekly_checkin":      7,
}


# ---------------------------------------------------------------------------
# Draft file renderer
# ---------------------------------------------------------------------------

def render_draft(comm: dict, program: str, run_date: str, index: int) -> str:
    comm_type = comm.get("type", "communication")
    label = COMM_TYPE_LABELS.get(comm_type, comm_type.replace("_", " ").title())
    to = comm.get("to", "")
    channel = comm.get("channel", "")
    subject = comm.get("subject", "")
    body = comm.get("body", "_No body provided._")

    lines = [
        f"# Draft: {label}",
        "",
        f"**Program:** {program}  ",
        f"**Run Date:** {run_date}  ",
        f"**Type:** `{comm_type}`  ",
        "",
        "---",
        "",
        "## Header",
        "",
        f"**To:** {to}  " if to else "",
        f"**Channel:** {channel}  " if channel else "",
        f"**Subject:** {subject}  " if subject else "",
        "",
        "---",
        "",
        "## Body",
        "",
        body,
        "",
        "---",
        "",
        "## Send Checklist",
        "",
        "- [ ] Review and edit body for accuracy",
        "- [ ] Confirm recipient(s)",
        "- [ ] Attach any supporting documents if needed",
        "- [ ] Send via correct channel",
        "- [ ] Log send date in program tracker",
        "",
    ]

    return "\n".join(l for l in lines if l is not None)


# ---------------------------------------------------------------------------
# Index renderer
# ---------------------------------------------------------------------------

def render_index(drafts: list[dict], program: str, run_date: str) -> str:
    lines = [
        f"# Draft Communications Index",
        f"**Program:** {program}  ",
        f"**Run Date:** {run_date}  ",
        f"**Total Drafts:** {len(drafts)}  ",
        "",
        "---",
        "",
        "| # | Type | To | Channel | File |",
        "|---|---|---|---|---|",
    ]

    for d in drafts:
        comm = d["comm"]
        fname = d["filename"]
        label = COMM_TYPE_LABELS.get(comm.get("type", ""), comm.get("type", ""))
        to = comm.get("to", "—")
        channel = comm.get("channel", "—")
        lines.append(f"| {d['index']} | {label} | {to} | {channel} | `{fname}` |")

    lines += ["", "---", "", "_Review each draft, edit lightly, and send._", ""]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main formatter
# ---------------------------------------------------------------------------

def collect_communications(run: dict) -> list[dict]:
    monitoring_comms = safe_get(run, "monitoring_output", "draft_communications", default=[])
    vendor_comms = safe_get(run, "vendor_output", "draft_communications", default=[])
    all_comms = monitoring_comms + vendor_comms

    # Deduplicate by type+to combination
    seen = set()
    unique = []
    for comm in all_comms:
        key = (comm.get("type", ""), comm.get("to", ""))
        if key not in seen:
            seen.add(key)
            unique.append(comm)

    # Sort by priority
    unique.sort(key=lambda c: COMM_PRIORITY.get(c.get("type", ""), 99))
    return unique


def format_drafts(run: dict, output_dir: Path, list_only: bool = False) -> list[dict]:
    manifest = run.get("run_manifest", {})
    program = manifest.get("program_name", "program")
    run_date = manifest.get("run_date", date.today().isoformat())

    comms = collect_communications(run)

    if not comms:
        print("No draft communications found in run JSON.")
        return []

    draft_manifest = []

    for i, comm in enumerate(comms, 1):
        comm_type = comm.get("type", "communication")
        to_slug = slugify(comm.get("to", "unknown")[:30])
        filename = f"{i:02d}_{comm_type}_{to_slug}.md"

        draft_manifest.append({
            "index": i,
            "comm": comm,
            "filename": filename,
        })

        if list_only:
            label = COMM_TYPE_LABELS.get(comm_type, comm_type)
            print(f"  {i:02d}. [{label}] → {comm.get('to', 'Unknown')} ({comm.get('channel', '?')})")
            continue

        content = render_draft(comm, program, run_date, i)
        out_file = output_dir / filename
        out_file.write_text(content, encoding="utf-8")

    if not list_only and draft_manifest:
        index_content = render_index(draft_manifest, program, run_date)
        index_file = output_dir / "00_index.md"
        index_file.write_text(index_content, encoding="utf-8")
        print(f"Index written to: {index_file}")

    return draft_manifest


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Format draft communications from a pipeline run JSON.")
    parser.add_argument("--run", required=True, help="Path to the pipeline run JSON file")
    parser.add_argument("--output", help="Directory to write draft files (default: /drafts/ next to run file)")
    parser.add_argument("--list", action="store_true", help="List available drafts without writing files")
    args = parser.parse_args()

    run_path = Path(args.run)
    if not run_path.exists():
        print(f"ERROR: Run file not found: {args.run}", file=sys.stderr)
        sys.exit(1)

    run = load_run(run_path)

    if args.list:
        print("Draft communications available in this run:")
        format_drafts(run, output_dir=Path("."), list_only=True)
        return

    if args.output:
        output_dir = Path(args.output)
    else:
        program = run.get("run_manifest", {}).get("program_name", "program").lower().replace(" ", "_")
        run_date = run.get("run_manifest", {}).get("run_date", date.today().isoformat())
        output_dir = run_path.parent / "drafts" / f"{program}_{run_date}"

    output_dir.mkdir(parents=True, exist_ok=True)
    drafts = format_drafts(run, output_dir)

    if drafts:
        print(f"\n{len(drafts)} draft(s) written to: {output_dir}")
        print("Run with --list to preview without writing files.")


if __name__ == "__main__":
    main()
