#!/usr/bin/env python3
"""
Scraper für psychologie.ch PsyFinder
Extrahiert alle Therapeuten-Profile aus der Sitemap und speichert als CSV.
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import re
import sys

SITEMAP_URL = "https://www.psychologie.ch/sitemap.xml"
OUTPUT_FILE = "/Users/cirilbullinger/Documents/Code Ablage/Cursör/PsyFinder Scrapen/therapeuten.csv"
DELAY = 0.5  # Sekunden zwischen Requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "de-DE,de;q=0.9",
}

CSV_FIELDS = [
    "slug",
    "name",
    "praxis_name",
    "strasse",
    "plz_ort",
    "telefon",
    "email",
    "website",
    "verfuegbarkeit",
    "online_beratung",
    "sprachen",
    "angebot",
    "zielgruppen",
    "abrechnung",
    "fsp_titel",
    "url",
]

# Label-Mapping: Seitentext-Label -> CSV-Feld
LABEL_MAP = {
    "telefon": "telefon",
    "e-mail-adresse": "email",
    "website": "website",
    "verfügbarkeit": "verfuegbarkeit",
    "online-beratung": "online_beratung",
    "sprachen": "sprachen",
    "angebot": "angebot",
    "zielgruppen": "zielgruppen",
    "abrechnung": "abrechnung",
    "fsp-titel": "fsp_titel",
}

# Labels die mehrwertig sind (bis zum nächsten Label gesammelt)
MULTI_VALUE_LABELS = {"sprachen", "angebot", "zielgruppen", "abrechnung", "fsp-titel"}


def get_all_psyfinder_urls():
    """Holt alle /de/psyfinder/ URLs aus der Sitemap."""
    print("Lade Sitemap...", flush=True)
    resp = requests.get(SITEMAP_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.content, "xml")
    seen = set()
    urls = []

    for loc in soup.find_all("loc"):
        url = loc.text.strip()
        if "/de/psyfinder/" in url:
            slug = url.split("/de/psyfinder/")[-1].rstrip("/")
            # Nur echte Profile (kein leerer Slug, keine weiteren Pfadsegmente)
            if slug and "/" not in slug and slug not in seen:
                seen.add(slug)
                urls.append(url)

    print(f"Gefunden: {len(urls)} Profile in der Sitemap", flush=True)
    return urls


def parse_profile(url, html):
    """Extrahiert Kontaktdaten aus einer Profil-Seite via Text-Parsing."""
    soup = BeautifulSoup(html, "lxml")
    data = {f: "" for f in CSV_FIELDS}
    data["url"] = url
    data["slug"] = url.split("/de/psyfinder/")[-1].rstrip("/")

    main = soup.find("main") or soup.body
    full_text = main.get_text(separator="\n", strip=True)
    lines = [l.strip() for l in full_text.split("\n") if l.strip()]

    # Name: H1
    h1 = soup.select_one("h1")
    if h1:
        data["name"] = h1.get_text(strip=True)

    # Finde den Abschnitt nach "Psyfinder" Breadcrumb
    try:
        start = next(i for i, l in enumerate(lines) if l == data["name"])
    except StopIteration:
        start = 0

    profile_lines = lines[start:]

    # Praxis-Name: zweite Zeile nach Name (wenn nicht PLZ/Straße)
    if len(profile_lines) > 1:
        candidate = profile_lines[1]
        # Praxis-Name hat keine reine Zahl am Anfang und ist kein Label
        if not re.match(r'^\d{4}$', candidate) and candidate.lower() not in LABEL_MAP:
            data["praxis_name"] = candidate

    # Straße: erste Zeile die wie eine Adresse aussieht
    for line in profile_lines[:10]:
        if re.match(r'.+\d+', line) and not re.match(r'^\+', line) and not re.match(r'^\d{4}$', line):
            if "http" not in line and "@" not in line and line != data["name"] and line != data["praxis_name"]:
                data["strasse"] = line.strip(" -,")
                break

    # PLZ + Ort: 4-stellige Zahl gefolgt von Stadtname
    for i, line in enumerate(profile_lines[:15]):
        if re.match(r'^\d{4}$', line):
            ort = profile_lines[i + 1] if i + 1 < len(profile_lines) else ""
            if ort and not re.match(r'^\d{4}$', ort):
                data["plz_ort"] = f"{line} {ort.strip(' ,')}"
            break
    else:
        # Alternative: PLZ und Ort in einer Zeile
        for line in profile_lines[:15]:
            m = re.search(r'\b(\d{4})\s+([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ\s\-]+)', line)
            if m:
                data["plz_ort"] = f"{m.group(1)} {m.group(2).strip()}"
                break

    # Telefon: tel: link hat Vorrang
    tel_link = soup.select_one('a[href^="tel:"]')
    if tel_link:
        data["telefon"] = tel_link.get("href", "").replace("tel:", "").strip()
    else:
        # Aus Text
        for i, line in enumerate(profile_lines):
            if line.lower() == "telefon" and i + 1 < len(profile_lines):
                candidate = profile_lines[i + 1]
                if re.match(r'[\+\d]', candidate):
                    data["telefon"] = candidate
                    break

    # E-Mail: mailto: link hat Vorrang
    mail_link = soup.select_one('a[href^="mailto:"]')
    if mail_link:
        data["email"] = mail_link.get("href", "").replace("mailto:", "").strip()

    # Website: aus Text (Label "Website")
    for i, line in enumerate(profile_lines):
        if line.lower() == "website" and i + 1 < len(profile_lines):
            candidate = profile_lines[i + 1]
            if candidate.startswith("http") and "psychologie.ch" not in candidate:
                data["website"] = candidate
                break

    # Einzel-Labels
    for i, line in enumerate(profile_lines):
        label = line.lower()
        if label in LABEL_MAP and label not in MULTI_VALUE_LABELS:
            field = LABEL_MAP[label]
            if not data[field] and i + 1 < len(profile_lines):
                data[field] = profile_lines[i + 1]

    # Multi-Wert-Labels: sammle alle Zeilen bis zum nächsten bekannten Label
    known_labels = set(LABEL_MAP.keys()) | {"über mich", "spezialisierung", "informationen", "adresse",
                                              "soziale netzwerke", "auf der karte"}
    for i, line in enumerate(profile_lines):
        label = line.lower()
        if label in MULTI_VALUE_LABELS:
            field = LABEL_MAP[label]
            values = []
            j = i + 1
            while j < len(profile_lines):
                next_line = profile_lines[j]
                if next_line.lower() in known_labels:
                    break
                values.append(next_line)
                j += 1
            if not data[field]:
                data[field] = "; ".join(values)

    return data


def scrape_all():
    urls = get_all_psyfinder_urls()

    if not urls:
        print("FEHLER: Keine URLs gefunden!")
        sys.exit(1)

    print(f"Starte Scraping von {len(urls)} Profilen...", flush=True)
    print(f"Geschätzte Dauer: ~{len(urls) * DELAY / 60:.0f} Minuten bei {DELAY}s Delay", flush=True)

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()

        session = requests.Session()
        session.headers.update(HEADERS)

        errors = 0
        ok = 0
        for i, url in enumerate(urls, 1):
            try:
                resp = session.get(url, timeout=15)
                if resp.status_code == 200:
                    data = parse_profile(url, resp.text)
                    writer.writerow(data)
                    f.flush()
                    ok += 1
                else:
                    errors += 1
                    print(f"  HTTP {resp.status_code}: {url}", flush=True)
            except Exception as e:
                errors += 1
                print(f"  FEHLER bei {url}: {e}", flush=True)

            if i % 50 == 0:
                print(f"  {i}/{len(urls)} ({i/len(urls)*100:.1f}%) – OK: {ok}, Fehler: {errors}", flush=True)

            time.sleep(DELAY)

    print(f"\nFertig! {ok} Profile gespeichert, {errors} Fehler.")
    print(f"CSV: {OUTPUT_FILE}")


if __name__ == "__main__":
    scrape_all()
