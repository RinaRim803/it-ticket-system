"""
server.py
IT Ticket System — Flask server entry point

Usage:
    python server.py

The server listens on http://localhost:5000
Other tools (sys-health-check, network-troubleshooter) send HTTP POST
requests to /api/tickets to create tickets automatically.
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    print("\n  IT Ticket System — API Server")
    print("  Running on http://localhost:5000")
    print("  Press Ctrl+C to stop\n")
    app.run(host="0.0.0.0", port=5000, debug=False)