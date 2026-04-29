# 🎯 A/B-Testing: Sie vs. Du - Anleitung

## Übersicht

Das System unterstützt jetzt vollständig separate Templates für Sie- und Du-Form mit **automatischer Konsistenz** für Follow-ups.

## ✅ Wie es funktioniert:

### **Konsistenz garantiert:**
- Person bekommt E-Mail 1 mit **Sie** → E-Mail 2 + 3 auch mit **Sie**
- Person bekommt E-Mail 1 mit **Du** → E-Mail 2 + 3 auch mit **Du**

Das wird automatisch in der CSV-Spalte `anrede_type_used` gespeichert!

## 📁 Template-Struktur:

```
templates/
├── email_1_sie.txt    # E-Mail 1 mit Sie-Form
├── email_1_du.txt     # E-Mail 1 mit Du-Form
├── email_2_sie.txt    # E-Mail 2 mit Sie-Form
├── email_2_du.txt     # E-Mail 2 mit Du-Form
├── email_3_sie.txt    # E-Mail 3 mit Sie-Form
└── email_3_du.txt     # E-Mail 3 mit Du-Form
```

## 🔄 Zwischen Sie/Du wechseln:

### **Tag 1: Sie-Form**
Editiere `config.json`:
```json
"anrede_type": "sie"
```

Führe aus:
```bash
python3 run_campaign.py
```

→ 100 Therapeuten bekommen E-Mails mit "Sie" + werden als "sie" markiert

---

### **Tag 2: Du-Form**
Editiere `config.json`:
```json
"anrede_type": "du"
```

Führe aus:
```bash
python3 run_campaign.py
```

→ 100 Therapeuten bekommen E-Mails mit "Du" + werden als "du" markiert

---

### **Tag 3: Wieder Sie-Form**
```json
"anrede_type": "sie"
```

Und so weiter...

## 📊 Empfohlener Testplan:

### **Option 1: Alternierend (Empfohlen)**
```
Tag 1: sie  → 100 Therapeuten
Tag 2: du   → 100 Therapeuten
Tag 3: sie  → 100 Therapeuten
Tag 4: du   → 100 Therapeuten
...
```

**Vorteil:** Zeitliche Faktoren werden ausgeglichen (Wochentag, etc.)

### **Option 2: Hälften**
```
Tag 1-5:  sie → 500 Therapeuten
Tag 6-11: du  → 500 Therapeuten
```

**Vorteil:** Einfacher zu tracken

## 🔍 Resultate analysieren:

Nach der Kampagne kannst du auswerten:

```python
import pandas as pd
df = pd.read_csv('therapeuten_kampagne.csv')

# Filtere nach Anrede-Typ
sie_gruppe = df[df['anrede_type_used'] == 'sie']
du_gruppe = df[df['anrede_type_used'] == 'du']

# Berechne Response-Rates
sie_responses = (sie_gruppe['responded'] == 'Ja').sum()
du_responses = (du_gruppe['responded'] == 'Ja').sum()

sie_sent = sie_gruppe['email_1_sent_date'].notna().sum()
du_sent = du_gruppe['email_1_sent_date'].notna().sum()

print(f"Sie-Form: {sie_responses}/{sie_sent} = {sie_responses/sie_sent*100:.1f}%")
print(f"Du-Form:  {du_responses}/{du_sent} = {du_responses/du_sent*100:.1f}%")
```

## ⚠️ Wichtig:

1. **Änderung nur VOR dem Versand:** Ändere `anrede_type` nur wenn keine E-Mails gerade versendet werden

2. **Follow-ups sind automatisch konsistent:** Du musst nichts tun - das System verwendet automatisch die richtige Form

3. **CSV-Spalte `anrede_type_used`:** Diese zeigt dir welche Form verwendet wurde:
   - Leer = noch keine E-Mail gesendet
   - "sie" = Person bekommt Sie-Form
   - "du" = Person bekommt Du-Form

## 📝 Beispiel-Workflow:

```bash
# Tag 1 - Sie-Form
# Editiere config.json: "anrede_type": "sie"
python3 run_campaign.py
# → 100 E-Mails mit Sie-Form versendet

# Tag 2 - Du-Form
# Editiere config.json: "anrede_type": "du"
python3 run_campaign.py
# → 100 E-Mails mit Du-Form versendet

# Tag 5 - Follow-ups
# Egal was in config.json steht:
python3 run_campaign.py
# → Follow-ups verwenden automatisch die richtige Form!
```

## ✅ Checkliste:

- [x] Templates für Sie-Form erstellt
- [x] Templates für Du-Form erstellt
- [x] CSV-Spalte `anrede_type_used` hinzugefügt
- [x] System speichert verwendete Anrede automatisch
- [x] Follow-ups verwenden korrekte Anrede
- [x] A/B-Testing kann starten!

Viel Erfolg! 🚀
