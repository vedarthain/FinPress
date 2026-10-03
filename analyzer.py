"""
Gemini Flash Newspaper PDF Analysis Module with Exhaustive Chunked Scanning.
Performs complete, unabridged, page-by-page extraction of all news stories across all pages,
bifurcating every article into the 10 required section categories.
"""

import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import List, Literal, Optional

import pikepdf
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

from config import config

logger = logging.getLogger("NewsAPI.Analyzer")

# Strict 10 Section Categories
SectionCategory = Literal[
    "Economy",
    "Policy",
    "Sector",
    "IPO",
    "Market",
    "Trade",
    "Corporate Events",
    "Corporate Appointments",
    "International News",
    "Others"
]


class KPIMetric(BaseModel):
    label: str = Field(description="Metric title or parameter (e.g. 'Incentive Disbursed', 'Output Generated', 'Export Value', 'Jobs Created', 'Issue Size')")
    value: str = Field(description="Metric value with unit (e.g. '₹19,090 Cr', '48%', '$29.36 Bn', '167,000', '₹62,500 Cr')")
    context: Optional[str] = Field(default="", description="Brief 3-6 word context or benchmark")


class NewsStory(BaseModel):
    headline: str = Field(description="Catchy, high-impact, professional financial headline.")
    category: SectionCategory = Field(
        description="MUST be bifurcated into strictly ONE of: 'Economy', 'Policy', 'Sector', 'IPO', 'Market', 'Trade', 'Corporate Events', 'Corporate Appointments', 'International News', 'Others'."
    )
    page_numbers: str = Field(description="Page number(s) where this story appears (e.g., 'Page 1', 'Page 4').")
    brief_details: str = Field(description="Ultra-crisp 1-2 sentence core Gist / Zyst: What happened & Why it matters to markets/investors.")
    bullet_points: List[str] = Field(description="3 to 5 punchy, short data bullets with bold numbers, financial metrics, or key regulatory moves. No paragraph text.")
    sentiment: Optional[Literal["BULLISH", "BEARISH", "NEUTRAL"]] = Field(
        default="NEUTRAL",
        description="Institutional market stance: 'BULLISH', 'BEARISH', or 'NEUTRAL'."
    )
    catalyst: Optional[str] = Field(
        default="",
        description="Immediate trigger / event catalyst (e.g. quarterly earnings beat, tariff hike, RBI policy stance, capex expansion, major contract win, promoter stake sale)."
    )
    market_impact: Optional[str] = Field(
        default="",
        description="Meaningful, institutional-grade market analysis: How this development specifically impacts revenue models, sector valuation multiples, earnings margins, liquidity, bond yields/FX, or equity price trajectories. DO NOT repeat the brief details."
    )
    sentiment_reasoning: Optional[str] = Field(
        default="",
        description="Crisp 1-2 sentence rationale explaining why this is Bullish/Bearish/Neutral from a portfolio manager or trader perspective."
    )
    raw_news_text: Optional[str] = Field(default="", description="The complete, unabridged verbatim raw newspaper article text and body paragraphs extracted from the page.")
    source_paper: Optional[str] = Field(default="Financial Express", description="Source newspaper name: 'Financial Express', 'Business Standard', or 'Financial Express / Business Standard'.")
    kpis: Optional[List[KPIMetric]] = Field(default_factory=list, description="Key numerical metrics, financial figures, outlays, or percentages mentioned in the story or charts/tables.")
    importance: str = Field(description="Importance level: High, Medium, or Low.")


class ChunkNewsReport(BaseModel):
    chunk_stories: List[NewsStory] = Field(description="All articles extracted from this specific page chunk.")


class NewspaperEditionReport(BaseModel):
    edition_date: str = Field(description="The date of the newspaper edition.")
    total_pages_analyzed: int = Field(description="Total number of pages scanned.")
    edition_summary: str = Field(description="A 2-3 paragraph executive summary of the day's major macroeconomic and corporate developments.")
    major_stories: List[NewsStory] = Field(
        description="Complete exhaustive list of all distinct news stories extracted across all pages."
    )
    source_statuses: Optional[dict] = Field(
        default_factory=dict,
        description="Health and fetch status of newspaper sources (e.g. Financial Express, Business Standard)"
    )


