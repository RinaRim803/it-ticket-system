"""
server.py
IT Ticket System — Flask server entry point

Usage:
    python server.py

Host, port, and debug mode are controlled via config.json.
Other tools (sys-health-check, network-troubleshooter) send HTTP POST
requests to /api/tickets to create tickets automatically.
"""

from app import create_app
from app.services.config import get_server_config

app = create_app()

if __name__ == "__main__":
    cfg = get_server_config()
    print("\n  IT Ticket System — API Server")
    print(f"  Running on http://{cfg['host']}:{cfg['port']}")
    print("  Press Ctrl+C to stop\n")
    app.run(host=cfg["host"], port=cfg["port"], debug=cfg["debug"])