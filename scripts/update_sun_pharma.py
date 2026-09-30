import json

verbatim_text = """The outlook for Sun Pharma is expected to improve on the back of multiple positive triggers. These include scaling up of its US portfolio, expanding innovative portfolio and tariff deal/specialty drug tariff waiver. The in-licensing deal with LIB Therapeutics to commercialise and manufacture cholesterol-lowering medication Lerodalcibep is also expected to strengthen its innovative medicines portfolio.

While the stock has underperformed its peers sharply over the last six months, there could be some gains given the triggers and target prices. At the current price of ₹1,860, the stock is trading at 27 times its FY28 earnings estimates.

The immediate trigger for the stock is the licensing deal for Lerodalcibep, which belongs to the PCSK9 class of drugs. The exclusive agreement for markets worldwide (excluding the US and China) will open up a $3.7 billion market for the company, growing at an annual rate of 38 per cent.

The global PCSK9 market is expected to be about $7 billion in 2026. LIB will receive upfront and future milestone payments, together with royalties based on net sales in licensed territories. And, Sun Pharma will be responsible for pursuing regulatory approvals in licensed territories where approval has not yet been obtained. 360 ONE Capital Research says that the deal builds on Sun's track record of strengthening its innovative portfolio through in-licensing and acquisitions.

Sun's FY26 innovative medicines grew by 16.8 per cent to $1.42 billion. Plaque psoriasis drug Ilumya, which is the largest product, reported sales of $796 million in FY26 and grew 17 per cent year-on-year (Y-o-Y).

Near-term catalysts, according to Rohit Bhat and Hrishikesh Patole of the brokerage, include the potential USFDA approval of Ilumya for psoriatic arthritis alongside continued ramp up of hairfall (alopecia areata) drug Leqselvi and skin cancer formulation, Unloxyt.

Combined with the proposed $12 billion Organon acquisition, which adds scale across innovative medicines, women's health and biosimilars, the company, according to the brokerage, is building a broader platform for sustained growth. It has a 'buy' rating with a target price of ₹2,250.

The other trigger is the tariff deal with the US which extended the most favoured nation drug pricing to state Medicaid programmes. In a positive, the arrangement, Kotak Research said, excludes Medicare which, along with the commercial channel accounts for the vast majority of Sun Pharma's innovative medicine sales. The deal also provides tariff protection for Sun's US branded portfolio until January 20, 2029.

The company's proposed acquisition (expected to be completed by early 2027), Organon, is outside the scope of the deal and it would need to negotiate a separate agreement. While lower Medicaid pricing is likely to weigh on earnings, the exclusion of Medicare and the tariff reprieve make the overall outcome marginally positive for Sun Pharma, says the brokerage. It has an 'add' rating with a target price of ₹2,150. The specialty drug tariff waiver will also help eliminate and lift the overhang of tariffs.

Geojit Research is also positive on the outlook for Sun Pharma. The approval of semaglutide in multiple markets, steady performance of its flagship brands, such as Ilumya, and progress in the commercialisation of new specialty products highlight its focus on innovation-led growth, it says. The proposed Organon acquisition is expected to broaden its therapeutic presence through the women's health and biosimilars portfolios while further enhancing its global reach. It has retained a 'buy' rating on the stock with a revised target price of ₹2,070."""

sun_pharma_story = {
    "headline": "Innovation portfolio may boost Sun Pharma stock",
    "companies_mentioned": ["Sun Pharma", "Sun Pharmaceutical Industries", "LIB Therapeutics", "Organon"],
    "sectors_impacted": ["Pharmaceuticals & Healthcare", "Stock Markets"],
    "page_numbers": ["BS (Page 22)"],
    "brief": "Sun Pharma outlook improves on triggers including US portfolio scaling, innovative medicine expansion, and licensing deal for cholesterol drug Lerodalcibep.",
    "detailed_points": [
        "In-licensing deal with LIB Therapeutics for PCSK9 drug Lerodalcibep opens a $3.7B market growing at 38% annually.",
        "Innovative medicines portfolio grew 16.8% in FY26 to $1.42 billion, led by plaque psoriasis drug Ilumya ($796M sales, +17% YoY).",
        "Near-term catalysts include potential USFDA approval of Ilumya for psoriatic arthritis, Leqselvi ramp-up, and Unloxyt skin cancer formulation.",
        "Brokerages remain bullish: 360 ONE targets ₹2,250 (Buy), Kotak targets ₹2,150 (Add), and Geojit targets ₹2,070 (Buy)."
    ],
    "bullish_signals": [
        "Global PCSK9 market expanding to $7B in 2026; deal provides exclusive worldwide commercialization rights outside US/China.",
        "Tariff protection secured for US branded portfolio until January 20, 2029; Medicare excluded from price caps.",
        "Proposed $12B Organon acquisition adds strategic scale in women's health, biosimilars, and global distribution."
    ],
    "bearish_signals": [
        "Stock has underperformed peers sharply over the last 6 months; currently trades at 27x FY28 EPS.",
        "Lower Medicaid pricing under US MFN deal could exert modest pressure on earnings."
    ],
    "quant_data": {
        "stock_price": "₹1,860",
        "target_prices": "₹2,070 - ₹2,250",
        "valuation_pe": "27x FY28 earnings",
        "innovative_sales_fy26": "$1.42 Billion (+16.8% YoY)",
        "ilumya_sales_fy26": "$796 Million (+17% YoY)",
        "market_opportunity_pcsk9": "$3.7 Billion (growing at 38% CAGR)",
        "global_pcsk9_market_2026": "$7 Billion",
        "proposed_organon_acquisition": "$12 Billion"
    },
    "raw_news_text": verbatim_text
}

targets = [
    "reports/news_report_unified_latest.json",
    "reports/news_report_unified_2026-09-29.json",
    "reports/news_report_bs_2026-09-29.json",
    "reports/news_report_2026-09-29.json"
]

for p in targets:
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        stories = data.get("major_stories", [])
        replaced = False
        for idx, s in enumerate(stories):
            if "sun pharma" in s.get("headline", "").lower() or "innovation portfolio" in s.get("headline", "").lower():
                stories[idx] = sun_pharma_story
                replaced = True
                break
        if not replaced:
            stories.insert(0, sun_pharma_story)
        
        data["major_stories"] = stories
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Updated {p} successfully")
    except Exception as e:
        print(f"Error {p}: {e}")
