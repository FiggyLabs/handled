*Part of [Figgy Labs](https://github.com/FiggyLabs/figgy-labs)*

# ✅ Handled

**Someone said they'd handle it. Did they?**

Decisions get made. Owners get named. Then nothing is tracked and nobody follows up. Handled logs what people committed to doing and surfaces what's overdue — in one command.

---

## Demo

```bash
# Log commitments as they're made
python3 handled.py add "Tom: migrate staging to Railway by Thursday" --due 2026-04-04
python3 handled.py add "Priya: VAT compliance research" --due 2026-04-07
python3 handled.py add "Maya: confirm go-live date with stakeholders"

# See everything open
python3 handled.py list

# Friday arrives
python3 handled.py overdue
```

**Output:**

```
  2 overdue commitments

  [2026-03-27 09:14]  #a1b2c3d4  🔴
  Commitment: Tom: migrate staging to Railway by Thursday
  Owner:      tom
  Due:        2026-04-04  ← 2 days overdue

  [2026-03-27 11:30]  #e5f6a7b8  🔴
  Commitment: Priya: VAT compliance research
  Owner:      priya
  Due:        2026-04-07  ← 1 day overdue
```

```bash
# Mark it done when it happens
python3 handled.py done a1b2c3d4

  ✅ Done  #a1b2c3d4
  Tom: migrate staging to Railway by Thursday
```

---

## Install

```bash
git clone https://github.com/FiggyLabs/handled
cd handled
```

Python 3.8+. No dependencies. Nothing to install.

---

## Usage

```bash
# Add a commitment (owner auto-parsed from "Name: task" format)
python3 handled.py add "Tom: migrate staging by Thursday" --due 2026-04-04

# Add with explicit owner
python3 handled.py add "Update the infra docs" --owner charlie --due 2026-04-01

# List all open commitments
python3 handled.py list

# Show only overdue (past due date, or open with no date for 7+ days)
python3 handled.py overdue

# Mark done (use full ID or any unique prefix)
python3 handled.py done a1b2c3d4

# Search by keyword or owner name
python3 handled.py find priya
python3 handled.py find "staging"
```

---

## How it fits with Settled and Stamped

```bash
# Settled extracts the decision from the Slack thread
python3 settled.py --file thread.txt
→ Decision: Use Stripe. Owner: Tom. Actions: migrate staging, add keys.

# Stamped logs it permanently
python3 stamped.py add "Stripe approved for billing. Owner: Tom."

# Handled tracks the follow-through
python3 handled.py add "Tom: migrate staging by Thursday" --due 2026-04-04
python3 handled.py add "Priya: add Stripe keys to secrets manager"

# Check in on Friday
python3 handled.py overdue
```

Three tools. One workflow. Decisions made, stored, and followed through.

---

## Storage

Commitments are stored in `~/.handled.json` — a plain append-only JSON file on your machine. Nothing leaves.

Override the path:

```bash
HANDLED_LOG=./team.json python3 handled.py list
```

---

## Roadmap

**v1 — current**
- `add`, `list`, `done`, `overdue`, `find`
- Auto-parses owner from `"Name: task"` format
- Overdue detection by due date or stale age (7+ days)
- Local JSON storage, env override

**v1.1**
- `cancel` command
- `edit` — update due date or text in place
- `summary` — X open, Y overdue, Z done this week
- Color output (red/green) via ANSI, no deps added

**v2**
- Web UI (`handled --web`) — same pattern as Settled
- Import from Settled JSON output
- Weekly digest Markdown export

---

## License

MIT
