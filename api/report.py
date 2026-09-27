"""
Vercel Serverless Function: /api/report
Fetches unified news reports from Neon PostgreSQL DB or Cloudflare R2 fallback.
"""

import json
import logging
import os
import urllib.request
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

logger = logging.getLogger("api.report")


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        date_param = query.get("date", [None])[0]
        source_param = query.get("source", [None])[0]

        report_data = None

        # 1. Try Neon PostgreSQL DB first
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            try:
                import psycopg2
                from psycopg2.extras import RealDictCursor

                conn = psycopg2.connect(database_url, sslmode="require")
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    if date_param and source_param:
                        cur.execute(
                            "SELECT * FROM editions WHERE edition_date = %s AND source = %s LIMIT 1;",
                            (date_param, source_param),
                        )
                    elif date_param:
                        cur.execute(
                            "SELECT * FROM editions WHERE edition_date = %s ORDER BY created_at DESC LIMIT 1;",
                            (date_param,),
                        )
                    else:
                        cur.execute(
                            "SELECT * FROM editions ORDER BY edition_date DESC, created_at DESC LIMIT 1;"
                        )

                    edition = cur.fetchone()
                    if edition:
                        cur.execute(
                            "SELECT * FROM articles WHERE edition_id = %s ORDER BY id ASC;",
                            (edition["id"],),
                        )
                        articles = cur.fetchall()

                        formatted_stories = []
                        for a in articles:
                            bullet_pts = a["bullet_points"]
                            if isinstance(bullet_pts, str):
                                bullet_pts = json.loads(bullet_pts)

                            formatted_stories.append({
                                "category": a["category"],
                                "headline": a["headline"],
                                "brief_details": a["brief_details"],
                                "bullet_points": bullet_pts,
                                "page_numbers": a["page_numbers"],
                                "importance": a["importance"],
                            })

                        report_data = {
                            "edition_date": str(edition["edition_date"]),
                            "source": edition["source"],
                            "total_pages_analyzed": edition["total_pages"],
                            "edition_summary": edition["summary"],
                            "pdf_url": edition["pdf_url"],
                            "major_stories": formatted_stories,
                        }
                conn.close()
            except Exception as e:
                logger.error(f"Neon DB query error: {e}")

        # 2. Fallback to Cloudflare R2
        if not report_data:
            r2_base = os.getenv(
                "CLOUDFLARE_R2_PUBLIC_URL",
                "https://pub-c81167dd545d49d0a2cd964a8bd6a1cd.r2.dev",
            )
            target_file = (
                f"news_report_unified_{date_param}.json"
                if date_param
                else "news_report_unified_latest.json"
            )
            r2_url = f"{r2_base.rstrip('/')}/reports/{target_file}"
            try:
                req = urllib.request.Request(
                    r2_url, headers={"User-Agent": "FinBrief-Vercel-Client"}
                )
                with urllib.request.urlopen(req, timeout=5) as resp:
                    if resp.status == 200:
                        report_data = json.loads(resp.read().decode("utf-8"))
            except Exception as e:
                logger.error(f"R2 fallback error: {e}")

        # Response
        if report_data:
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "public, s-maxage=300, stale-while-revalidate=600")
            self.end_headers()
            self.wfile.write(json.dumps(report_data).encode("utf-8"))
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Report not found"}).encode("utf-8"))
