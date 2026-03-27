# IT Ticket System

> "I built tools to detect problems. Then I realized I had no system to track what I did about them."

A lightweight ITSM ticketing system that closes the gap between **detecting a fault** and **managing the resolution process** — built as the governance layer on top of my existing [sys-health-check](../sys-health-check) and [network-troubleshooter](../network-troubleshooter) diagnostic tools.

---

## 📌 Performance Impact

| Metric | Before (Ad-hoc) | After (This System) |
|---|---|---|
| Incident Tracking | Verbal / email only — no record | Every ticket logged with full history |
| Priority Decision | Subjective, case-by-case | Rule-based SLA logic (P1–P4) |
| Classification Time | Manual categorization per ticket | Auto-classified on creation |
| Audit Trail | Often missing | Full status change log in SQLite |
| Tool Integration | Diagnostic tools ran in isolation | Alerts feed directly into ticket creation |

---

## 📋 Scenario & Problem Statement

### The Solo IT Support Problem

**The Situation:**
After building a system health monitor and a network diagnostic tool, I ran into a structural gap. Both tools were good at *detecting* problems — but there was no centralized place to track *what happened next*. Alerts were acted on in the moment and then forgotten. There was no record of what broke, when, how it was resolved, or whether a similar issue had occurred before.

**The Problem:**
In a small IT environment — or as a solo support person — it's easy to fall into a reactive loop:
- Issues come in verbally or by email with no structure
- Priority decisions are made on gut feeling, not defined criteria
- No incident history means the same problems get re-diagnosed from scratch
- There's no way to demonstrate response times or resolution rates

**The Solution:**
A purpose-built ITSM system that implements the core ITIL ticket lifecycle — intake, classification, prioritization, status tracking, and audit logging — without the overhead of an enterprise platform.

> *"Having developed standalone diagnostic tools, I realized the need for a centralized governance layer. This project bridges the gap between 'detecting a fault' and 'managing the resolution process' by implementing a custom ITSM workflow."*

---

## 🔁 How It Fits Into the Bigger Picture

This is the third tool in a connected IT support automation pipeline:

```
sys-health-check
  └─ Detects CPU, memory, disk anomalies
       └─ [v1.1] Auto-creates a ticket with diagnostic output attached

network-troubleshooter
  └─ Runs full-stack network diagnostics
       └─ [v1.1] Injects diagnosis report into ticket description

it-ticket-system  ◄── You are here
  └─ Receives alerts, classifies, prioritizes, and tracks to resolution
       └─ [v1.2] Syncs with ServiceNow PDI via REST API
```

Each tool solves a distinct problem. Together they simulate a complete IT support workflow — from first alert to closed ticket.

---

## ⚙️ Core Features (MVP)

| ITSM Concept | Implementation |
|---|---|
| **Ticket Lifecycle** | Open → In Progress → Resolved |
| **Auto-Categorization** | Keyword analysis → Network / Hardware / Software / General |
| **SLA Priority Logic** | Condition-based P1–P4 automatic assignment |
| **Audit Log** | Every status change recorded with timestamp and note |
| **Status Filtering** | Query tickets by status or priority |

---

## 🎯 SLA Priority Logic

```
P1 (Critical) : Full service outage / multiple users affected   → Immediate response
P2 (High)     : Single user fully blocked / security issue
P3 (Medium)   : Work impacted but a workaround exists
P4 (Low)      : General inquiry / software install request
```

Network issues default to **P2** due to high business impact.  
Tickets mentioning a specific device (printer, monitor, etc.) are routed to **Hardware** regardless of other keyword matches.

---

## 📁 Project Structure

```
it-ticket-system/
├── database.py       # SQLite setup, CRUD operations, and audit log
├── classifier.py     # Auto-categorization and SLA priority logic
├── main.py           # CLI interface (create / list / view / update)
├── test_system.py    # Automated test suite (24/24 passing)
└── tickets.db        # SQLite database (created at runtime)
```

---

## 🚀 Usage

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

## 📊 Sample Session

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
$ python main.py view 1

  Title         : Printer not responding
  Category      : Hardware
  Priority      : P3
  Status        : In Progress

  -- Status History --
  2026-03-26 10:00:00  Created as Open
  2026-03-26 10:05:00  Open -> In Progress   Checking printer drivers
```

---

## 🗺️ Roadmap

- [ ] **v1.1** — `sys-health-check` + `network-troubleshooter` integration: auto-create tickets on alerts
- [ ] **v1.2** — ServiceNow PDI API integration: sync with a real enterprise instance
- [ ] **v1.3** — Escalation logic: flag P1/P2 tickets that breach SLA response time
- [ ] **v2.0** — Web dashboard (Flask): browser-based ticket management UI

---

## 🛠️ Tech Stack

- **Language**: Python 3.x
- **Database**: SQLite3 (standard library)
- **Interface**: CLI (`argparse`)
- **Testing**: Custom test runner — 24 test cases, 100% pass rate