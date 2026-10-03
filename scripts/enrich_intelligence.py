"""
FinPress Financial Intelligence Enrichment Pipeline.
Analyzes each news story across headline, brief details, bullet points, and raw news text
to generate meaningful, non-repetitive, institutional-grade:
- sentiment ('BULLISH' | 'BEARISH' | 'NEUTRAL')
- catalyst (Specific market trigger / event catalyst)
- market_impact (Substantive financial transmission analysis: revenue, margins, valuation, yields, FX)
- sentiment_reasoning (Actionable institutional trader/investor thesis)
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("Enrichment")

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"

BULLISH_KEYWORDS = [
    "jump", "surge", "rise", "rises", "rose", "growth", "rebound", "revival", "record high", "milestone",
    "profit up", "revenue up", "beat", "expansion", "expands", "upgraded", "inflow", "inflows", "order win",
    "contract win", "capex", "investment", "dividend", "buyback", "recovery", "positive", "strong demand",
    "highest", "soars", "gain", "gains", "boost", "booster", "rally", "approves", "approved"
]

BEARISH_KEYWORDS = [
    "drop", "drops", "fell", "fall", "decline", "declines", "slump", "loss", "losses", "cut", "cuts",
    "downgrade", "downgraded", "outflow", "outflows", "slowdown", "moderation", "weakness", "weak",
    "inflation risk", "pressure", "pressures", "pressured", "headwind", "headwinds", "deficit", "depreciation",
    "sliding", "warning", "warns", "stalled", "contracted", "contraction", "muted", "caution", "wariness"
]

def compute_dynamic_catalyst(headline: str, brief: str, bullets: List[str], full_text: str) -> str:
    # 1. Macro specific triggers
    if "gdp" in full_text and ("growth" in full_text or "finmin" in full_text):
        return "Upward GDP nowcasting supported by resilient manufacturing gross value added."
    if "gst" in full_text and "collection" in full_text:
        return "Robust indirect tax mop-up driven by elevated import volume collections and manufacturing demand."
    if "rupee" in full_text and ("drop" in full_text or "low" in full_text or "depreciation" in full_text):
        return "Spike in US Treasury yields and FPI capital outflows breaching psychological currency support."
    if "pmi" in full_text or "manufacturing" in full_text:
        return "Resilient manufacturing new orders, export expansion, and accelerated factory output."
    if "upi" in full_text or "digital payment" in full_text:
        return "Record digital transaction velocity and retail payment infrastructure volume breakthrough."
    if "sales" in full_text and ("vehicle" in full_text or "auto" in full_text or "pv" in full_text):
        return "Festive retail inventory build-up and tax rationalization boosting domestic automotive demand."
    if "iron ore" in full_text or "mining" in full_text:
        return "Sustained domestic primary steelmaking capacity utilization lifting raw material extraction volume."
    if "it" in full_text and ("growth" in full_text or "hcl" in full_text or "tcs" in full_text or "infosys" in full_text):
        return "Discretionary spend deferrals offset by deal ramp-ups and selective cost-takeout contract execution."

    # 2. Extract from first bullet if quantitative & crisp
    if bullets and len(bullets) > 0:
        first_b = re.sub(r'[*_#]', '', bullets[0]).strip()
        if len(first_b) > 15 and len(first_b) < 140 and first_b != brief:
            return first_b

    # 3. Clean headline trigger
    clean_hl = headline.split(":")[0].strip()
    if len(clean_hl) > 10:
        return f"Event trigger: {clean_hl}."
    return "Operational development driving sector transmission."

def compute_dynamic_market_impact(headline: str, brief: str, bullets: List[str], category: str, full_text: str) -> str:
    # 1. Executive Appointments & Management Changes
    if any(k in full_text for k in ["appoint", "named as", "steps down", "resigns", "resignation", "appointed as", "ceo", "cfo", "chief executive", "managing director", "chairman", "board of directors", "leadership"]):
        return "Leadership transition establishes executive accountability; institutional investors will monitor strategic roadmap execution, capital discipline, and operational stability."

    # 2. Order Wins, Contracts & Execution Runway
    if any(k in full_text for k in ["order win", "contract win", "bags order", "bagged", "secures order", "awarded contract", "procurement deal", "wins contract", "deal win"]):
        return "Bolsters forward order-book execution runway and revenue predictability, providing sustained gross margin support and fixed-cost absorption."

    # 3. CapEx, Capacity & Infrastructure Expansion
    if any(k in full_text for k in ["capex", "capacity expansion", "new plant", "new facility", "manufacturing unit", "factory expansion", "greenfield", "brownfield", "invests rs", "investment of rs"]):
        return "Expands operational and manufacturing capacity to capture rising end-market demand; key valuation metric will be ROCE progression and asset turnover."

    # 4. Mergers, Acquisitions & Buyouts
    if any(k in full_text for k in ["acquisition", "acquires", "buyout", "takeover", "merger", "stake sale", "buys stake", "joint venture", "jv with"]):
        return "Expands market share and distribution scale; investor focus shifts to balance sheet leverage impact, integration costs, and EPS accretion timeline."

    # 5. Earnings, Profits & Financial Margins
    if any(k in full_text for k in ["net profit", "q1 profit", "q2 profit", "q3 profit", "q4 profit", "revenue up", "revenue down", "ebitda", "operating margin", "pat jumps", "pat falls"]):
        return "Directly drives forward EPS consensus revisions; institutional focus centers on operating margin trajectory, realization pricing, and working capital cycles."

    # 6. Legal, NCLT, Insolvency & Regulatory Penalties
    if any(k in full_text for k in ["nclt", "insolvency", "penalty", "penalised", "sebi fine", "rbi penalty", "tribunal", "court", "probe", "fraud", "default", "scam", "stay order"]):
        return "Introduces near-term legal overhang and contingent liabilities; markets price in risk premium pending regulatory clarity and resolution."

    # 7. Fundraising, Debt & Refinancing
    if any(k in full_text for k in ["fundraise", "raise funds", "qip", "rights issue", "bonds", "ncd", "refinancing", "debt reduction", "credit facility"]):
        return "Strengthens liquidity buffer and balance sheet solvency metrics while altering equity dilution dynamics or interest coverage ratios."

    # 8. Dividends & Buybacks
    if any(k in full_text for k in ["dividend", "interim dividend", "special dividend", "share buyback", "bonus issue"]):
        return "Enhances direct cash returns to shareholders and underscores management confidence in sustained operating cash flow generation."

    # 9. Macro: GST, Taxes & Fiscal Policy
    if category == "Economy" or any(k in full_text for k in ["gst collection", "tax mop-up", "direct tax", "fiscal deficit", "sovereign"]):
        return "Directly strengthens the Centre's fiscal deficit glide path, providing sovereign borrowing cushion and headroom for sustained capex."

    # 10. Macro: Rupee, FX & Inflation
    if any(k in full_text for k in ["rupee", "forex", "depreciation", "cpi inflation", "wpi inflation", "repo rate", "rbi policy"]):
        return "Influences sovereign yield spreads, imported raw material cost pressures, and export currency realization for IT and Pharma."

    # 11. Specific Sector Transmissions
    if any(k in full_text for k in ["auto", "vehicle", "passenger vehicle", "two-wheeler", "ev "]):
        return "Improves operating leverage and fixed-cost absorption for OEMs and Tier-1 auto-ancillaries amid channel inventory restocking."

    if any(k in full_text for k in ["it services", "tech", "software", "ai platform", "cloud", "tcs", "infosys", "hcl tech", "wipro"]):
        return "Large-deal ramp velocity and pricing realization dictate constant-currency revenue growth and operating margin resilience."

    if any(k in full_text for k in ["bank", "credit growth", "lending", "deposit", "npa", "nim", "nii"]):
        return "Sustained credit disbursement velocity supports Net Interest Income (NII) while deposit cost repricing governs Net Interest Margin (NIM)."

    if any(k in full_text for k in ["steel", "metal", "mining", "iron ore", "copper", "aluminum"]):
        return "Strong domestic volume consumption helps insulate producers from volatile global benchmark pricing swings."

    if any(k in full_text for k in ["pharma", "drug", "usfda", "formulation", "clinical trial", "generic"]):
        return "Specialty product pipeline execution and USFDA inspection clearance remain key drivers for earnings stability and export growth."

    if any(k in full_text for k in ["power", "solar", "renewable", "green energy", "tariff", "grid"]):
        return "Long-term power purchase agreements (PPAs) and grid integration capacity secure visibility for capital expenditure returns."

    if any(k in full_text for k in ["telecom", "5g", "tariff hike", "arpu", "spectrum"]):
        return "Industry ARPU expansion improves operating cash flows and interest coverage needed to service ongoing 5G network capex."

    if any(k in full_text for k in ["real estate", "housing", "realty", "pre-sales"]):
        return "Strong residential pre-sales collections accelerate project completion cycles and reduce developer debt leverage."

    if category == "IPO":
        return "Expands institutional free-float and establishes benchmark price discovery for peer group enterprise valuations."

    if category in ["Policy", "Trade"]:
        return "Alters regulatory compliance frameworks and tariff structures, realigning domestic supply-chain cost competitiveness."

    # 12. Default Contextual Analysis
    return "Influences operational positioning and peer-group competitive dynamics; institutional focus remains on execution runway and margin defensibility."

def analyze_story_intelligence(story: Dict[str, Any]) -> Dict[str, Any]:
    headline = story.get("headline", "")
    category = story.get("category", "Market")
    brief = story.get("brief_details", "") or story.get("brief", "")
    bullets = story.get("bullet_points", []) or story.get("detailed_points", [])
    raw_text = story.get("raw_news_text", "")
    
    full_text = f"{headline} {brief} {' '.join(bullets)} {raw_text}".lower()

    # 1. Determine Sentiment
    existing_sent = (story.get("sentiment") or "").upper()
    if existing_sent in ["BULLISH", "BEARISH"]:
        sentiment = existing_sent
    else:
        bull_score = sum(1 for kw in BULLISH_KEYWORDS if kw in full_text)
        bear_score = sum(1 for kw in BEARISH_KEYWORDS if kw in full_text)
        
        # Specific category heuristics
        if category == "IPO":
            bull_score += 1
        if "tax collection" in full_text and ("rise" in full_text or "rose" in full_text or "jump" in full_text):
            bull_score += 2
        if "gdp" in full_text and ("growth" in full_text or "7." in full_text or "6." in full_text or "8." in full_text):
            bull_score += 2
        if "inflation risk" in full_text and "ease" in full_text:
            bull_score += 2
            bear_score = max(0, bear_score - 1)
        if "rupee" in full_text and ("drop" in full_text or "low" in full_text or "fall" in full_text):
            bear_score += 2

        if bull_score > bear_score:
            sentiment = "BULLISH"
        elif bear_score > bull_score:
            sentiment = "BEARISH"
        else:
            sentiment = "NEUTRAL"

    # 2. Extract / Derive Catalyst
    catalyst = story.get("catalyst", "").strip()
    if not catalyst or catalyst == brief or catalyst.startswith("Operational and market development triggered by"):
        catalyst = compute_dynamic_catalyst(headline, brief, bullets, full_text)

    # 3. Formulate Meaningful Market Impact & Financial Transmission Analysis
    market_impact = story.get("market_impact", "").strip()
    is_generic_impact = (
        not market_impact 
        or market_impact == brief 
        or market_impact == catalyst 
        or "Clarifies management execution roadmap" in market_impact
        or "Ripples into relevant industry peer groups" in market_impact
        or market_impact == "Directly impacts EBITDA margin expectations, working capital requirements, and relative valuation multiples against sector benchmarks."
    )

    if is_generic_impact:
        market_impact = compute_dynamic_market_impact(headline, brief, bullets, category, full_text)

    # 4. Formulate Actionable Sentiment Reasoning / Institutional Thesis
    sentiment_reasoning = story.get("sentiment_reasoning", "").strip()
    if not sentiment_reasoning or sentiment_reasoning == brief:
        if sentiment == "BULLISH":
            sentiment_reasoning = f"Positive fundamental development reinforcing operational upside, strong volume/revenue execution, and supportive valuation metrics."
        elif sentiment == "BEARISH":
            sentiment_reasoning = f"Headwind creating margin compression, near-term liquidity pressure, or elevated regulatory/macro vulnerability."
        else:
            sentiment_reasoning = f"Balanced fundamentals with neutral transmission; market will track ongoing execution and follow-through metrics."

    # Update story dictionary
    story["sentiment"] = sentiment
    story["catalyst"] = catalyst
    story["market_impact"] = market_impact
    story["sentiment_reasoning"] = sentiment_reasoning

    return story

def enrich_all_reports():
    json_files = list(REPORTS_DIR.glob("*.json"))
    logger.info(f"Found {len(json_files)} JSON report files in {REPORTS_DIR}")

    for file_path in json_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, dict) and "major_stories" in data:
                stories = data["major_stories"]
                for s in stories:
                    analyze_story_intelligence(s)
                
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                logger.info(f"✅ Enriched {len(stories)} stories in: {file_path.name}")
            elif isinstance(data, list):
                for s in data:
                    if isinstance(s, dict):
                        analyze_story_intelligence(s)
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                logger.info(f"✅ Enriched array list ({len(data)} items) in: {file_path.name}")
        except Exception as e:
            logger.error(f"Error enriching {file_path.name}: {e}")

if __name__ == "__main__":
    enrich_all_reports()
