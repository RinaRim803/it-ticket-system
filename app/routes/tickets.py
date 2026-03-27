"""
app/routes/tickets.py
Ticket API endpoints

POST   /api/tickets               Create a new ticket (used by integrations)
GET    /api/tickets               List all tickets (optional ?status= filter)
GET    /api/tickets/<id>          Get a single ticket + history
PATCH  /api/tickets/<id>/status   Update ticket status
"""

from flask import Blueprint, request, jsonify
from app.services.database import insert_ticket, get_ticket, get_all_tickets, get_ticket_history, update_status
from app.services.classifier import analyze_ticket

tickets_bp = Blueprint("tickets", __name__)


@tickets_bp.route("/tickets", methods=["POST"])
def create_ticket():
    """
    Create a new ticket.
    Auto-classifies and assigns priority from title + description.

    Request body (JSON):
        {
            "title":       "High CPU usage detected",       # required
            "description": "CPU at 94% for 5 minutes",     # required
            "source":      "sys-health-check"               # optional — which tool sent this
        }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    source = data.get("source", "manual")

    if not title or not description:
        return jsonify({"error": "title and description are required"}), 400

    # Auto-classify and assign priority
    result = analyze_ticket(title, description)
    category = result["category"]
    priority = result["priority"]

    # Append source tag to description for traceability
    if source != "manual":
        description = f"[Source: {source}]\n\n{description}"

    ticket_id = insert_ticket(title, description, category, priority)

    return jsonify({
        "id":       ticket_id,
        "title":    title,
        "category": category,
        "priority": priority,
        "status":   "Open",
        "source":   source,
    }), 201


@tickets_bp.route("/tickets", methods=["GET"])
def list_tickets():
    """
    List all tickets.
    Optional query param: ?status=Open|In Progress|Resolved
    """
    status_filter = request.args.get("status")
    tickets = get_all_tickets(status_filter)
    return jsonify({"tickets": tickets, "total": len(tickets)}), 200


@tickets_bp.route("/tickets/<int:ticket_id>", methods=["GET"])
def get_ticket_detail(ticket_id):
    """Get a single ticket with its full status history"""
    ticket = get_ticket(ticket_id)
    if not ticket:
        return jsonify({"error": f"Ticket #{ticket_id} not found"}), 404

    history = get_ticket_history(ticket_id)
    return jsonify({"ticket": ticket, "history": history}), 200


@tickets_bp.route("/tickets/<int:ticket_id>/status", methods=["PATCH"])
def update_ticket_status(ticket_id):
    """
    Update ticket status.

    Request body (JSON):
        {
            "status": "In Progress",
            "note":   "Investigating the issue"   # optional
        }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    new_status = data.get("status", "").strip()
    note = data.get("note", "").strip() or None

    valid_statuses = ["Open", "In Progress", "Resolved"]
    if new_status not in valid_statuses:
        return jsonify({"error": f"Invalid status. Must be one of: {valid_statuses}"}), 400

    ok, msg = update_status(ticket_id, new_status, note)
    if not ok:
        return jsonify({"error": msg}), 404

    return jsonify({"message": msg}), 200