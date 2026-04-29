# A/B-Testing: Sie vs. Du

## Übersicht

Das System unterstützt jetzt A/B-Testing zwischen zwei Anrede-Varianten:

### **Variante A: Sie-Form** (Formal)
- "Geschätzter Herr Müller"
- "Geschätzte Frau Schmidt"

### **Variante B: Du-Form** (Persönlich)
- "Geschätzter Max"
- "Geschätzte Anna"

## Wie funktioniert es?

Die CSV enthält jetzt **zwei Anrede-Spalten**:
- `anrede` - Sie-Form (z.B. "Geschätzter Herr Pezzoli")
- `anrede_du` - Du-Form (z.B. "Geschätzter Lorenzo")

## Anrede-Variante wählen

In der `config.json` kannst du festlegen welche Anrede verwendet wird:

```json
"campaign": {
  ...
  "anrede_type": "sie"    // oder "du"
}
```

### **Option 1: Sie-Form verwenden**
```json
"anrede_type": "sie"
```

### **Option 2: Du-Form verwenden**
```json
"anrede_type": "du"
```

## A/B-Test durchführen

### **Methode 1: Sequentiell (Empfohlen)**

**Schritt 1:** Erste Hälfte mit Sie-Form
```json
"anrede_type": "sie"
"daily_limit": 50
```
Führe Kampagne aus für ~10 Tage (ca. 500 Therapeuten)

**Schritt 2:** Zweite Hälfte mit Du-Form
```json
"anrede_type": "du"
"daily_limit": 50
```
Führe Kampagne aus für weitere ~10 Tage (ca. 500 Therapeuten)

**Schritt 3:** Resultate vergleichen
- Welche Gruppe hat höhere Response-Rate?
- Markiere in CSV eine neue Spalte `test_group` (A oder B)

### **Methode 2: Alternierend**

Tag 1: Sie-Form (100 E-Mails)
Tag 2: Du-Form (100 E-Mails)
Tag 3: Sie-Form (100 E-Mails)
Tag 4: Du-Form (100 E-Mails)
...

Wechsle `anrede_type` täglich in `config.json`

## Resultate tracken

### Empfohlenes Vorgehen:

1. **Vor dem Test:** Füge eine Spalte `test_group` zur CSV hinzu
   - Markiere erste 500: "A_sie"
   - Markiere zweite 500: "B_du"

2. **Nach dem Test:** Analysiere Response-Rates

```python
import pandas as pd
df = pd.read_csv('therapeuten_kampagne.csv')

# Filter nach Test-Gruppen
gruppe_a = df[df['test_group'] == 'A_sie']
gruppe_b = df[df['test_group'] == 'B_du']

# Response-Rates berechnen
response_a = (gruppe_a['responded'] == 'Ja').sum()
response_b = (gruppe_b['responded'] == 'Ja').sum()

sent_a = gruppe_a['email_1_sent_date'].notna().sum()
sent_b = gruppe_b['email_1_sent_date'].notna().sum()

rate_a = response_a / sent_a * 100
rate_b = response_b / sent_b * 100

print(f"Gruppe A (Sie): {rate_a:.1f}% Response-Rate")
print(f"Gruppe B (Du):  {rate_b:.1f}% Response-Rate")
```

## Beispiel-Vergleich

### E-Mail mit Sie-Form:
```
Geschätzter Herr Müller,

ich bin auf Ihr Profil auf psychologie.ch gestossen...
```

### E-Mail mit Du-Form:
```
Geschätzter Max,

ich bin auf Ihr Profil auf psychologie.ch gestossen...
```

**Hinweis:** Der Rest der E-Mail bleibt gleich (weiterhin "Sie" im Text). Nur die Anrede ändert sich.

## Empfehlung

Für professionelle Therapeuten würde ich **mit Sie-Form starten**:
- Sicherer bei formeller Zielgruppe
- Geringeres Risiko negativ wahrgenommen zu werden

Wenn Sie-Form gut funktioniert, kannst du Du-Form als Test ausprobieren.

## Schnell-Wechsel

Um schnell zwischen Sie/Du zu wechseln:

```bash
# Sie-Form aktivieren
# In config.json ändern: "anrede_type": "sie"
python3 send_campaign.py

# Du-Form aktivieren
# In config.json ändern: "anrede_type": "du"
python3 send_campaign.py
```

Kein Neustart nötig - einfach config.json editieren!
