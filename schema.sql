-- Schema for Neon PostgreSQL Database (NewsAPI / FinBrief)

CREATE TABLE IF NOT EXISTS editions (
    id SERIAL PRIMARY KEY,
    edition_date DATE NOT NULL,
    source VARCHAR(50) NOT NULL DEFAULT 'financial_express',
    total_pages INT DEFAULT 0,
    total_stories INT DEFAULT 0,
    summary TEXT,
    pdf_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(edition_date, source)
);

CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY,
    edition_id INT REFERENCES editions(id) ON DELETE CASCADE,
    edition_date DATE NOT NULL,
    source VARCHAR(50) NOT NULL DEFAULT 'financial_express',
    category VARCHAR(100) NOT NULL,
    headline TEXT NOT NULL,
    brief_details TEXT,
    bullet_points JSONB DEFAULT '[]'::jsonb,
    page_numbers VARCHAR(500),
    importance VARCHAR(20) DEFAULT 'MEDIUM',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_articles_date_source ON articles(edition_date, source);
CREATE INDEX IF NOT EXISTS idx_articles_category ON articles(category);
