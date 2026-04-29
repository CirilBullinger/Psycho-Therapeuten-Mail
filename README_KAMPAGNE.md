# 📧 E-Mail-Kampagnen-System für Therapeuten-Rekrutierung

Automatisiertes System zum Versand personalisierter E-Mails an Therapeuten mit Tracking und Response-Management.

## 📋 Übersicht

Das System versendet automatisch drei E-Mails:
1. **E-Mail 1**: Erste Kontaktaufnahme
2. **E-Mail 2**: Follow-up nach 3 Tagen
3. **E-Mail 3**: Letzter Reminder nach weiteren 5 Tagen

**Features:**
- ✅ Personalisierte Anrede für jeden Therapeuten
- ✅ Automatisches Tracking (wer hat welche E-Mail erhalten)
- ✅ Response-Tracking (wer hat geantwortet)
- ✅ Rate-Limiting (max. 100 E-Mails pro Tag)
- ✅ Zufällige Verzögerung zwischen E-Mails (30-90 Sekunden)
- ✅ Dry-Run Modus zum Testen
- ✅ Vollständiges Logging

## 📁 Dateien im System

```
.
├── config.json                      # Konfiguration (NICHT committen!)
├── therapeuten_kampagne.csv         # Haupt-CSV mit Tracking-Spalten
├── templates/
│   ├── email_1.html                # Template für erste E-Mail
│   ├── email_2.html                # Template für Follow-up
│   ├── email_3.html                # Template für Reminder
│   └── subjects.txt                # Betreff-Zeilen
├── send_campaign.py                 # Haupt-Skript für Versand
├── check_responses.py               # Prüft auf Antworten
├── test_email.py                    # Test-Versand
├── prepare_campaign_csv.py          # CSV-Vorbereitung
└── campaign_log.txt                 # Log-Datei
```

## 🚀 Schnellstart

### 1️⃣ Test-E-Mail senden

**Erste wichtige Aktion:** Teste das System mit einer E-Mail an dich selbst!

```bash
python3 test_email.py
```

Folge den Anweisungen:
- Wähle welche E-Mail du testen möchtest (1, 2, 3 oder alle)
- Die E-Mail wird an deine eigene Adresse gesendet
- Prüfe dein Postfach und kontrolliere Formatierung/Inhalt

### 2️⃣ Dry-Run (Test ohne echten Versand)

Teste die Kampagnen-Logik **ohne** echte E-Mails zu versenden:

```bash
python3 send_campaign.py --dry-run
```

Das zeigt dir:
- Wie viele E-Mails versendet würden
- An wen sie gehen würden
- Welche E-Mail-Sequenz gewählt wird
- **ABER:** Es werden KEINE echten E-Mails versendet!

### 3️⃣ Echte Kampagne starten

**Erst nach erfolgreichen Tests!**

```bash
python3 send_campaign.py
```

Das System:
- Versendet max. 100 E-Mails pro Lauf
- Aktualisiert automatisch die CSV
- Loggt alle Aktivitäten in `campaign_log.txt`

### 4️⃣ Response-Tracking

Prüfe auf Antworten von Therapeuten:

```bash
python3 check_responses.py
```

Das System:
- Verbindet sich mit deinem IMAP-Postfach
- Sucht nach E-Mails von Therapeuten
- Markiert Antworten in der CSV
- Verhindert weitere E-Mails an Personen, die geantwortet haben

## 📅 Empfohlener Tagesablauf

### Täglich (z.B. 9:00 Uhr morgens):

```bash
# 1. Prüfe zuerst auf Antworten
python3 check_responses.py

# 2. Versende E-Mails für heute
python3 send_campaign.py
```

**Das war's!** Dauert nur 1-2 Minuten pro Tag.

## ⚙️ Konfiguration

Die `config.json` enthält alle Einstellungen:

### E-Mail-Einstellungen
```json
"email": {
  "smtp_server": "asmtp.mail.hostpoint.ch",
  "smtp_port": 465,
  "imap_server": "imap.mail.hostpoint.ch",
  "imap_port": 993,
  "username": "bullinger@psychotherapie-portal.ch",
  "password": "Uebergangspasswort01"
}
```

### Kampagnen-Einstellungen
```json
"campaign": {
  "daily_limit": 100,                      # Max. E-Mails pro Tag
  "delay_min_seconds": 30,                 # Min. Verzögerung
  "delay_max_seconds": 90,                 # Max. Verzögerung
  "days_between_email_1_and_2": 3,        # Tage zwischen E-Mail 1 und 2
  "days_between_email_2_and_3": 5         # Tage zwischen E-Mail 2 und 3
}
```

## 📊 CSV-Struktur

Die `therapeuten_kampagne.csv` enthält zusätzliche Tracking-Spalten:

