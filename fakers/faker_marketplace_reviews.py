"""
Faker ULASAN media sosial.
Menghasilkan ulasan palsu (rating + teks multibahasa) lalu mengirimnya
ke Marketplace API via POST /reviews. Rating memengaruhi nada teks supaya
hasil analisis sentimen VADER nanti masuk akal.
"""
import random
import time

import requests

from config import settings
from fakers._sources import get_products, get_customer_ids

# Template teks per nada & bahasa (versi sederhana dari "Bayesian network").
POSITIVE = {
    "en": [
        "Outstanding quality! Works perfectly and feels very durable.",
        "Absolutely love it, highly recommend to everyone.",
        "Excellent build and great value for the price.",
    ],
    "id": [
        "Kualitas mantap, sangat memuaskan dan awet!",
        "Barangnya bagus banget, sangat direkomendasikan.",
        "Sesuai ekspektasi, nyaman dipakai.",
    ],
}
NEUTRAL = {
    "en": ["It's okay, does the job.", "Average product, nothing special."],
    "id": ["Lumayan, sesuai harga.", "Biasa saja, standar."],
}
NEGATIVE = {
    "en": ["Disappointed, it broke quickly.", "Poor quality, not worth the money."],
    "id": ["Kecewa, cepat rusak.", "Kualitas buruk, tidak sesuai harapan."],
}


def _make_review():
    # distribusi rating condong positif (mirip data nyata)
    rating = random.choices([5, 4, 3, 2, 1], weights=[40, 25, 15, 10, 10])[0]
    language = random.choice(["en", "id"])
    if rating >= 4:
        text = random.choice(POSITIVE[language])
    elif rating == 3:
        text = random.choice(NEUTRAL[language])
    else:
        text = random.choice(NEGATIVE[language])

    product_id, _ = random.choice(get_products())
    customer_id = random.choice(get_customer_ids())
    return {
        "product_id": product_id,
        "customer_id": customer_id,
        "rating": rating,
        "review_text": text,
        "language": language,
    }


def run(stop_event=None, duration_hours=72):
    deadline = time.time() + duration_hours * 3600
    url = settings.MARKETPLACE_API_URL.rstrip("/") + "/reviews"
    while time.time() < deadline and (stop_event is None or not stop_event.is_set()):
        review = _make_review()
        try:
            resp = requests.post(url, json=review, timeout=10)
            print(f"[reviews] {resp.status_code} rating={review['rating']} lang={review['language']}")
        except Exception as exc:
            print(f"[reviews] gagal kirim: {exc}")
        time.sleep(settings.FAKER_REVIEW_INTERVAL)


if __name__ == "__main__":
    print(_make_review())  # uji cepat: cetak satu contoh review
