"""
database.py
SQLite database management module for IT Ticket System
"""

import sqlite3
from datetime import datetime

DB_PATH = "tickets.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name like a dictionary
    return conn


def initialize_db():
    """Initialize the database — create tables if they don't exist"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT    NOT NULL,
            description TEXT    NOT NULL,
            category    TEXT    NOT NULL,   -- Network / Hardware / Software / General
            priority    TEXT    NOT NULL,   -- P1 / P2 / P3 / P4
            status      TEXT    NOT NULL DEFAULT 'Open',  -- Open / In Progress / Resolved
            created_at  TEXT    NOT NULL,
            updated_at  TEXT    NOT NULL,
            resolved_at TEXT                -- Recorded when status becomes Resolved
        )
    """)

    # Audit log table for tracking all status changes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ticket_history (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id   INTEGER NOT NULL,
            old_status  TEXT,
            new_status  TEXT    NOT NULL,
            changed_at  TEXT    NOT NULL,
            note        TEXT,
            FOREIGN KEY (ticket_id) REFERENCES tickets(id)
        )
    """)

    conn.commit()
    conn.close()
    print("[DB] Database initialized.")


def insert_ticket(title, description, category, priority):
    """Create a new ticket and return its ID"""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO tickets (title, description, category, priority, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, 'Open', ?, ?)
    """, (title, description, category, priority, now, now))

    ticket_id = cursor.lastrowid

    # Record initial creation in history log
    cursor.execute("""
        INSERT INTO ticket_history (ticket_id, old_status, new_status, changed_at, note)
        VALUES (?, NULL, 'Open', ?, 'Ticket created')
    """, (ticket_id, now))

    conn.commit()
    conn.close()
    return ticket_id


def update_status(ticket_id, new_status, note=None):
    """Update ticket status and append an entry to the history log"""
    conn = get_connection()
    cursor = conn.cursor()

    # Fetch current status before updating
    cursor.execute("SELECT status FROM tickets WHERE id = ?", (ticket_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False, "Ticket not found"

    old_status = row["status"]
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    resolved_at = now if new_status == "Resolved" else None

    if resolved_at:
        cursor.execute("""
            UPDATE tickets SET status = ?, updated_at = ?, resolved_at = ? WHERE id = ?
        """, (new_status, now, resolved_at, ticket_id))
    else:
        cursor.execute("""
            UPDATE tickets SET status = ?, updated_at = ? WHERE id = ?
        """, (new_status, now, ticket_id))

    # Append history entry
    cursor.execute("""
        INSERT INTO ticket_history (ticket_id, old_status, new_status, changed_at, note)
        VALUES (?, ?, ?, ?, ?)
    """, (ticket_id, old_status, new_status, now, note))

    conn.commit()
    conn.close()
    return True, f"Status updated: {old_status} -> {new_status}"


def get_ticket(ticket_id):
    """Fetch a single ticket by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_tickets(status_filter=None):
    """Fetch all tickets, optionally filtered by status"""
    conn = get_connection()
    cursor = conn.cursor()
    if status_filter:
        cursor.execute(
            "SELECT * FROM tickets WHERE status = ? ORDER BY priority, created_at",
            (status_filter,)
        )
    else:
        cursor.execute("SELECT * FROM tickets ORDER BY priority, created_at")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_ticket_history(ticket_id):
    """Fetch the full status change history for a given ticket"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM ticket_history WHERE ticket_id = ? ORDER BY changed_at
    """, (ticket_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
