"""
FinBrief Web Application Server.
Serves the FinBrief UI and provides API endpoints for news reports.
"""

import json
import logging
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("web_app")

PROJECT_ROOT = Path(__file__).parent.resolve()
REPORTS_DIR = PROJECT_ROOT / "reports"
WEB_DIR = PROJECT_ROOT / "web"


class FinBriefHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)

        if path == "/api/report":
            self.handle_api_report(query)
        elif path == "/api/dates":
            self.handle_api_dates()
        else:
            # Serve index.html for root or static files
            if path == "/" or path == "/index.html":
                file_path = WEB_DIR / "index.html"
            else:
                file_path = WEB_DIR / path.lstrip("/")

            if file_path.exists() and file_path.is_file():
                self.send_response(200)
                if file_path.suffix == ".html":
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                elif file_path.suffix == ".css":
                    self.send_header("Content-Type", "text/css")
                elif file_path.suffix == ".js":
                    self.send_header("Content-Type", "application/javascript")
                elif file_path.suffix == ".json":
                    self.send_header("Content-Type", "application/json")
                self.end_headers()
                with open(file_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "File Not Found")

    def handle_api_report(self, query):
        date_param = query.get("date", [None])[0]
        source_param = query.get("source", [None])[0]

        # Check Neon PostgreSQL DB first if configured
        from db import db
        if db.is_active():
            report_data = db.get_report(edition_date=date_param, source=source_param)
            if report_data:
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(report_data, ensure_ascii=False).encode("utf-8"))
                return

        # Fallback to local files
        report_file = None
        if date_param:
            for candidate in [
                REPORTS_DIR / f"news_report_unified_{date_param}.json",
                REPORTS_DIR / f"news_report_{date_param}.json",
                REPORTS_DIR / f"news_report_bs_{date_param}.json",
            ]:
                if candidate.exists():
                    report_file = candidate
                    break

        if not report_file:
            # Check unified latest first
            unified_latest = REPORTS_DIR / "news_report_unified_latest.json"
            if unified_latest.exists():
                report_file = unified_latest
            else:
                json_files = sorted(REPORTS_DIR.glob("*.json"), key=os.path.getmtime, reverse=True)
                if json_files:
                    report_file = json_files[0]

        if report_file and report_file.exists():
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            with open(report_file, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404, "No reports available.")

    def handle_api_dates(self):
        dates = []
        from db import db
        if db.is_active():
            try:
                conn = db.get_connection()
                with conn.cursor() as cur:
                    cur.execute("SELECT DISTINCT edition_date FROM editions ORDER BY edition_date DESC;")
                    rows = cur.fetchall()
                    dates = [str(r[0]) for r in rows]
                conn.close()
            except Exception as e:
                logger.error(f"Error querying dates from DB: {e}")

        if not dates:
            json_files = sorted(REPORTS_DIR.glob("news_report_*.json"), key=os.path.getmtime, reverse=True)
            dates = [f.stem.replace("news_report_", "") for f in json_files]

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(dates).encode("utf-8"))


def run_server(port=8000):
    server_address = ("", port)
    httpd = HTTPServer(server_address, FinBriefHandler)
    logger.info(f"🚀 FinBrief Web App server running on http://localhost:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped.")


if __name__ == "__main__":
    run_server()
