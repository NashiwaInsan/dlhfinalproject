-- Skema penyimpanan ulasan marketplace (dijalankan otomatis saat container
-- PostgreSQL pertama kali dibuat).
CREATE TABLE IF NOT EXISTS reviews (
    review_id    SERIAL PRIMARY KEY,
    product_id   INT  NOT NULL,
    customer_id  INT  NOT NULL,
    rating       INT  NOT NULL CHECK (rating BETWEEN 1 AND 5),
    review_text  TEXT NOT NULL,
    language     VARCHAR(10) DEFAULT 'en',
    is_verified  BOOLEAN     DEFAULT TRUE,
    review_date  TIMESTAMPTZ DEFAULT now(),
    created_at   TIMESTAMPTZ DEFAULT now()
);

-- Index pada created_at mempercepat query incremental (WHERE created_at > watermark).
CREATE INDEX IF NOT EXISTS idx_reviews_created_at ON reviews (created_at);
