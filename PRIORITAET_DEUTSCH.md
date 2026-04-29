# 🎯 Priorität: Deutsch sprechende Therapeuten

## Aktuelle Einstellung:

Das System ist so konfiguriert, dass **zuerst alle deutschsprachigen Therapeuten** angeschrieben werden.

## 📊 Zahlen:

- **Gesamt:** 5.916 Therapeuten in der CSV
- **Deutsch:** 3.328 Therapeuten (56%)
- **Andere:** 2.588 Therapeuten (44%)

## ⚙️ Wie es funktioniert:

In `config.json`:
```json
"prioritize_deutsch": true
```

### **Phase 1: Nur Deutsch** (Aktuell aktiv ✅)
- System sendet E-Mails NUR an Therapeuten mit `spricht_deutsch = X`
- Ca. **34 Tage** bei 100 E-Mails/Tag (3.328 Therapeuten)

### **Phase 2: Alle anderen** (Nach manueller Umstellung)
Wenn alle deutschsprachigen Therapeuten angeschrieben wurden:

**Ändern in `config.json`:**
```json
"prioritize_deutsch": false
```

Dann werden auch die anderen 2.588 Therapeuten angeschrieben.

## 🔍 Status prüfen:

Um zu sehen wie viele deutschsprachige Therapeuten noch übrig sind:

```python
import pandas as pd
df = pd.read_csv('therapeuten_kampagne.csv')

# Deutschsprachige, noch nicht angeschrieben
deutsch_offen = df[(df['spricht_deutsch'] == 'X') &
                   (df['email_1_sent_date'] == '')]
print(f"Noch {len(deutsch_offen)} deutschsprachige Therapeuten übrig")

# Wenn 0, dann zu Phase 2 wechseln!
```

## 📅 Zeitplan (ca.):

```
Tag 1-34:   Deutschsprachige Therapeuten (3.328)
            → "prioritize_deutsch": true

Tag 35-60:  Andere Therapeuten (2.588)
            → "prioritize_deutsch": false
```

## ✅ Vorteile dieser Methode:

- ✅ Alle 5.916 Therapeuten bleiben in einer CSV
- ✅ Deutschsprachige werden priorisiert
- ✅ Du entscheidest wann du zur nächsten Phase wechselst
- ✅ Einfacher Wechsel durch Config-Änderung

## 🚨 Wichtig:

Das System zeigt dir im Log wie viele E-Mails bereit sind:
```
Bereit für E-Mail 1: 3328
```

Wenn diese Zahl auf **0** fällt (bei aktiver Deutsch-Priorisierung), dann sind alle deutschsprachigen Therapeuten angeschrieben!

→ Dann änderst du `"prioritize_deutsch": false` und die anderen werden angeschrieben.

## 🔄 Manueller Wechsel:

```bash
# 1. Editiere config.json
# Ändere: "prioritize_deutsch": false

# 2. Starte Kampagne wie gewohnt
python3 run_campaign.py
```

Fertig! 🎉
