import csv

def analyze_therapeuten(csv_file):
    """
    Analysiert Therapeuten nach verschiedenen Kriterien:
    - Nimmt neue Patienten auf
    - Bietet Online-Beratung an
    - Spricht Deutsch
    """

    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        total = 0
        nimmt_neue_patienten = 0
        online_verfuegbar = 0
        spricht_deutsch = 0
        alle_drei_kriterien = 0

        therapeuten_liste = []

        for row in reader:
            total += 1

            # Prüfe ob neue Patienten aufgenommen werden
            # "Keine neuen Kunden" bedeutet NICHT verfügbar
            verfuegbarkeit = row['verfuegbarkeit']
            neue_patienten = verfuegbarkeit != "Keine neuen Kunden"

            # Prüfe ob Online-Beratung verfügbar ist
            online = row['online_beratung'] == "Verfügbar"

            # Prüfe ob Deutsch gesprochen wird
            deutsch = row['spricht_deutsch'] == "X"

            if neue_patienten:
                nimmt_neue_patienten += 1

            if online:
                online_verfuegbar += 1

            if deutsch:
                spricht_deutsch += 1

            # Alle drei Kriterien erfüllt?
            if neue_patienten and online and deutsch:
                alle_drei_kriterien += 1
                therapeuten_liste.append({
                    'name': row['name'],
                    'email': row['email'],
                    'telefon': row['telefon'],
                    'plz_ort': row['plz_ort'],
                    'verfuegbarkeit': row['verfuegbarkeit'],
                    'anrede': row['anrede']
                })

        print("=" * 70)
        print("ANALYSE DER THERAPEUTEN")
        print("=" * 70)
        print(f"\nGesamtanzahl Therapeuten: {total}")
        print(f"\nTherapeuten die neue Patienten aufnehmen: {nimmt_neue_patienten} ({nimmt_neue_patienten/total*100:.1f}%)")
        print(f"Therapeuten die Online-Beratung anbieten: {online_verfuegbar} ({online_verfuegbar/total*100:.1f}%)")
        print(f"Therapeuten die Deutsch sprechen: {spricht_deutsch} ({spricht_deutsch/total*100:.1f}%)")
        print("\n" + "=" * 70)
        print(f"THERAPEUTEN MIT ALLEN 3 KRITERIEN:")
        print(f"(Neue Patienten + Online + Deutsch)")
        print("=" * 70)
        print(f"\nAnzahl: {alle_drei_kriterien} ({alle_drei_kriterien/total*100:.1f}%)")

        # Zeige erste 10 Beispiele
        print("\nErste 10 Beispiele:")
        print("-" * 70)
        for i, therapeut in enumerate(therapeuten_liste[:10], 1):
            print(f"\n{i}. {therapeut['name']}")
            print(f"   Anrede: {therapeut['anrede']}")
            print(f"   Ort: {therapeut['plz_ort']}")
            print(f"   Verfügbarkeit: {therapeut['verfuegbarkeit']}")
            print(f"   Email: {therapeut['email']}")
            print(f"   Telefon: {therapeut['telefon']}")

        if alle_drei_kriterien > 10:
            print(f"\n... und {alle_drei_kriterien - 10} weitere")

        return alle_drei_kriterien, therapeuten_liste

if __name__ == "__main__":
    csv_file = "therapeuten_bearbeitet.csv"
    anzahl, liste = analyze_therapeuten(csv_file)

    # Optional: Speichere gefilterte Liste
    if anzahl > 0:
        with open("therapeuten_gefiltert.csv", 'w', encoding='utf-8', newline='') as outfile:
            if liste:
                fieldnames = ['name', 'anrede', 'email', 'telefon', 'plz_ort', 'verfuegbarkeit']
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(liste)
        print(f"\n\nGefilterte Liste gespeichert in: therapeuten_gefiltert.csv")