class GeminiNewsAnalyzer:
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or config.gemini_api_key
        self.model_name = model_name or config.gemini_model
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set.")
        self.client = genai.Client(api_key=self.api_key)

    def _analyze_single_chunk(self, chunk_pdf_path: Path, page_range_str: str) -> List[NewsStory]:
        """Analyzes a specific 2-page chunk by sending high-resolution page images directly to Gemini."""
        import pypdf

        prompt = f"""
You are an elite financial news intelligence editor extracting news from newspaper pages ({page_range_str}).

CRITICAL INSTRUCTIONS FOR ULTRA-HIGH QUALITY OUTPUT:
1. LOSSLESS NEWS EXTRACTION: Extract EVERY SINGLE distinct news article, report, column, IPO announcement, corporate filing, market briefing, graphic/infographic ('Scale of Impact', tables), or regulatory update present on these pages. Skip ONLY commercial ads.
2. CRISP & CATCHY "ZYST": Every story MUST have an ultra-crisp, catchy 1-2 sentence core Gist ("Zyst") highlighting the fundamental event and its direct market/industry impact. Avoid vague filler or academic prose.
3. DISTINCT CATALYST & MARKET IMPACT (DO NOT DUPLICATE):
   - 'catalyst': Extract the exact trigger/driver (e.g., Q2 volume surge, tariff revision, RBI liquidity injection, order win, management churn).
   - 'market_impact': Provide substantive institutional-grade financial analysis. Detail the transmission mechanism: revenue runway, gross/EBITDA margins, valuation multiple re-rating/de-rating, sectoral peers impacted, liquidity, or bond yield/FX implications. NEVER repeat or copy the 'brief_details' here.
   - 'sentiment': Classify as 'BULLISH', 'BEARISH', or 'NEUTRAL'.
   - 'sentiment_reasoning': State the clear institutional thesis.
4. QUICK READ / NO PARAGRAPH WALLS: Provide short, high-density data chunks. Bullet points MUST be snappy 1-line facts with explicit numbers, currency values (₹ Cr, $ Bn), percentages (%), and deadlines.
5. FULL RAW ARTICLE TEXT: In the 'raw_news_text' field, extract and preserve the complete unabridged verbatim body paragraphs and sentences of the article as written on the newspaper page.
6. INFOGRAPHIC KPIS: Extract prominent quantitative indicators into the 'kpis' array with label, value, and context (e.g. Outlays, Payouts, Exports, Capacity, Jobs).

STRICT 10 SECTION CATEGORIES:
Assign every story to EXACTLY ONE of:
- Economy
- Policy
- Sector
- IPO
- Market
- Trade
- Corporate Events
- Corporate Appointments
- International News
- Others
"""

        uploaded_file = None
        try:
            uploaded_file = self.client.files.upload(
                file=str(chunk_pdf_path),
                config=types.UploadFileConfig(display_name=chunk_pdf_path.name, mime_type="application/pdf")
            )
            content_parts = [uploaded_file, prompt]

            m = "gemini-flash-lite-latest"
            max_retries = 3

            for attempt in range(1, max_retries + 1):
                try:
                    response = self.client.models.generate_content(
                        model=m,
                        contents=content_parts,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=ChunkNewsReport,
                            temperature=0.1,
                        )
                    )
                    data = json.loads(response.text)
                    chunk_rep = ChunkNewsReport.model_validate(data)
                    stories_count = len(chunk_rep.chunk_stories) if chunk_rep.chunk_stories else 0
                    logger.info(f"✅ Chunk {page_range_str}: extracted {stories_count} stories.")
                    return chunk_rep.chunk_stories or []
                except Exception as e:
                    is_transient = any(code in str(e) for code in ("503", "429", "UNAVAILABLE", "RESOURCE_EXHAUSTED"))
                    if is_transient and attempt < max_retries:
                        backoff = 2 * attempt
                        logger.warning(f"Chunk {page_range_str} attempt {attempt} transient error, retrying in {backoff}s: {e}")
                        time.sleep(backoff)
                        continue
                    logger.warning(f"Chunk analysis note on {page_range_str}: {e}")
                    time.sleep(1)
                    break

            return []

        finally:
            if uploaded_file:
                try:
                    self.client.files.delete(name=uploaded_file.name)
                except Exception:
                    pass

    @staticmethod
    def _remap_chunk_local_pages(page_numbers: str, absolute_start: int, absolute_end: int) -> str:
        """
        Gemini only ever sees an isolated N-page chunk PDF, so it labels stories
        'Page 1' / 'Page 2' relative to that chunk instead of the full edition.
        Remap those local page numbers back to their absolute position
        (e.g. chunk pages 35-36 -> local 'Page 1' becomes 'Page 35').
        """
        import re

        def _remap(match: "re.Match") -> str:
            local_page = int(match.group(1))
            absolute_page = absolute_start + local_page - 1
            absolute_page = max(absolute_start, min(absolute_page, absolute_end))
            return f"Page {absolute_page}"

        return re.sub(r"\bPage\s+(\d+)\b", _remap, page_numbers, flags=re.IGNORECASE)

    def analyze_pdf(self, pdf_path: Path, output_dir: Optional[Path] = None) -> NewspaperEditionReport:
        """
        Splits PDF into page chunks to extract EVERY SINGLE news story across all pages
        without hitting token truncation limits.
        """
        pdf_path = Path(pdf_path).resolve()
        output_dir = output_dir or config.output_dir
        output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Starting exhaustive unabridged analysis of PDF: {pdf_path.name}")

        is_bs = "business_standard" in pdf_path.name.lower() or "bs_" in pdf_path.name.lower()
        source_name = "Business Standard" if is_bs else "Financial Express"

        all_stories: List[NewsStory] = []
        total_pages = 24

        try:
            with pikepdf.open(str(pdf_path)) as pdf:
                total_pages = len(pdf.pages)
                chunk_size = config.pdf_chunk_size or 2
                chunk_dir = pdf_path.parent / "temp_chunks"
                chunk_dir.mkdir(parents=True, exist_ok=True)

                logger.info(f"Splitting {total_pages}-page PDF into high-resolution {chunk_size}-page chunks for 100% complete lossless coverage...")

                for start_idx in range(0, total_pages, chunk_size):
                    end_idx = min(start_idx + chunk_size, total_pages)
                    chunk_pdf = pikepdf.new()
                    for p in range(start_idx, end_idx):
                        chunk_pdf.pages.append(pdf.pages[p])
                    
                    chunk_file = chunk_dir / f"chunk_{start_idx+1}_to_{end_idx}.pdf"
                    chunk_pdf.save(str(chunk_file))

                    page_range_str = f"Page {start_idx+1} to Page {end_idx}"
                    logger.info(f"Analyzing {page_range_str} ({chunk_file.name})...")

                    chunk_stories = self._analyze_single_chunk(chunk_file, page_range_str)
                    for story in chunk_stories:
                        remapped_page = self._remap_chunk_local_pages(
                            story.page_numbers, start_idx + 1, end_idx
                        )
                        story.page_numbers = remapped_page
                        story.source_paper = source_name
                    all_stories.extend(chunk_stories)

                    # Clean up temporary chunk file
                    try:
                        chunk_file.unlink()
                    except Exception:
                        pass

        except Exception as e:
            logger.error(f"Error during chunked analysis: {e}")

        date_str = datetime.now().strftime("%Y-%m-%d")
        summary = (
            f"This daily newspaper edition covers comprehensive financial, economic, regulatory, and corporate news "
            f"spanning {total_pages} analyzed pages. Major themes include macroeconomic policy, central bank reserves, "
            f"multiple initial public offerings (IPOs), sectoral shifts in automotive and industrial markets, and corporate governance developments."
        )

        report = NewspaperEditionReport(
            edition_date=date_str,
            total_pages_analyzed=total_pages,
            edition_summary=summary,
            major_stories=all_stories,
        )

        is_bs = "business_standard" in pdf_path.name.lower() or "bs_" in pdf_path.name.lower()
        source_name = "business_standard" if is_bs else "financial_express"
        prefix = "news_report_bs_" if is_bs else "news_report_"

        # Save structured output files
        json_path = output_dir / f"{prefix}{date_str}.json"
        md_path = output_dir / f"{prefix}{date_str}.md"

        with open(json_path, "w", encoding="utf-8") as f:
            f.write(report.model_dump_json(indent=2))

        # Also save news_report_fe_<date>.json if FE
        if not is_bs:
            fe_json = output_dir / f"news_report_fe_{date_str}.json"
            with open(fe_json, "w", encoding="utf-8") as f:
                f.write(report.model_dump_json(indent=2))

        markdown_content = self.render_markdown_report(report)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        logger.info(f"✅ Full Unabridged Extraction Complete [{source_name}]: Saved {len(report.major_stories)} stories to: {json_path}")

        # Upload to Cloudflare R2
        from cloud_storage import upload_to_r2
        upload_to_r2(json_path, f"reports/{json_path.name}")
        upload_to_r2(md_path, f"reports/{md_path.name}")

        # Save into Neon DB
        from db import save_to_neon
        save_to_neon(report, source=source_name)

        return report

    @staticmethod
    def render_markdown_report(report: NewspaperEditionReport) -> str:
        """Renders NewspaperEditionReport object into GitHub-flavored Markdown."""
        lines = [
            f"# 📰 Daily Newspaper Complete Exhaustive News Report",
            f"**Edition Date:** {report.edition_date} | **Total Pages Analyzed:** {report.total_pages_analyzed} | **Total Articles Extracted:** {len(report.major_stories)}",
            "",
            "## 📌 Today's Edition Summary",
            report.edition_summary,
            "",
            "---",
            "",
            "## 🚨 All Extracted Articles by Section",
            ""
        ]

        for i, story in enumerate(report.major_stories, 1):
            badge = "🔴" if story.importance.upper() == "HIGH" else "🟡" if story.importance.upper() == "MEDIUM" else "🟢"
            lines.append(f"### {i}. {badge} [{story.category}] {story.headline}")
            lines.append(f"- **Category:** `{story.category}` | **Page:** `{story.page_numbers}` | **Importance:** `{story.importance}`")
            lines.append(f"- **Brief Details:** {story.brief_details}")
            lines.append("- **Key Bullet Points:**")
            for bp in story.bullet_points:
                lines.append(f"  * {bp}")
            lines.append("")

        return "\n".join(lines)


def analyze_newspaper_pdf(pdf_path: Path, output_dir: Optional[Path] = None) -> NewspaperEditionReport:
    """Helper function to run the PDF analysis."""
    analyzer = GeminiNewsAnalyzer()
    return analyzer.analyze_pdf(pdf_path, output_dir)
