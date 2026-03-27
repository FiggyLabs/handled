#!/usr/bin/env python3
"""
Handled — Someone said they'd handle it. Did they?

Usage:
  Add:      python3 handled.py add "Tom: migrate staging by Thursday" --due 2024-04-04
  List:     python3 handled.py list
  Done:     python3 handled.py done a1b2c3d4
  Overdue:  python3 handled.py overdue
  Find:     python3 handled.py find tom
"""

import json
import os
import sys
import argparse
import textwrap
import uuid
from datetime import datetime, date

# ── Storage ───────────────────────────────────────────────────────────────────

LOG_FILE = os.getenv("HANDLED_LOG", os.path.expanduser("~/.handled.json"))


def _load() -> list:
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE) as f:
        return json.load(f)


def _save(entries: list):
    with open(LOG_FILE, "w") as f:
        json.dump(entries, f, indent=2)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _new_id() -> str:
    return str(uuid.uuid4())[:8]


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _fmt_dt(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return iso


def _parse_owner(text: str) -> str:
    """Best-effort: if text starts with 'Name:' treat Name as owner."""
    if ":" in text:
        candidate = text.split(":")[0].strip()
        if len(candidate.split()) <= 2 and candidate.isalpha() or " " not in candidate:
            return candidate.lower()
    return ""


def _days_overdue(due_str: str) -> int:
    try:
        due = date.fromisoformat(due_str)
        return (date.today() - due).days
    except Exception:
        return 0


def _status_icon(entry: dict) -> str:
    if entry["status"] == "done":
        return "✅"
    if entry.get("due_date"):
        if _days_overdue(entry["due_date"]) > 0:
            return "🔴"
    return "⏳"


def _get(entries: list, partial_id: str) -> dict | None:
    for e in entries:
        if e["id"].startswith(partial_id):
            return e
    return None


# ── Display ───────────────────────────────────────────────────────────────────

def _print_entry(e: dict, width: int = 72):
    icon    = _status_icon(e)
    created = _fmt_dt(e["created_at"])
    eid     = e["id"]
    lines   = textwrap.wrap(e["raw_text"], width - 4)

    print(f"  [{created}]  #{eid}  {icon}")
    for i, line in enumerate(lines):
        prefix = "  Commitment: " if i == 0 else "               "
        print(f"{prefix}{line}")

    if e.get("owner"):
        print(f"  Owner:       {e['owner']}")
    if e.get("due_date"):
        days = _days_overdue(e["due_date"])
        suffix = f"  ← {days} day{'s' if days != 1 else ''} overdue" if days > 0 and e["status"] == "open" else ""
        print(f"  Due:         {e['due_date']}{suffix}")
    if e["status"] == "done" and e.get("completed_at"):
        print(f"  Completed:   {_fmt_dt(e['completed_at'])}")
    print()


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_add(raw_text: str, due_date: str = None, owner: str = None):
    if not raw_text.strip():
        print("Error: commitment text cannot be empty.", file=sys.stderr)
        sys.exit(1)

    entries = _load()
    entry = {
        "id":           _new_id(),
        "raw_text":     raw_text.strip(),
        "owner":        (owner or _parse_owner(raw_text)).lower(),
        "due_date":     due_date or None,
        "status":       "open",
        "created_at":   _now(),
        "completed_at": None,
    }
    entries.append(entry)
    _save(entries)

    print(f"\n  Handled [{entry['id']}]  {_fmt_dt(entry['created_at'])}")
    print(f"  {entry['raw_text']}")
    if entry["due_date"]:
        print(f"  Due: {entry['due_date']}")
    print()


def cmd_list(show_done: bool = False):
    entries = _load()
    items = entries if show_done else [e for e in entries if e["status"] == "open"]
    if not items:
        msg = "No commitments logged yet." if not entries else "No open commitments."
        print(f"\n  {msg}")
        print('  Try: python3 handled.py add "Tom: migrate staging by Thursday"\n')
        return
    print()
    for e in items:
        _print_entry(e)


def cmd_done(partial_id: str):
    entries = _load()
    entry = _get(entries, partial_id)
    if not entry:
        print(f"  No entry found matching '{partial_id}'.", file=sys.stderr)
        sys.exit(1)
    if entry["status"] == "done":
        print(f"  #{entry['id']} is already marked done.")
        return
    entry["status"]       = "done"
    entry["completed_at"] = _now()
    _save(entries)
    print(f"\n  ✅ Done  #{entry['id']}")
    print(f"  {entry['raw_text']}\n")


def cmd_overdue():
    entries = _load()
    items = [
        e for e in entries
        if e["status"] == "open"
        and e.get("due_date")
        and _days_overdue(e["due_date"]) > 0
    ]
    # also surface open items with no due date open for more than 7 days
    stale = [
        e for e in entries
        if e["status"] == "open"
        and not e.get("due_date")
        and (datetime.now() - datetime.fromisoformat(e["created_at"])).days > 7
    ]
    if not items and not stale:
        print("\n  No overdue commitments. All good.\n")
        return

    total = len(items) + len(stale)
    print(f"\n  {total} overdue commitment{'s' if total != 1 else ''}\n")
    for e in items:
        _print_entry(e)
    for e in stale:
        days_open = (datetime.now() - datetime.fromisoformat(e["created_at"])).days
        print(f"  #{e['id']}  {e['raw_text']}")
        print(f"  No deadline — open for {days_open} days\n")


def cmd_find(query: str):
    entries = _load()
    q = query.lower()
    matches = [
        e for e in entries
        if q in e["raw_text"].lower() or q in (e.get("owner") or "").lower()
    ]
    if not matches:
        print(f'\n  No commitments found matching "{query}".\n')
        return
    print(f'\n  {len(matches)} result(s) for "{query}"\n')
    for e in matches:
        _print_entry(e)


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Handled — track whether promised follow-through actually happened.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Examples:
          python3 handled.py add "Tom: migrate staging by Thursday" --due 2024-04-04
          python3 handled.py add "Priya: VAT research" --owner priya --due 2024-04-07
          python3 handled.py list
          python3 handled.py overdue
          python3 handled.py done a1b2c3d4
          python3 handled.py find tom
        """),
    )

    sub = parser.add_subparsers(dest="command")

    p_add = sub.add_parser("add", help="Log a new commitment")
    p_add.add_argument("raw_text", help="The commitment text")
    p_add.add_argument("--due",   "-d", help="Due date (YYYY-MM-DD)")
    p_add.add_argument("--owner", "-o", help="Owner name (auto-parsed if omitted)")

    sub.add_parser("list",    help="Show all open commitments")
    sub.add_parser("overdue", help="Show past-due and stale commitments")

    p_done = sub.add_parser("done", help="Mark a commitment as complete")
    p_done.add_argument("id", help="Commitment ID (or prefix)")

    p_find = sub.add_parser("find", help="Search commitments by keyword or owner")
    p_find.add_argument("query", help="Keyword or owner name")

    args = parser.parse_args()

    if args.command == "add":
        cmd_add(args.raw_text, due_date=args.due, owner=args.owner)
    elif args.command == "list":
        cmd_list()
    elif args.command == "overdue":
        cmd_overdue()
    elif args.command == "done":
        cmd_done(args.id)
    elif args.command == "find":
        cmd_find(args.query)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
