#!/usr/bin/env python3
"""
Fügt eine Du-Anrede hinzu für A/B-Testing
"""

import csv


def create_du_anrede(vorname, nachname):
    """
    Erstellt eine Du-Anrede basierend auf Vorname und Nachname.
    Format: "Geschätzter Ciril" oder "Geschätzte Anna"
    """
    # Liste häufiger weiblicher Vornamen
    weibliche_namen = ['rana', 'ana', 'caroline', 'barbara', 'irina', 'antonia', 'danja', 'johanna',
                       'anke', 'claudia', 'andrea', 'jeanne', 'elisabeth', 'veronika', 'sulamith',
                       'stephanie', 'katarina', 'rahel', 'annina', 'vanesa', 'yvonne', 'stela',
                       'viera', 'petra', 'ellen', 'chloé', 'astrid', 'nadine', 'jennifer',
                       'dorothee', 'florence', 'julia', 'eliana', 'didem', 'silvia', 'fiorenza',
                       'elsa', 'joanna']

    # Liste häufiger männlicher Vornamen
    maennliche_namen = ['lorenzo', 'simon', 'peter', 'max', 'andreas', 'rolf', 'julian', 'giuliano']

    # Liste häufiger weiblicher Vornamen-Endungen
    weibliche_endungen = ['a', 'e', 'ie', 'ine', 'ette', 'elle']

    vorname_lower = vorname.lower()

    # Prüfe gegen bekannte Namen
    if vorname_lower in weibliche_namen:
        return f"Geschätzte {vorname}"
    elif vorname_lower in maennliche_namen:
        return f"Geschätzter {vorname}"

    # Fallback: Prüfe Endungen
    for endung in weibliche_endungen:
        if vorname_lower.endswith(endung):
            return f"Geschätzte {vorname}"

    # Standard: männlich
    return f"Geschätzter {vorname}"


def add_du_anrede(csv_file):
    """
    Fügt eine neue Spalte 'anrede_du' zur CSV hinzu
    """
    # Lade CSV
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        rows = list(reader)

    # Füge neue Spalte hinzu (direkt nach 'anrede')
    anrede_index = fieldnames.index('anrede')
    fieldnames.insert(anrede_index + 1, 'anrede_du')

    # Erstelle Du-Anrede für jeden Therapeuten
    for row in rows:
        vorname = row['vorname']
        nachname = row['nachname']
        row['anrede_du'] = create_du_anrede(vorname, nachname)

    # Speichere CSV
    with open(csv_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Du-Anrede hinzugefügt!")
    print(f"   CSV aktualisiert: {csv_file}")
    print(f"   Neue Spalte: 'anrede_du'")
    print(f"\nBeispiele:")
    for i, row in enumerate(rows[:10], 1):
        print(f"{i}. {row['name']}")
        print(f"   Sie: {row['anrede']}")
        print(f"   Du:  {row['anrede_du']}")
        print()


if __name__ == "__main__":
    csv_file = "therapeuten_kampagne.csv"
    add_du_anrede(csv_file)
