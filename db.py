"""
Neon PostgreSQL Database Integration for NewsAPI / FinBrief.
Handles saving news editions, articles, and querying for Vercel Web App.
"""

import json
import logging
import os
from pathlib import Path
from typing import Optional, List, Dict, Any

import psycopg2
from psycopg2.extras import RealDictCursor

from config import config

logger = logging.getLogger("NewsAPI.DB")


class NeonDatabase:
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.getenv("DATABASE_URL", "")

    def get_connection(self):
        if not self.database_url:
            return None
        return psycopg2.connect(self.database_url, sslmode="require")

    def is_active(self) -> bool:
        return bool(self.database_url)

    def init_db(self):
        """Initializes tables in Neon PostgreSQL database."""
        if not self.is_active():
            logger.info("DATABASE_URL not set in .env. Skipping database init.")
            return

        schema_path = Path(__file__).parent / "schema.sql"
        if not schema_path.exists():
            logger.warning("schema.sql file not found.")
            return

        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute(schema_path.read_text(encoding="utf-8"))
            conn.commit()
            conn.close()
            logger.info("✅ Neon PostgreSQL database tables initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing Neon database: {e}")

    def save_report(self, report, source: str = "financial_express", pdf_url: Optional[str] = None) -> bool:
        """
        Saves a NewspaperEditionReport into Neon PostgreSQL database.
        Upserts the edition and inserts all bifurcated articles.
        """
        if not self.is_active():
            logger.warning("DATABASE_URL not configured. Skipping Neon DB save.")
            return False

        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                # Upsert edition
                cur.execute(
                    """
                    INSERT INTO editions (edition_date, source, total_pages, total_stories, summary, pdf_url)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (edition_date, source) 
                    DO UPDATE SET 
                        total_pages = EXCLUDED.total_pages,
                        total_stories = EXCLUDED.total_stories,
                        summary = EXCLUDED.summary,
                        pdf_url = COALESCE(EXCLUDED.pdf_url, editions.pdf_url)
                    RETURNING id;
                    """,
                    (
                        report.edition_date,
                        source,
                        report.total_pages_analyzed,
                        len(report.major_stories),
                        report.edition_summary,
                        pdf_url,
                    ),
                )
                edition_id = cur.fetchone()[0]

                # Delete old articles for re-run / refresh
                cur.execute("DELETE FROM articles WHERE edition_id = %s;", (edition_id,))

                # Insert all extracted stories
                for story in report.major_stories:
                    cur.execute(
                        """
                        INSERT INTO articles 
                        (edition_id, edition_date, source, category, headline, brief_details, bullet_points, page_numbers, importance)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                        """,
                        (
                            edition_id,
                            report.edition_date,
                            source,
                            story.category,
                            story.headline,
                            story.brief_details,
                            json.dumps(story.bullet_points),
                            story.page_numbers,
                            story.importance,
                        ),
                    )

            conn.commit()
            conn.close()
            logger.info(f"✅ Saved {len(report.major_stories)} stories into Neon PostgreSQL database (Edition ID: {edition_id}).")
            return True

        except Exception as e:
            logger.error(f"Failed to save report to Neon DB: {e}")
            return False

    def get_report(self, edition_date: Optional[str] = None, source: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Queries the latest or target date report from Neon DB for Vercel Web App."""
        if not self.is_active():
            return None

        try:
            conn = self.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Find target edition
                if edition_date and source:
                    cur.execute("SELECT * FROM editions WHERE edition_date = %s AND source = %s LIMIT 1;", (edition_date, source))
                elif edition_date:
                    cur.execute("SELECT * FROM editions WHERE edition_date = %s ORDER BY created_at DESC LIMIT 1;", (edition_date,))
                else:
                    cur.execute("SELECT * FROM editions ORDER BY edition_date DESC, created_at DESC LIMIT 1;")
                
                edition = cur.fetchone()
                if not edition:
                    conn.close()
                    return None

                # Fetch articles
                cur.execute("SELECT * FROM articles WHERE edition_id = %s ORDER BY id ASC;", (edition["id"],))
                articles = cur.fetchall()

            conn.close()

            # Format to JSON schema match
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

            return {
                "edition_date": str(edition["edition_date"]),
                "source": edition["source"],
                "total_pages_analyzed": edition["total_pages"],
                "edition_summary": edition["summary"],
                "pdf_url": edition["pdf_url"],
                "major_stories": formatted_stories,
            }

        except Exception as e:
            logger.error(f"Error reading from Neon DB: {e}")
            return None


db = NeonDatabase()

def init_neon_db():
    db.init_db()

def save_to_neon(report, source="financial_express", pdf_url=None):
    return db.save_report(report, source=source, pdf_url=pdf_url)
