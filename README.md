# 📰 Daily Newspaper Automation & Gemini Flash Analysis Pipeline

A Python automation system that runs daily to:
1. Log into newspaper web portals (e.g. Financial Express ePaper) using **Playwright**.
2. Download today's complete 64-page PDF edition.
3. Upload and send the 64-page PDF to the **Google Gemini Flash API** via the official `google-genai` SDK (`gemini-2.5-flash`).
4. Extract all major news stories with structured headlines, category breakdown, page numbers, brief details, bullet points, and importance levels.
5. Save output in both structured **JSON** and human-readable **Markdown** summary reports.

---

## 🏗️ Architecture Overview

```
NewsAPI/
├── config.py         # Environment configuration & validation
├── downloader.py     # Playwright automated login & PDF edition downloader
├── analyzer.py       # Google Gemini Flash API PDF processor (using official google-genai SDK)
├── main.py           # CLI entry point & continuous daily scheduler
├── requirements.txt  # Python package dependencies
├── .env.example      # Sample environment variables configuration
├── downloads/        # Storage for downloaded 64-page PDF editions
└── reports/          # Storage for generated JSON and Markdown news reports
```

---

## ⚡ Quick Start

### 1. Prerequisites
- Python 3.10+
- Google Gemini API Key ([Get one here](https://aistudio.google.com/))

### 2. Setup Virtual Environment & Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser binaries
playwright install chromium
```

### 3. Environment Configuration

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
NEWSPAPER_URL=https://epaper.financialexpress.com/4203631/Mumbai/September-27-2026#page/1/1
NEWSPAPER_USERNAME=your_username@example.com
NEWSPAPER_PASSWORD=your_password
SCHEDULE_TIME=06:00
```

---

## 🚀 Running the Automation

### Run Immediately Once
```bash
python main.py --run-now
```

### Analyze an Existing Local PDF Directly
If you already have a 64-page newspaper PDF downloaded:
```bash
python main.py --pdf /path/to/today_edition.pdf
```

### Run Daily Schedule (Daemon Mode)
To run continuously every day at the scheduled time (e.g., `06:00`):
```bash
python main.py --daemon --schedule-time 06:00
```

---

## ⏰ Cron Job Setup (Alternative Daily Scheduler)

If you prefer system `cron` over running a background Python daemon:

```bash
crontab -e
```

Add the following entry to run every morning at 06:00:
```cron
0 6 * * * cd /Users/debasissahoo/Documents/NewsAPI && /Users/debasissahoo/Documents/NewsAPI/venv/bin/python main.py --run-now >> /Users/debasissahoo/Documents/NewsAPI/newspaper_automation.log 2>&1
```

---

## 📄 Output Reports

Reports are automatically written to `./reports/`:
- `news_report_YYYY-MM-DD.json`: Full Pydantic validated JSON data structure.
- `news_report_YYYY-MM-DD.md`: Rendered markdown with formatted badges, bullet points, and category sections.
