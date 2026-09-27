"""
Vercel Serverless Function: /api/dates
Fetches all available edition dates from Neon PostgreSQL DB.
"""

import json
import logging
import os
from http.server import BaseHTTPRequestHandler

logger = logging.getLogger("api.dates")


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        dates = []
        database_url = os.getenv("DATABASE_URL")

        if database_url:
            try:
                import psycopg2

                conn = psycopg2.connect(database_url, sslmode="require")
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT DISTINCT edition_date FROM editions ORDER BY edition_date DESC;"
                    )
                    rows = cur.fetchall()
                    dates = [str(r[0]) for r in rows]
                conn.close()
            except Exception as e:
                logger.error(f"Neon DB dates query error: {e}")

        if not dates:
            # Fallback to current date
            from datetime import datetime

            dates = [datetime.now().strftime("%Y-%m-%d")]

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "public, s-maxage=300")
        self.end_headers()
        self.wfile.write(json.dumps(dates).encode("utf-8"))
