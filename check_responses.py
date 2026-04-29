#!/usr/bin/env python3
"""
Response-Tracking-System
Prüft E-Mail-Postfach auf Antworten und aktualisiert CSV
"""

import csv
import json
import imaplib
import email
from email.header import decode_header
from datetime import datetime


class ResponseTracker:
    def __init__(self, config_file='config.json'):
        """Initialisiert das Response-Tracking"""
        self.config = self.load_config(config_file)
        self.log_file = self.config['logging']['log_file']

    def load_config(self, config_file):
        """Lädt die Konfiguration aus JSON"""
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def log(self, message):
        """Schreibt Log-Nachricht in Datei und Konsole"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)

        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')

    def connect_to_imap(self):
        """Verbindet sich mit IMAP-Server"""
        try:
            # Verbindung zum IMAP-Server
            mail = imaplib.IMAP4_SSL(
                self.config['email']['imap_server'],
                self.config['email']['imap_port']
            )

            # Login
            mail.login(
                self.config['email']['username'],
                self.config['email']['password']
            )

            self.log("✅ Erfolgreich mit IMAP verbunden")
            return mail

        except Exception as e:
            self.log(f"❌ FEHLER bei IMAP-Verbindung: {str(e)}")
            return None

    def get_sender_email(self, from_header):
        """Extrahiert E-Mail-Adresse aus From-Header"""
        # Format: "Name <email@example.com>" oder "email@example.com"
        if '<' in from_header and '>' in from_header:
            start = from_header.index('<') + 1
            end = from_header.index('>')
            return from_header[start:end].strip().lower()
        return from_header.strip().lower()

    def check_for_responses(self, days_back=30):
        """Prüft Postfach auf Antworten"""
        mail = self.connect_to_imap()
        if not mail:
            return []

        responses = []

        try:
            # Wähle Posteingang
            mail.select('INBOX')

            # Suche nach E-Mails der letzten X Tage
            from datetime import datetime, timedelta
            since_date = (datetime.now() - timedelta(days=days_back)).strftime('%d-%b-%Y')

            # Suche nach allen E-Mails seit dem Datum
            status, messages = mail.search(None, f'SINCE {since_date}')

            if status != 'OK':
                self.log("Keine Nachrichten gefunden")
                return responses

            # IDs der E-Mails
            email_ids = messages[0].split()
            self.log(f"Gefundene E-Mails der letzten {days_back} Tage: {len(email_ids)}")

            for email_id in email_ids:
                try:
                    # Hole E-Mail
                    status, msg_data = mail.fetch(email_id, '(RFC822)')

                    if status != 'OK':
                        continue

                    # Parse E-Mail
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)

                    # Extrahiere Absender
                    from_header = msg.get('From', '')
                    sender_email = self.get_sender_email(from_header)

                    # Extrahiere Datum
                    date_header = msg.get('Date', '')

                    responses.append({
                        'from': sender_email,
                        'date': date_header,
                        'subject': msg.get('Subject', '')
                    })

                except Exception as e:
                    self.log(f"⚠️  Fehler beim Verarbeiten einer E-Mail: {str(e)}")
                    continue

            mail.close()
            mail.logout()

        except Exception as e:
            self.log(f"❌ FEHLER beim Abrufen der E-Mails: {str(e)}")

        return responses

    def load_csv(self):
        """Lädt CSV-Datei"""
        csv_file = self.config['campaign']['csv_file']
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader), reader.fieldnames

    def save_csv(self, rows, fieldnames):
        """Speichert aktualisierte CSV-Datei"""
        csv_file = self.config['campaign']['csv_file']
        with open(csv_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def run(self):
        """Führt Response-Tracking aus"""
        self.log("=" * 70)
        self.log("Response-Tracking gestartet")
        self.log("=" * 70)

        # Prüfe Postfach
        responses = self.check_for_responses(days_back=30)
        self.log(f"Insgesamt {len(responses)} E-Mails im Posteingang gefunden")

        # Erstelle Set mit allen E-Mail-Adressen die geantwortet haben
        responder_emails = set(r['from'] for r in responses)
        self.log(f"Unique Absender: {len(responder_emails)}")

        # Lade CSV
        rows, fieldnames = self.load_csv()

        # Aktualisiere CSV
        updated_count = 0
        for row in rows:
            therapeut_email = row['email'].strip().lower()

            # Hat dieser Therapeut geantwortet?
            if therapeut_email in responder_emails and row['responded'] != 'Ja':
                row['responded'] = 'Ja'
                row['responded_date'] = datetime.now().strftime('%Y-%m-%d')
                updated_count += 1
                self.log(f"✅ Antwort markiert: {row['name']} ({therapeut_email})")

        # Speichere CSV
        if updated_count > 0:
            self.save_csv(rows, fieldnames)
            self.log(f"\n✅ CSV aktualisiert: {updated_count} neue Antworten markiert")
        else:
            self.log("\nℹ️  Keine neuen Antworten gefunden")

        self.log("=" * 70)
        self.log("Response-Tracking abgeschlossen")
        self.log("=" * 70)


def main():
    tracker = ResponseTracker()
    tracker.run()


if __name__ == '__main__':
    main()
