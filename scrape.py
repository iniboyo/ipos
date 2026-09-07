"""
Scraper: stockanalysis.com/ipos/calendar -> ICS feed berisi IPO NASDAQ.

Cara kerja:
1. Ambil HTML halaman kalender IPO stockanalysis.com
2. Cari tabel yang punya kolom "Symbol" dan "IPO Date"
3. Filter baris yang Exchange == NASDAQ
4. Bangun file .ics (all-day event per IPO) ke docs/ipo_nasdaq.ics

File ICS ini nantinya di-hosting via GitHub Pages dan di-subscribe
langsung ke Apple Calendar / Google Calendar / Outlook.
"""

import sys
from datetime import datetime, timedelta, timezone

import pandas as pd
import requests

URL = "https://stockanalysis.com/ipos/calendar/"
OUTPUT_PATH = "docs/ipo_nasdaq.ics"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}


def fetch_ipo_table() -> pd.DataFrame:
    """Ambil HTML dan cari tabel IPO yang relevan."""
    resp = requests.get(URL, headers=HEADERS, timeout=20)
    resp.raise_for_status()

    tables = pd.read_html(resp.text)
    for df in tables:
        cols = [str(c).strip() for c in df.columns]
        if "Symbol" in cols and any(c in cols for c in ("IPO Date", "Date")):
            return df

    raise RuntimeError(
        "Tabel IPO tidak ditemukan di halaman. "
        "Kemungkinan struktur situs stockanalysis.com berubah - "
        "cek ulang script parsing."
    )


def clean_rows(df: pd.DataFrame) -> list[dict]:
    date_col = "IPO Date" if "IPO Date" in df.columns else "Date"
    rows = []

    for _, r in df.iterrows():
        exchange = str(r.get("Exchange", "")).strip().upper()
        if exchange != "NASDAQ":
            continue

        try:
            ipo_date = pd.to_datetime(r[date_col], errors="raise").date()
        except Exception:
            # Baris tanggal yang tidak valid (mis. "TBD") dilewati
            continue

        rows.append(
            {
                "date": ipo_date,
                "symbol": str(r.get("Symbol", "")).strip(),
                "name": str(r.get("Company Name", "")).strip(),
                "price_range": str(r.get("Price Range", "")).strip(),
                "shares": str(r.get("Shares Offered", "")).strip(),
                "deal_size": str(r.get("Deal Size", "")).strip(),
            }
        )

    return rows


def escape_ics(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\n", "\\n")
    )


def build_ics(rows: list[dict]) -> str:
    now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//IPO Nasdaq Calendar//stockanalysis-scraper//ID",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:IPO NASDAQ Calendar",
        "X-WR-CALDESC:Jadwal IPO NASDAQ, sumber data: stockanalysis.com",
        "X-WR-TIMEZONE:UTC",
        "REFRESH-INTERVAL;VALUE=DURATION:PT6H",
    ]

    for row in rows:
        dtstart = row["date"].strftime("%Y%m%d")
        dtend = (row["date"] + timedelta(days=1)).strftime("%Y%m%d")
        uid = f"{row['symbol']}-{dtstart}@ipo-nasdaq-calendar"
        summary = f"IPO: {row['symbol']} - {row['name']}"

        desc_parts = []
        if row["price_range"] and row["price_range"] != "nan":
            desc_parts.append(f"Price range: {row['price_range']}")
        if row["shares"] and row["shares"] != "nan":
            desc_parts.append(f"Shares offered: {row['shares']}")
        if row["deal_size"] and row["deal_size"] != "nan":
            desc_parts.append(f"Deal size: {row['deal_size']}")
        desc_parts.append("Source: stockanalysis.com/ipos/calendar")
        description = escape_ics(" | ".join(desc_parts))

        lines += [
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{now}",
            f"DTSTART;VALUE=DATE:{dtstart}",
            f"DTEND;VALUE=DATE:{dtend}",
            f"SUMMARY:{escape_ics(summary)}",
            f"DESCRIPTION:{description}",
            "END:VEVENT",
        ]

    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


def main() -> None:
    df = fetch_ipo_table()
    rows = clean_rows(df)
    ics_content = build_ics(rows)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(ics_content)

    print(f"OK: {len(rows)} event IPO NASDAQ ditulis ke {OUTPUT_PATH}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        print(f"GAGAL: {exc}", file=sys.stderr)
        sys.exit(1)
