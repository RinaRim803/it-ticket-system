"""
test_system.py
Automated test suite for IT Ticket System

Covers:
  - Auto-categorization
  - SLA priority assignment
  - Ticket CRUD operations
  - Status transitions
  - Audit log / history
  - Status filtering
"""

import os
import sys

# Use a separate DB file for testing
from app.services import database
database.DB_PATH = "test_tickets.db"

from app.services.database import initialize_db, insert_ticket, update_status, get_ticket, get_all_tickets, get_ticket_history
from app.services.classifier import analyze_ticket

PASS = "\033[92m PASS\033[0m"
FAIL = "\033[91m FAIL\033[0m"
passed = 0
failed = 0


def check(label, condition):
    global passed, failed
    if condition:
        passed += 1
        print(f"  [{PASS}]  {label}")
    else:
        failed += 1
        print(f"  [{FAIL}]  {label}")
    return condition


def section(title):
    print(f"\n\033[1m-- {title} --\033[0m")


def run_tests():
    # Clean up any previous test DB
    if os.path.exists("test_tickets.db"):
        os.remove("test_tickets.db")
    initialize_db()

    # ── Auto-Categorization ───────────────────────────────────────────────────
    section("Auto-Categorization")
    category_cases = [
        ("WiFi keeps disconnecting in the office",  "internet connection drops every hour",   "Network"),
        ("Printer not responding",                   "HP printer offline, cannot print",       "Hardware"),
        ("Outlook crashes on startup",               "Office 365 Outlook crashes every time",  "Software"),
        ("Need help with new badge",                 "I need access to the 3rd floor",         "General"),
    ]
    for title, desc, expected in category_cases:
        result = analyze_ticket(title, desc)
        check(
            f'"{title[:40]}" -> {result["category"]} (expected: {expected})',
            result["category"] == expected
        )

    # ── SLA Priority Assignment ───────────────────────────────────────────────
    section("SLA Priority Assignment")
    priority_cases = [
        ("Server outage",         "All users cannot access the system, entire office down",   "P1"),
        ("VPN not working",       "I cannot access internal resources, urgent need for work", "P2"),
        ("Network slow",          "Internet connection is slow but still usable",             "P2"),
        ("Excel formula issue",   "VLOOKUP not working in my spreadsheet",                   "P3"),
        ("Request new software",  "Would like to have Figma installed on my machine",        "P4"),
    ]
    for title, desc, expected in priority_cases:
        result = analyze_ticket(title, desc)
        check(
            f'"{title}" -> {result["priority"]} (expected: {expected})',
            result["priority"] == expected
        )

    # ── Ticket CRUD ───────────────────────────────────────────────────────────
    section("Ticket CRUD")
    tid = insert_ticket("Test ticket", "This is a test description", "Software", "P3")
    check("insert_ticket returns a valid ID",        tid is not None and tid > 0)

    ticket = get_ticket(tid)
    check("get_ticket returns correct title",        ticket["title"] == "Test ticket")
    check("get_ticket default status is Open",       ticket["status"] == "Open")
    check("get_ticket category matches",             ticket["category"] == "Software")

    all_tickets = get_all_tickets()
    check("get_all_tickets returns at least one",    len(all_tickets) >= 1)

    # ── Status Transitions ────────────────────────────────────────────────────
    section("Status Transitions")
    ok, msg = update_status(tid, "In Progress", "Starting investigation")
    check("Open -> In Progress succeeds",            ok)

    ticket = get_ticket(tid)
    check("Status is now In Progress",               ticket["status"] == "In Progress")

    ok, msg = update_status(tid, "Resolved", "Issue fixed")
    check("In Progress -> Resolved succeeds",        ok)

    ticket = get_ticket(tid)
    check("Status is now Resolved",                  ticket["status"] == "Resolved")
    check("resolved_at timestamp is recorded",       ticket["resolved_at"] is not None)

    # ── Audit Log / History ───────────────────────────────────────────────────
    section("Audit Log / History")
    history = get_ticket_history(tid)
    check("History has 3 entries (create + 2 updates)", len(history) == 3)
    check("First entry note is 'Ticket created'",    history[0]["note"] == "Ticket created")
    check("Last entry new_status is Resolved",       history[-1]["new_status"] == "Resolved")

    # ── Status Filtering ──────────────────────────────────────────────────────
    section("Status Filtering")
    insert_ticket("Open ticket A", "desc", "Network", "P1")
    insert_ticket("Open ticket B", "desc", "Hardware", "P3")
    open_tickets = get_all_tickets(status_filter="Open")
    check("Filtering Open returns only Open tickets",
          all(t["status"] == "Open" for t in open_tickets))
    check("At least 2 Open tickets exist",           len(open_tickets) >= 2)

    # ── Summary ───────────────────────────────────────────────────────────────
    total = passed + failed
    print(f"\n\033[1m{'=' * 40}\033[0m")
    print(f"  Results: {passed}/{total} passed", end="")
    if failed == 0:
        print("  \033[92mAll tests passed.\033[0m")
    else:
        print(f"  \033[91m{failed} failed.\033[0m")
    print(f"\033[1m{'=' * 40}\033[0m\n")

    # Clean up test DB
    os.remove("test_tickets.db")

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    run_tests()
