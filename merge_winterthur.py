#!/usr/bin/env python3
"""
Merge Winterthur therapists into the main campaign CSV
"""

import csv
import sys
from datetime import datetime


def normalize_email(email):
    """Normalizes email for comparison"""
    if not email:
        return ""
    return email.strip().lower()


def load_winterthur_therapists():
    """Load the Winterthur CSV file"""
    winterthur_file = '/Users/cirilbullinger/Documents/Code Ablage/Cursör/Mail Adressen/winterthur_therapists_detailed.csv'

    therapists = []
    with open(winterthur_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Skip if no email
            if not row.get('email') and not row.get('profile_email'):
                continue

            # Use profile_email if email is empty
            email = row.get('email') or row.get('profile_email', '')

            if not email:
                continue

            therapists.append({
                'name': row.get('full_name', ''),
                'first_name': row.get('first_name', ''),
                'last_name': row.get('last_name', ''),
                'email': email,
                'phone': row.get('phone', ''),
                'location': row.get('location', ''),
                'address': row.get('full_address', ''),
                'specializations': row.get('specializations', ''),
                'languages': row.get('languages', ''),
            })

    return therapists


def load_campaign_csv():
    """Load the main campaign CSV"""
    campaign_file = 'therapeuten_kampagne.csv'

    with open(campaign_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames

    return rows, fieldnames


def determine_anrede(first_name, last_name):
    """Determine formal greeting (Sie)"""
    if not last_name:
        return f"Guten Tag"
    return f"Geschätzte{'r Herr' if first_name else ' Frau'} {last_name}"


def determine_anrede_du(first_name):
    """Determine informal greeting (Du)"""
    if first_name:
        return f"Hallo {first_name}"
    return "Hallo"


def create_campaign_row(winterthur_therapist, fieldnames):
    """Create a row matching the campaign CSV structure"""
    first_name = winterthur_therapist['first_name'].strip()
    last_name = winterthur_therapist['last_name'].strip()
    email = winterthur_therapist['email'].strip()

    # Create a slug from name
    slug = f"{first_name.lower()}-{last_name.lower()}".replace(' ', '-')

    row = {field: '' for field in fieldnames}

    row['slug'] = slug
    row['name'] = winterthur_therapist['name']
    row['vorname'] = first_name
    row['nachname'] = last_name
    row['email'] = email
    row['telefon'] = winterthur_therapist['phone']
    row['plz_ort'] = winterthur_therapist['location']
    row['strasse'] = winterthur_therapist['address']
    row['angebot'] = winterthur_therapist['specializations']
    row['sprachen'] = winterthur_therapist['languages']

    # Anreden
    row['anrede'] = determine_anrede(first_name, last_name)
    row['anrede_du'] = determine_anrede_du(first_name)
    row['anrede_type_used'] = ''  # Will be set when first email is sent

    # German speaker flag (everyone from Winterthur speaks German)
    row['spricht_deutsch'] = 'X'

    # Campaign tracking (empty = not sent yet)
    row['email_1_sent_date'] = ''
    row['email_2_sent_date'] = ''
    row['email_3_sent_date'] = ''
    row['responded'] = ''
    row['responded_date'] = ''
    row['notes'] = 'Aus Winterthur-Liste'

    return row


def merge_lists():
    """Main function to merge the lists"""
    print("=" * 70)
    print("  WINTERTHUR THERAPEUTEN ZUSAMMENFÜHREN")
    print("=" * 70)
    print()

    # Load both files
    print("📂 Lade Winterthur Therapeuten...")
    winterthur = load_winterthur_therapists()
    print(f"   ✅ {len(winterthur)} Therapeuten geladen")

    print("\n📂 Lade bestehende Kampagnen-CSV...")
    campaign_rows, fieldnames = load_campaign_csv()
    print(f"   ✅ {len(campaign_rows)} Therapeuten in Kampagne")

    # Build set of existing emails
    existing_emails = {normalize_email(row['email']) for row in campaign_rows}
    print(f"\n🔍 {len(existing_emails)} eindeutige E-Mails in Kampagne")

    # Find new therapists
    new_therapists = []
    duplicates = 0

    for therapist in winterthur:
        norm_email = normalize_email(therapist['email'])
        if norm_email and norm_email not in existing_emails:
            new_therapists.append(therapist)
            existing_emails.add(norm_email)
        else:
            duplicates += 1

    print(f"\n📊 Ergebnis:")
    print(f"   • Neue Therapeuten: {len(new_therapists)}")
    print(f"   • Duplikate (übersprungen): {duplicates}")

    if len(new_therapists) == 0:
        print("\n✅ Keine neuen Therapeuten zum Hinzufügen!")
        return

    # Add new therapists to campaign
    print(f"\n➕ Füge {len(new_therapists)} neue Therapeuten hinzu...")

    for therapist in new_therapists:
        new_row = create_campaign_row(therapist, fieldnames)
        campaign_rows.append(new_row)
        print(f"   ✅ {therapist['name']} ({therapist['email']})")

    # Save updated CSV
    print(f"\n💾 Speichere aktualisierte CSV...")
    with open('therapeuten_kampagne.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(campaign_rows)

    print(f"   ✅ Gespeichert!")

    print("\n" + "=" * 70)
    print("  ZUSAMMENFASSUNG")
    print("=" * 70)
    print(f"  Vorher:      {len(campaign_rows) - len(new_therapists)} Therapeuten")
    print(f"  Hinzugefügt: {len(new_therapists)} Therapeuten")
    print(f"  Nachher:     {len(campaign_rows)} Therapeuten")
    print("=" * 70)
    print()


if __name__ == '__main__':
    try:
        merge_lists()
    except Exception as e:
        print(f"\n❌ FEHLER: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
