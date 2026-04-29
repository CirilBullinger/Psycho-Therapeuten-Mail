#!/usr/bin/env python3
"""
Fügt eine Tracking-Spalte hinzu für verwendete Anrede-Form
"""

import csv


def add_anrede_tracking(csv_file):
    """
    Fügt eine neue Spalte 'anrede_type_used' zur CSV hinzu
    Diese speichert ob "sie" oder "du" verwendet wurde
    """
    # Lade CSV
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        rows = list(reader)

    # Füge neue Spalte hinzu (direkt nach 'anrede_du')
    if 'anrede_type_used' not in fieldnames:
        anrede_du_index = fieldnames.index('anrede_du')
        fieldnames.insert(anrede_du_index + 1, 'anrede_type_used')

        # Initialisiere mit leerem Wert
        for row in rows:
            row['anrede_type_used'] = ''

    # Speichere CSV
    with open(csv_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Anrede-Tracking hinzugefügt!")
    print(f"   CSV aktualisiert: {csv_file}")
    print(f"   Neue Spalte: 'anrede_type_used'")
    print(f"\nDiese Spalte speichert welche Anrede verwendet wurde:")
    print(f"   - 'sie' = Person bekommt alle E-Mails mit Sie-Form")
    print(f"   - 'du'  = Person bekommt alle E-Mails mit Du-Form")


if __name__ == "__main__":
    csv_file = "therapeuten_kampagne.csv"
    add_anrede_tracking(csv_file)
