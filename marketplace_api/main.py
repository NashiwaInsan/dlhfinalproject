"""
Marketplace API (mensimulasikan sistem ulasan media sosial).

Endpoint:
  POST /reviews            -> faker mengirim ulasan baru ke sini
  GET  /reviews/latest     -> dipakai pipeline ETL untuk menarik ulasan baru
                              berdasarkan watermark (?since=<timestamp ISO>)
  GET  /health             -> cek hidup/mati
"""
import os
from typing import Optional

import psycopg2
import psycopg2.extras
from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

app = FastAPI(title="AdventureWorks Marketplace API")


def get_conn():
    return psycopg2.connect(
        host=os.getenv("PG_HOST", "localhost"),
        port=os.getenv("PG_PORT", "5432"),
        dbname=os.getenv("PG_DB", "marketplace_db"),
        user=os.getenv("PG_USER", "mkuser"),
        password=os.getenv("PG_PASSWORD", "mkpass123"),
    )


class ReviewIn(BaseModel):
    product_id: int
    customer_id: int
    rating: int = Field(ge=1, le=5)
    review_text: str
    language: str = "en"
    is_verified: bool = True


@app.post("/reviews")
def create_review(r: ReviewIn):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO reviews
               (product_id, customer_id, rating, review_text, language, is_verified)
           VALUES (%s, %s, %s, %s, %s, %s)
           RETURNING review_id, created_at""",
        (r.product_id, r.customer_id, r.rating, r.review_text, r.language, r.is_verified),
    )
    review_id, created_at = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return {"review_id": review_id, "created_at": created_at.isoformat()}


@app.get("/reviews/latest")
def latest_reviews(since: Optional[str] = Query(None, description="Timestamp ISO; ambil review setelah ini")):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    if since:
        cur.execute(
            "SELECT * FROM reviews WHERE created_at > %s ORDER BY created_at", (since,)
        )
    else:
        cur.execute("SELECT * FROM reviews ORDER BY created_at")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


@app.get("/health")
def health():
    return {"status": "ok"}
