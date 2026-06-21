"""
Menjalankan satu atau beberapa faker daemon sekaligus (tiap satu thread).

Contoh pemakaian (jalankan dari root proyek):
    python run_fakers.py                         # semua faker, 72 jam
    python run_fakers.py --sources store_excel   # hanya Excel
    python run_fakers.py --sources marketplace sales_online --duration 1
Tekan Ctrl+C untuk berhenti.
"""
import argparse
import threading

from fakers import faker_sales_online, faker_store_excel, faker_marketplace_reviews

FAKERS = {
    "sales_online": faker_sales_online.run,
    "store_excel": faker_store_excel.run,
    "marketplace": faker_marketplace_reviews.run,
}


def main():
    parser = argparse.ArgumentParser(description="Jalankan faker daemon")
    parser.add_argument(
        "--sources", nargs="+", default=["all"],
        choices=sorted(FAKERS.keys()) + ["all"],
        help="Faker yang dijalankan",
    )
    parser.add_argument("--duration", type=float, default=72, help="Durasi jam")
    args = parser.parse_args()

    sources = list(FAKERS.keys()) if "all" in args.sources else args.sources

    stop_event = threading.Event()
    threads = []
    for src in sources:
        t = threading.Thread(
            target=FAKERS[src],
            kwargs={"stop_event": stop_event, "duration_hours": args.duration},
            daemon=True,
            name=f"faker-{src}",
        )
        t.start()
        threads.append(t)
        print(f"start faker: {src}")

    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        print("\nMenghentikan faker...")
        stop_event.set()
        for t in threads:
            t.join(timeout=5)


if __name__ == "__main__":
    main()
