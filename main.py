"""
main.py
IT Ticket System — CLI Interface

Usage:
    python main.py create              # Create a new ticket
    python main.py list                # List all tickets
    python main.py list --status Open  # Filter by status
    python main.py view <id>           # View ticket detail + history
    python main.py update <id>         # Update ticket status
"""

import argparse
import sys
from app.services.database import initialize_db, insert_ticket, update_status, get_ticket, get_all_tickets, get_ticket_history
from app.services.classifier import analyze_ticket
from app.services.config import get_ticket_config

# ── ANSI color codes ──────────────────────────────────────────────────────────
COLORS = {
    "P1": "\033[91m",
    "P2": "\033[93m",
    "P3": "\033[94m",
    "P4": "\033[92m",
    "RESET": "\033[0m",
    "BOLD": "\033[1m",
    "DIM": "\033[2m",
    "CYAN": "\033[96m",
}

# Loaded from config — edit config.json to change status flow
STATUS_FLOW = get_ticket_config()["valid_statuses"]


def color(text, code):
    return f"{COLORS.get(code, '')}{text}{COLORS['RESET']}"


def print_header(text):
    print(f"\n{color('=' * 55, 'BOLD')}")
    print(f"  {color(text, 'BOLD')}")
    print(f"{color('=' * 55, 'BOLD')}\n")


def print_ticket_row(ticket):
    pri = ticket["priority"]
    status_col = {
        "Open":        "\033[91mOpen       \033[0m",
        "In Progress": "\033[93mIn Progress\033[0m",
        "Resolved":    "\033[92mResolved   \033[0m",
    }.get(ticket["status"], ticket["status"])

    print(
        f"  [{color(str(ticket['id']).zfill(4), 'CYAN')}] "
        f"{color(pri, pri):<18} "
        f"{status_col}  "
        f"{ticket['category']:<10} "
        f"{ticket['title'][:40]}"
    )


def print_ticket_detail(ticket):
    pri = ticket["priority"]
    print_header(f"Ticket #{ticket['id']}")
    print(f"  {'Title':<14}: {color(ticket['title'], 'BOLD')}")
    print(f"  {'Category':<14}: {ticket['category']}")
    print(f"  {'Priority':<14}: {color(pri, pri)}")
    print(f"  {'Status':<14}: {ticket['status']}")
    print(f"  {'Created':<14}: {ticket['created_at']}")
    print(f"  {'Updated':<14}: {ticket['updated_at']}")
    if ticket.get("resolved_at"):
        print(f"  {'Resolved':<14}: {ticket['resolved_at']}")
    print(f"\n  {'Description':<14}:")
    print(f"  {color(ticket['description'], 'DIM')}\n")


def cmd_create():
    print_header("Create New Ticket")
    title = input("  Title       : ").strip()
    if not title:
        print("  [ERROR] Title cannot be empty.")
        return

    description = input("  Description : ").strip()
    if not description:
        print("  [ERROR] Description cannot be empty.")
        return

    result   = analyze_ticket(title, description)
    category = result["category"]
    priority = result["priority"]

    print(f"\n  {color('-- Auto-Analysis Result --', 'CYAN')}")
    print(f"  Category : {category}")
    print(f"  Priority : {color(priority, priority)}")

    confirm = input("\n  Create ticket? (y/n): ").strip().lower()
    if confirm != "y":
        print("  Cancelled.")
        return

    ticket_id = insert_ticket(title, description, category, priority)
    print(f"\n  {color(f'Ticket #{ticket_id} created successfully!', 'BOLD')}\n")


def cmd_list(status_filter=None):
    tickets = get_all_tickets(status_filter)
    label   = f"Tickets ({status_filter})" if status_filter else "All Tickets"
    print_header(label)

    if not tickets:
        print("  No tickets found.\n")
        return

    print(f"  {'ID':<8} {'Priority':<10} {'Status':<13} {'Category':<10} Title")
    print(f"  {color('-' * 50, 'DIM')}")
    for t in tickets:
        print_ticket_row(t)
    print(f"\n  Total: {len(tickets)} ticket(s)\n")


def cmd_view(ticket_id):
    ticket = get_ticket(ticket_id)
    if not ticket:
        print(f"  [ERROR] Ticket #{ticket_id} not found.")
        return

    print_ticket_detail(ticket)

    history = get_ticket_history(ticket_id)
    print(f"  {color('-- Status History --', 'CYAN')}")
    for h in history:
        arrow = (
            f"{h['old_status']} -> {h['new_status']}"
            if h["old_status"]
            else f"Created as {h['new_status']}"
        )
        print(f"  {h['changed_at']}  {arrow}  {color(h['note'] or '', 'DIM')}")
    print()


def cmd_update(ticket_id):
    ticket = get_ticket(ticket_id)
    if not ticket:
        print(f"  [ERROR] Ticket #{ticket_id} not found.")
        return

    current = ticket["status"]
    print(f"\n  Ticket #{ticket_id}: {ticket['title']}")
    print(f"  Current status : {color(current, 'BOLD')}")
    print(f"\n  Available      : {' / '.join(STATUS_FLOW)}")

    new_status = input("  New status     : ").strip()
    if new_status not in STATUS_FLOW:
        print(f"  [ERROR] Invalid status. Choose from: {', '.join(STATUS_FLOW)}")
        return

    if new_status == current:
        print("  [INFO] Status unchanged.")
        return

    note = input("  Note (optional): ").strip() or None
    ok, msg = update_status(ticket_id, new_status, note)
    if ok:
        print(f"\n  {color(msg, 'BOLD')}\n")
    else:
        print(f"  [ERROR] {msg}\n")


def main():
    initialize_db()

    parser = argparse.ArgumentParser(
        description="IT Ticket System CLI",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("create", help="Create a new ticket")

    list_parser = subparsers.add_parser("list", help="List tickets")
    list_parser.add_argument("--status", choices=STATUS_FLOW, help="Filter by status")

    view_parser = subparsers.add_parser("view", help="View ticket detail and history")
    view_parser.add_argument("id", type=int, help="Ticket ID")

    update_parser = subparsers.add_parser("update", help="Update ticket status")
    update_parser.add_argument("id", type=int, help="Ticket ID")

    args = parser.parse_args()

    if args.command == "create":
        cmd_create()
    elif args.command == "list":
        cmd_list(args.status)
    elif args.command == "view":
        cmd_view(args.id)
    elif args.command == "update":
        cmd_update(args.id)
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()