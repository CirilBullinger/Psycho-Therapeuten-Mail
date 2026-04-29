# Psychotherapeuten Mail Kampagne

Automatisiertes E-Mail-Kampagnen-System für die Rekrutierung von Psychotherapeuten für PsyCare.

## Features

- 📧 **Multi-Stage E-Mail-Kampagne**: Automatischer Versand von bis zu 3 Follow-up E-Mails
- 🎯 **Personalisierung**: Automatische Anrede-Generierung (Sie/Du-Form)
- 🔒 **Rate Limiting**: Konfigurierbare Tageslimits und Verzögerungen
- 📊 **Response Tracking**: Automatische Erkennung von Antworten via IMAP
- 🌍 **Mehrsprachig**: Unterstützung für deutschsprachige Therapeuten
- 🔄 **Daten-Merge**: Tools zum Zusammenführen mehrerer Therapeutenlisten

## Struktur

```
.
├── send_campaign.py          # Haupt-Kampagnen-Script
├── run_campaign.py           # Kombiniertes Script (Tracking + Versand)
├── check_responses.py        # Response-Tracking via IMAP
├── merge_winterthur.py       # Merge-Tool für neue Therapeutenlisten
├── scrape_psyfinder.py       # Web-Scraper für psychologie.ch
├── process_therapeuten.py    # Datenverarbeitung und -bereinigung
├── prepare_campaign_csv.py   # CSV-Vorbereitung
├── templates/                # E-Mail-Templates
│   ├── email_1_sie.txt      # Erste E-Mail (Sie-Form)
│   ├── email_2_sie.txt      # Follow-up 1 (Sie-Form)
│   ├── email_3_sie.txt      # Follow-up 2 (Sie-Form)
│   ├── email_1_du.txt       # Erste E-Mail (Du-Form)
│   ├── email_2_du.txt       # Follow-up 1 (Du-Form)
│   └── email_3_du.txt       # Follow-up 2 (Du-Form)
└── config.json              # Konfiguration (nicht in Git!)
```

## Installation

1. Python 3.7+ erforderlich
2. Keine externen Dependencies nötig (nur Standard-Bibliothek)

## Konfiguration

1. Kopiere `config.example.json` zu `config.json`
2. Fülle die E-Mail-Zugangsdaten aus:

```json
{
  "email": {
    "smtp_server": "your-smtp-server.com",
    "smtp_port": 465,
    "imap_server": "your-imap-server.com",
    "imap_port": 993,
    "username": "your-email@example.com",
    "password": "your-password",
    "from_name": "Your Name",
    "from_email": "your-email@example.com"
  },
  "campaign": {
    "csv_file": "therapeuten_kampagne.csv",
    "daily_limit": 50,
    "delay_min_seconds": 30,
    "delay_max_seconds": 90,
    "days_between_email_1_and_2": 3,
    "days_between_email_2_and_3": 5,
    "anrede_type": "sie",
    "prioritize_deutsch": true
  }
}
```

## Verwendung

### Tägliche Kampagne ausführen

```bash
python3 run_campaign.py
```

Führt automatisch aus:
1. Response-Tracking (prüft auf Antworten)
2. E-Mail-Versand (bis zu daily_limit E-Mails)

### Nur E-Mails versenden

```bash
python3 send_campaign.py
```

### Nur Responses prüfen

```bash
python3 check_responses.py
```

### Neue Therapeutenliste hinzufügen

```bash
python3 merge_winterthur.py
```

## CSV-Format

Die Kampagnen-CSV benötigt folgende Spalten:

- `email`: E-Mail-Adresse
- `vorname`: Vorname
- `nachname`: Nachname
- `anrede`: Formelle Anrede (z.B. "Geschätzter Herr Müller")
- `anrede_du`: Informelle Anrede (z.B. "Hallo Thomas")
- `spricht_deutsch`: "X" wenn deutschsprachig
- `email_1_sent_date`: Datum der ersten E-Mail (YYYY-MM-DD)
- `email_2_sent_date`: Datum der zweiten E-Mail
- `email_3_sent_date`: Datum der dritten E-Mail
- `responded`: "Ja" wenn geantwortet
- `responded_date`: Datum der Antwort
- `anrede_type_used`: "sie" oder "du" (wird automatisch gesetzt)

## Sicherheit

⚠️ **WICHTIG**: 
- `config.json` enthält Zugangsdaten und ist in `.gitignore`
- CSV-Dateien mit persönlichen Daten werden nicht committed
- Verwende `config.example.json` als Vorlage

## E-Mail-Templates

Templates verwenden folgende Platzhalter:
- `{{ANREDE}}`: Wird durch die passende Anrede ersetzt
- `{{VORNAME}}`: Vorname (nur in Betreff)
- `{{NACHNAME}}`: Nachname (nur in Betreff)

## Kampagnen-Logik

1. **E-Mail 1**: Sofort an alle, die noch keine E-Mail erhalten haben
2. **E-Mail 2**: 3 Tage nach E-Mail 1 (wenn keine Antwort)
3. **E-Mail 3**: 5 Tage nach E-Mail 2 (wenn keine Antwort)

Response-Tracking markiert automatisch Therapeuten, die geantwortet haben.

## Lizenz

Privates Projekt für PsyCare
