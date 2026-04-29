import csv
from datetime import datetime

def prepare_campaign_csv(input_file, output_file):
    """
    Erweitert die CSV-Datei um Tracking-Spalten für die E-Mail-Kampagne.
    """

    # Neue Spalten für das Tracking
    new_columns = [
        'email_1_sent_date',
        'email_2_sent_date',
        'email_3_sent_date',
        'responded',
        'responded_date',
        'notes'
    ]

    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)

        # Erweitere Feldnamen
        fieldnames = list(reader.fieldnames) + new_columns

        rows = []
        for row in reader:
            # Initialisiere neue Felder mit leeren Werten
            for col in new_columns:
                row[col] = ''
            rows.append(row)

    # Schreibe erweiterte CSV
    with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Kampagnen-CSV erstellt: {output_file}")
    print(f"   Anzahl Therapeuten: {len(rows)}")
    print(f"   Neue Spalten hinzugefügt: {', '.join(new_columns)}")

if __name__ == "__main__":
    input_file = "therapeuten_bearbeitet.csv"
    output_file = "therapeuten_kampagne.csv"

    prepare_campaign_csv(input_file, output_file)
