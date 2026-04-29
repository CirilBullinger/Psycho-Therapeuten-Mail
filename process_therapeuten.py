import csv
import re

def split_name(full_name):
    """
    Trennt einen vollen Namen in Vorname und Nachname.
    Nimmt an, dass der erste Teil der Vorname und der Rest der Nachname ist.
    """
    parts = full_name.strip().split()
    if len(parts) == 0:
        return "", ""
    elif len(parts) == 1:
        return parts[0], ""
    else:
        # Erster Teil = Vorname, Rest = Nachname
        vorname = parts[0]
        nachname = " ".join(parts[1:])
        return vorname, nachname

def determine_anrede(vorname, nachname):
    """
    Bestimmt die Anrede basierend auf dem Vornamen.
    Versucht das Geschlecht zu erraten (sehr einfache Heuristik).
    """
    # Liste häufiger weiblicher Vornamen-Endungen
    weibliche_endungen = ['a', 'e', 'ie', 'ine', 'ette', 'elle']
    # Liste häufiger männlicher Vornamen
    maennliche_namen = ['lorenzo', 'simon', 'peter', 'max', 'andreas', 'rolf', 'julian', 'giuliano']
    # Liste häufiger weiblicher Vornamen
    weibliche_namen = ['rana', 'ana', 'caroline', 'barbara', 'irina', 'antonia', 'danja', 'johanna',
                       'anke', 'claudia', 'andrea', 'jeanne', 'elisabeth', 'veronika', 'sulamith',
                       'stephanie', 'katarina', 'rahel', 'annina', 'vanesa', 'yvonne', 'stela',
                       'viera', 'petra', 'ellen', 'chloé', 'astrid', 'nadine', 'jennifer',
                       'dorothee', 'florence', 'julia', 'eliana', 'didem', 'silvia', 'fiorenza',
                       'elsa', 'joanna']

    vorname_lower = vorname.lower()

    # Prüfe gegen bekannte Namen
    if vorname_lower in weibliche_namen:
        return f"Geschätzte Frau {nachname}"
    elif vorname_lower in maennliche_namen:
        return f"Geschätzter Herr {nachname}"

    # Fallback: Prüfe Endungen
    for endung in weibliche_endungen:
        if vorname_lower.endswith(endung):
            return f"Geschätzte Frau {nachname}"

    # Standard: männlich
    return f"Geschätzter Herr {nachname}"

def check_deutsch_speaker(sprachen_text):
    """
    Prüft ob 'Deutsch' in der Sprachen-Spalte vorkommt.
    Gibt 'X' zurück wenn ja, sonst ''.
    """
    if not sprachen_text:
        return ""

    # Suche nach "Deutsch" (case-insensitive)
    if re.search(r'\bDeutsch\b', sprachen_text, re.IGNORECASE):
        return "X"
    return ""

def process_csv(input_file, output_file):
    """
    Liest die CSV, fügt neue Spalten hinzu und schreibt sie in eine neue Datei.
    """
    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)

        # Erstelle neue Feldnamen mit den zusätzlichen Spalten
        fieldnames = reader.fieldnames + ['vorname', 'nachname', 'anrede', 'spricht_deutsch']

        rows = []
        for row in reader:
            # Trenne Namen
            vorname, nachname = split_name(row['name'])

            # Bestimme Anrede
            anrede = determine_anrede(vorname, nachname)

            # Prüfe ob Deutsch gesprochen wird
            spricht_deutsch = check_deutsch_speaker(row['sprachen'])

            # Füge neue Felder hinzu
            row['vorname'] = vorname
            row['nachname'] = nachname
            row['anrede'] = anrede
            row['spricht_deutsch'] = spricht_deutsch

            rows.append(row)

    # Schreibe in neue CSV
    with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Verarbeitung abgeschlossen!")
    print(f"Eingabedatei: {input_file}")
    print(f"Ausgabedatei: {output_file}")
    print(f"Anzahl verarbeiteter Datensätze: {len(rows)}")

    # Statistik
    deutsch_sprecher = sum(1 for row in rows if row['spricht_deutsch'] == 'X')
    print(f"Therapeuten die Deutsch sprechen: {deutsch_sprecher}")

if __name__ == "__main__":
    input_file = "therapeuten.csv"
    output_file = "therapeuten_bearbeitet.csv"
    process_csv(input_file, output_file)
