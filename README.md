# IT Ticket System (MVP)

> **Portfolio Project #3** — IT Support Specialist  
> A ticket management system that demonstrates core ITSM workflow concepts through code.

---

## Overview

Built to show understanding of the ITSM ticket lifecycle without formal helpdesk experience.  
The core logic that runs inside enterprise tools like ServiceNow — ticket intake, auto-classification, priority assignment, and status tracking — is implemented from scratch using Python and SQLite.

```
Ticket Created → Auto-Classified → Priority Assigned → Status Tracked → Resolved & Logged
```

---

## Concepts Demonstrated

| ITSM Concept | Implementation |
|---|---|
| **Ticket Lifecycle** | Open → In Progress → Resolved status management |
| **Auto-Categorization** | Keyword analysis → Network / Hardware / Software / General |
| **SLA Priority Logic** | Condition-based P1–P4 automatic assignment |
| **Audit Log** | Every status change is recorded to the database with timestamp and note |
| **Status Filtering** | Query tickets by priority and current status |

---

## SLA Priority Logic

```
P1 (Critical) : Full service outage / multiple users affected   → Immediate response
P2 (High)     : Single user fully blocked / security issue
P3 (Medium)   : Work impacted but a workaround exists
P4 (Low)      : General inquiry / software install request
```

Network issues default to P2 due to high business impact.  
Tickets mentioning a specific device (printer, monitor, etc.) are routed to Hardware regardless of other keyword matches.

---

## Project Structure

```
it-ticket-system/
├── database.py       # SQLite setup, CRUD operations, and audit log
├── classifier.py     # Auto-categorization and SLA priority logic
├── main.py           # CLI interface (create / list / view / update)
├── test_system.py    # Automated test suite (19 cases)
└── tickets.db        # SQLite database (created at runtime)
```

---

## Usage

```bash
# Create a new ticket (auto-classified and prioritized)
python main.py create

# List all tickets
python main.py list

# Filter by status
python main.py list --status Open
python main.py list --status "In Progress"

# View ticket detail and full status history
python main.py view 1

# Update ticket status
python main.py update 1

# Run test suite
python test_system.py
```

---

## Example Session

```
$ python main.py create

  Title       : Printer not responding
  Description : HP printer offline, cannot print documents

  -- Auto-Analysis Result --
  Category : Hardware
  Priority : P3

  Create ticket? (y/n): y

  Ticket #1 created successfully!
```

```
$ python main.py update 1

  Ticket #1: Printer not responding
  Current status : Open

  Available      : Open / In Progress / Resolved
  New status     : In Progress
  Note (optional): Checking printer drivers

  Status updated: Open -> In Progress
```

```
$ python main.py view 1

  Title         : Printer not responding
  Category      : Hardware
  Priority      : P3
  Status        : In Progress
  ...

  -- Status History --
  2026-03-26 10:00:00  Created as Open         Ticket created
  2026-03-26 10:05:00  Open -> In Progress     Checking printer drivers
```

---

## Connection to Other Portfolio Projects

This project is designed to integrate with the other tools in this portfolio:

```
sys-health-check        →  Detects anomalies and triggers automatic ticket creation  [planned]
network-troubleshooter  →  Injects diagnostic output into ticket description         [planned]
it-ticket-system        →  Syncs tickets with ServiceNow PDI via REST API            [planned]
```

---

## Roadmap

- [ ] **v1.1** — `sys-health-check` integration: auto-create tickets on system alerts
- [ ] **v1.2** — ServiceNow PDI API integration: sync tickets with a real enterprise instance
- [ ] **v1.3** — Escalation logic: alert when P1/P2 tickets exceed SLA response time
- [ ] **v2.0** — Web dashboard (Flask): browser-based ticket management UI

---

## Tech Stack

- **Language**: Python 3.x
- **Database**: SQLite3 (standard library)
- **Interface**: CLI (`argparse`)
- **Testing**: Custom test runner — 19 test cases, 100% pass rate
