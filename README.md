# IT Ticket System

> "I built tools to detect problems. Then I realized I had no system to track what I did about them."

A lightweight ITSM ticketing system that closes the gap between **detecting a fault** and **managing the resolution process** — built as the governance layer on top of my existing [sys-health-check](../sys-health-check) and [network-troubleshooter](../network-troubleshooter) diagnostic tools.

---

## 📌 Performance Impact

| Metric | Before (Ad-hoc) | **After (Automated System)** |
| :--- | :--- | :--- |
| **Incident Tracking** | Verbal/Email (No centralized records) | **Full lifecycle logging with persistent history** |
| **Priority Assessment** | Subjective & Inconsistent | **Rule-based SLA Logic (P1–P4 classification)** |
| **Classification Speed** | Manual categorization per ticket | **Instant auto-classification on creation** |
| **Audit Compliance** | Missing or fragmented trail | **Full status change logs (SQLite-backed)** |
| **Workflow Integration** | Isolated diagnostic tools | **End-to-end automation via REST API** |

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
  └─ Detects CPU, memory, disk, service anomalies
       └─ On WARNING: POST /api/tickets → ticket auto-created per alert

network-troubleshooter
  └─ Runs full-stack network diagnostics (L1 → cloud layer)
       └─ On FAIL: POST /api/tickets → ticket auto-created per failed check
          On PASS: prompts user to optionally save run as a record

it-ticket-system  ◄── You are here
  └─ Flask API server — receives alerts, classifies, prioritizes,
     and tracks every ticket to resolution
       └─ [v1.2] Syncs with ServiceNow PDI via REST API
```

Each tool solves a distinct problem. Together they simulate a complete IT support workflow — from first alert to closed ticket.

---

## ⚙️ Core Features

| ITSM Concept | Implementation |
|---|---|
| **Ticket Lifecycle** | Open → In Progress → Resolved |
| **Auto-Categorization** | Keyword analysis → Network / Hardware / Software / General |
| **SLA Priority Logic** | Condition-based P1–P4 automatic assignment |
| **Audit Log** | Every status change recorded with timestamp and note |
| **Status Filtering** | Query tickets by status or priority |
| **REST API** | Flask-based API server — accepts tickets from external tools via HTTP POST |
| **CLI** | Manual ticket management via command line |

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
├── server.py                    # Flask server entry point (python server.py)
├── main.py                      # CLI interface (create / list / view / update)
├── test_system.py               # Automated test suite (24/24 passing)
├── requirements.txt
├── tickets.db                   # SQLite database (created at runtime)
│
├── app/
│   ├── __init__.py              # Flask app factory — registers blueprints
│   ├── routes/
│   │   ├── tickets.py           # POST /api/tickets, GET, PATCH endpoints
│   │   └── health.py            # GET /api/health — server status check
│   └── services/
│       ├── database.py          # SQLite CRUD and audit log
│       └── classifier.py        # Auto-categorization and SLA priority logic
```

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Server status check |
| `POST` | `/api/tickets` | Create a ticket (used by integrations) |
| `GET` | `/api/tickets` | List all tickets (`?status=Open` filter available) |
| `GET` | `/api/tickets/<id>` | Get ticket detail + full status history |
| `PATCH` | `/api/tickets/<id>/status` | Update ticket status |

**POST /api/tickets — request body:**
```json
{
    "title":       "High CPU Usage Detected",
    "description": "CPU at 94% for 5 minutes on DESKTOP-01",
    "source":      "sys-health-check"
}
```

**Response:**
```json
{
    "id":       1,
    "title":    "High CPU Usage Detected",
    "category": "Hardware",
    "priority": "P2",
    "status":   "Open",
    "source":   "sys-health-check"
}
```

---

## 🚀 Usage

**Start the API server:**
```bash
python server.py
# Running on http://localhost:5000
```

**CLI — manual ticket management:**
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

**Auto-ticket from sys-health-check (HTTP):**
```
[sys-health-check] CPU WARNING detected
  [TICKET] #1 created — P2 | Hardware | High CPU Usage Detected
  [TICKET] #2 created — P2 | Hardware | High Memory Usage Detected
```

**Manual ticket via CLI:**
```
$ python main.py create

  Title       : Printer not responding
  Description : HP printer offline, cannot print documents

  -- Auto-Analysis Result --
  Category : Hardware
  Priority : P3

  Create ticket? (y/n): y
  Ticket #3 created successfully!
```

**Viewing a ticket with history:**
```
$ python main.py view 1

  Title         : High CPU Usage Detected
  Category      : Hardware
  Priority      : P2
  Status        : In Progress

  -- Status History --
  2026-03-26 10:00:00  Created as Open        Ticket created
  2026-03-26 10:08:00  Open -> In Progress    Investigating top processes
```

---

## 🗺️ Roadmap

- [x] **v1.0** — CLI MVP: SQLite CRUD, auto-categorization, SLA priority, audit log
- [x] **v1.1** — Flask REST API + integration with sys-health-check and network-troubleshooter
- [ ] **v1.2** — ServiceNow PDI API integration: sync tickets with a real enterprise instance
- [ ] **v1.3** — Escalation logic: flag P1/P2 tickets that breach SLA response time
- [ ] **v2.0** — Web dashboard (Flask + Jinja2): browser-based ticket management UI

---

## 🛠️ Tech Stack

| Layer | Technology | Role |
|---|---|---|
| **API Server** | Flask 3.x | REST endpoints — always running, receives alerts |
| **Database** | SQLite3 (stdlib) | Ticket storage and audit log |
| **Classification** | Python (regex) | Auto-categorization + SLA priority |
| **Integration** | requests | Other tools POST tickets via HTTP |
| **CLI** | argparse (stdlib) | Manual ticket management |
| **Testing** | Custom runner | 24 test cases, 100% pass rate |