| Spalte | Beschreibung |
|--------|--------------|
| `email_1_sent_date` | Datum wann E-Mail 1 versendet wurde |
| `email_2_sent_date` | Datum wann E-Mail 2 versendet wurde |
| `email_3_sent_date` | Datum wann E-Mail 3 versendet wurde |
| `responded` | "Ja" wenn Person geantwortet hat |
| `responded_date` | Datum der Antwort |
| `notes` | Freitext für Notizen |

## 🔍 Wie funktioniert die Logik?

### E-Mail 1 wird gesendet wenn:
- ✅ Noch keine E-Mail 1 gesendet wurde
- ✅ Person hat nicht geantwortet

### E-Mail 2 wird gesendet wenn:
- ✅ E-Mail 1 wurde bereits gesendet
- ✅ Mindestens 3 Tage sind seit E-Mail 1 vergangen
- ✅ Person hat nicht geantwortet
- ✅ E-Mail 2 wurde noch nicht gesendet

### E-Mail 3 wird gesendet wenn:
- ✅ E-Mail 2 wurde bereits gesendet
- ✅ Mindestens 5 Tage sind seit E-Mail 2 vergangen
- ✅ Person hat nicht geantwortet
- ✅ E-Mail 3 wurde noch nicht gesendet

## 📈 Fortschritt verfolgen

### Status überprüfen:

```bash
# Zeigt Statistik der Kampagne
cat campaign_log.txt | tail -20
```

### CSV analysieren:

```python
import pandas as pd
df = pd.read_csv('therapeuten_kampagne.csv')

# Wie viele haben E-Mail 1 bekommen?
print(f"E-Mail 1 gesendet: {df['email_1_sent_date'].notna().sum()}")

# Wie viele haben geantwortet?
print(f"Antworten: {(df['responded'] == 'Ja').sum()}")

# Response-Rate berechnen
sent = df['email_1_sent_date'].notna().sum()
responded = (df['responded'] == 'Ja').sum()
print(f"Response-Rate: {responded/sent*100:.1f}%")
```

## 🛡️ Sicherheit

**WICHTIG:**
- ❌ **NIEMALS** `config.json` ins Git committen!
- ❌ **NIEMALS** CSV-Dateien mit echten Daten teilen!
- ✅ `.gitignore` ist bereits konfiguriert
- ✅ Passwort sollte nach Tests geändert werden

## 🐛 Troubleshooting

### "Authentication failed"
- Prüfe Username/Passwort in `config.json`
- Prüfe ob SMTP/IMAP bei Hostpoint aktiviert sind

### "Connection refused"
- Prüfe Server-Adressen in `config.json`
- Prüfe Firewall/Internetverbindung

### E-Mails kommen nicht an
- Prüfe Spam-Ordner
- Teste zuerst mit `test_email.py`
- Erhöhe Verzögerung in Config (weniger = weniger Spam-verdächtig)

### CSV wird nicht aktualisiert
- Prüfe Schreibrechte im Ordner
- Stelle sicher, dass CSV nicht in Excel geöffnet ist

## 📞 Tipps für beste Resultate

1. **Starte klein**: Erste Tage mit Dry-Run testen
2. **Timing**: Versende morgens zwischen 9-11 Uhr
3. **Monitoring**: Prüfe täglich das Log
4. **Response-Rate**: ~5-10% ist normal für Cold Outreach
5. **Anpassen**: Wenn Response-Rate zu niedrig, überarbeite Templates

## 📊 Zeitplan-Beispiel

Angenommen du startest heute (Tag 1):

| Tag | Aktion | E-Mails |
|-----|--------|---------|
| 1 | Start | 100 × E-Mail 1 |
| 2 | Versand | 100 × E-Mail 1 |
| 3 | Versand | 100 × E-Mail 1 |
| 4 | Versand + Follow-up | 100 × E-Mail 1 + erste E-Mails 2 |
| 5 | Versand + Follow-up | 100 × E-Mail 1 + E-Mails 2 |
| ... | ... | ... |
| 11 | Alle E-Mail 1 versendet | Nur noch Follow-ups |
| 14+ | Reminder-Phase | E-Mails 3 beginnen |

**Gesamt-Dauer:** ~14-16 Tage für alle 1058 Therapeuten

## ✅ Checkliste vor Start

- [ ] Test-E-Mail an mich selbst gesendet (`test_email.py`)
- [ ] Dry-Run erfolgreich getestet (`--dry-run`)
- [ ] E-Mail-Templates gelesen und überprüft
- [ ] Config geprüft (Server, Passwort, Limits)
- [ ] Backup von `therapeuten_kampagne.csv` erstellt
- [ ] Log-Datei vorbereitet
- [ ] Response-Tracking getestet (`check_responses.py`)

## 🎯 Nächste Schritte

1. **JETZT:** Test-E-Mail senden
2. **Dann:** Dry-Run ausführen
3. **Wenn alles OK:** Echte Kampagne starten
4. **Täglich:** Response-Tracking + Versand

Viel Erfolg! 🚀
