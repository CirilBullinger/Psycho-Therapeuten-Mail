#!/usr/bin/env python3
"""
E-Mail-Kampagnen-System für Therapeuten-Rekrutierung
Versendet personalisierte E-Mails mit Rate-Limiting und Tracking
"""

import csv
import json
import smtplib
import imaplib
import ssl
import time
import random
import email.utils
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from pathlib import Path


class EmailCampaign:
    def __init__(self, config_file='config.json', dry_run=False):
        """Initialisiert die E-Mail-Kampagne"""
        self.dry_run = dry_run
        self.config = self.load_config(config_file)
        self.log_file = self.config['logging']['log_file']
        self.sent_count = 0

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

    def load_template(self, template_file):
        """Lädt Text-Template"""
        with open(template_file, 'r', encoding='utf-8') as f:
            return f.read()

    def personalize_email(self, template, anrede):
        """Ersetzt Platzhalter im Template"""
        return template.replace('{{ANREDE}}', anrede)

    def personalize_subject(self, subject, vorname, nachname):
        """Ersetzt Platzhalter im Betreff"""
        subject = subject.replace('{{VORNAME}}', vorname)
        subject = subject.replace('{{NACHNAME}}', nachname)
        return subject

    def save_to_sent_folder(self, msg):
        """Speichert E-Mail im Gesendet-Ordner via IMAP"""
        try:
            # Verbindung zu IMAP
            mail = imaplib.IMAP4_SSL(
                self.config['email']['imap_server'],
                self.config['email']['imap_port']
            )
            mail.login(
                self.config['email']['username'],
                self.config['email']['password']
            )

            # Speichere in Sent/Gesendet Ordner
            # Verschiedene Provider nutzen unterschiedliche Namen
            sent_folders = ['Sent', 'INBOX.Sent', 'Sent Messages', 'Gesendet']

            for folder in sent_folders:
                try:
                    mail.append(folder, '\\Seen', imaplib.Time2Internaldate(time.time()), msg.as_bytes())
                    mail.logout()
                    return True
                except:
                    continue

            mail.logout()
            return False

        except Exception as e:
            self.log(f"⚠️  Konnte E-Mail nicht in Gesendet speichern: {str(e)}")
            return False

    def send_email(self, to_email, subject, text_content):
        """Versendet eine einzelne E-Mail"""
        if self.dry_run:
            self.log(f"[DRY-RUN] Würde E-Mail senden an: {to_email}")
            self.log(f"[DRY-RUN] Betreff: {subject}")
            return True

        try:
            # E-Mail erstellen (Plain Text)
            msg = MIMEText(text_content, 'plain', 'utf-8')
            msg['Subject'] = subject
            msg['From'] = f"{self.config['email']['from_name']} <{self.config['email']['from_email']}>"
            msg['To'] = to_email
            msg['Date'] = email.utils.formatdate(localtime=True)

            # SSL-Kontext erstellen (ohne Zertifikats-Verifikation für Hostpoint)
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            # Verbindung zu SMTP-Server (Port 465 = SSL)
            with smtplib.SMTP_SSL(
                self.config['email']['smtp_server'],
                self.config['email']['smtp_port'],
                context=context
            ) as server:
                server.login(
                    self.config['email']['username'],
                    self.config['email']['password']
                )
                server.send_message(msg)

            # Speichere in Gesendet-Ordner
            self.save_to_sent_folder(msg)

            self.log(f"✅ E-Mail gesendet an: {to_email} - Betreff: {subject}")
            return True

        except Exception as e:
            self.log(f"❌ FEHLER beim Senden an {to_email}: {str(e)}")
            return False

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

    def should_send_email_1(self, row):
        """Prüft ob E-Mail 1 gesendet werden soll"""
        # Noch nicht gesendet und hat nicht geantwortet
        # UND spricht Deutsch (wenn prioritize_deutsch aktiviert)
        if self.config['campaign'].get('prioritize_deutsch', True):
            return (row['email_1_sent_date'] == '' and
                    row['responded'] != 'Ja' and
                    row['spricht_deutsch'] == 'X')
        else:
            return row['email_1_sent_date'] == '' and row['responded'] != 'Ja'

    def should_send_email_2(self, row):
        """Prüft ob E-Mail 2 gesendet werden soll"""
        # E-Mail 1 wurde gesendet, aber E-Mail 2 noch nicht
        if row['email_1_sent_date'] == '' or row['email_2_sent_date'] != '':
            return False

        # Hat nicht geantwortet
        if row['responded'] == 'Ja':
            return False

        # Genug Tage vergangen seit E-Mail 1?
        try:
            sent_date = datetime.strptime(row['email_1_sent_date'], '%Y-%m-%d')
            days_since = (datetime.now() - sent_date).days
            return days_since >= self.config['campaign']['days_between_email_1_and_2']
        except:
            return False

    def should_send_email_3(self, row):
        """Prüft ob E-Mail 3 gesendet werden soll"""
        # E-Mail 2 wurde gesendet, aber E-Mail 3 noch nicht
        if row['email_2_sent_date'] == '' or row['email_3_sent_date'] != '':
            return False

        # Hat nicht geantwortet
        if row['responded'] == 'Ja':
            return False

        # Genug Tage vergangen seit E-Mail 2?
        try:
            sent_date = datetime.strptime(row['email_2_sent_date'], '%Y-%m-%d')
            days_since = (datetime.now() - sent_date).days
            return days_since >= self.config['campaign']['days_between_email_2_and_3']
        except:
            return False

    def run_response_tracking(self):
        """Führt Response-Tracking vor dem Versand aus"""
        self.log("\n" + "=" * 70)
        self.log("SCHRITT 1: RESPONSE-TRACKING")
        self.log("=" * 70)

        try:
            import subprocess
            import sys

            result = subprocess.run(
                [sys.executable, 'check_responses.py'],
                capture_output=True,
                text=True,
                check=True
            )

            # Zeige Output vom Response-Tracking
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    print(line)

            self.log("✅ Response-Tracking abgeschlossen")
            return True

        except subprocess.CalledProcessError as e:
            self.log(f"⚠️  Response-Tracking hatte Fehler, mache trotzdem weiter...")
            return False
        except Exception as e:
            self.log(f"⚠️  Response-Tracking Fehler: {str(e)}")
            return False

    def run(self):
        """Führt die Kampagne aus"""
        self.log("=" * 70)
        self.log(f"E-Mail-Kampagne gestartet {'(DRY-RUN MODE)' if self.dry_run else ''}")
        self.log("=" * 70)

        # WICHTIG: Response-Tracking ZUERST ausführen
        if not self.dry_run:
            self.run_response_tracking()

        self.log("\n" + "=" * 70)
        self.log("SCHRITT 2: E-MAIL-VERSAND")
        self.log("=" * 70)

        # Lade CSV
        rows, fieldnames = self.load_csv()
        total_therapeuten = len(rows)

        self.log(f"Gesamtanzahl Therapeuten in CSV: {total_therapeuten}")

        # Zähle wer welche E-Mail bekommen soll
        to_send_1 = sum(1 for row in rows if self.should_send_email_1(row))
        to_send_2 = sum(1 for row in rows if self.should_send_email_2(row))
        to_send_3 = sum(1 for row in rows if self.should_send_email_3(row))

        self.log(f"Bereit für E-Mail 1: {to_send_1}")
        self.log(f"Bereit für E-Mail 2: {to_send_2}")
        self.log(f"Bereit für E-Mail 3: {to_send_3}")
        self.log(f"Tageslimit: {self.config['campaign']['daily_limit']}")

        # Templates werden dynamisch pro Person geladen basierend auf ihrer anrede_type_used
        # (siehe unten im Loop)

        self.log("\nStarte Versand...")
        self.log("-" * 70)

        # Versende E-Mails
        for row in rows:
            # Tageslimit erreicht?
            if self.sent_count >= self.config['campaign']['daily_limit']:
                self.log(f"\n⚠️  Tageslimit von {self.config['campaign']['daily_limit']} E-Mails erreicht!")
                break

            # Bestimme welche E-Mail gesendet werden soll
            email_to_send = None
            subject = None
            date_field = None

            if self.should_send_email_3(row):
                email_to_send = 3
                subject = self.config['templates']['email_3_subject']
                date_field = 'email_3_sent_date'
            elif self.should_send_email_2(row):
                email_to_send = 2
                subject = self.config['templates']['email_2_subject']
                date_field = 'email_2_sent_date'
            elif self.should_send_email_1(row):
                email_to_send = 1
                subject = self.config['templates']['email_1_subject']
                date_field = 'email_1_sent_date'

            if email_to_send:
                # Wähle Anrede basierend auf Config ODER bereits verwendete Anrede
                # Wenn bereits eine Anrede verwendet wurde (E-Mail 1), nutze diese auch für E-Mail 2+3
                if row.get('anrede_type_used'):
                    # Verwende die bereits gespeicherte Anrede-Form
                    anrede_type = row['anrede_type_used']
                else:
                    # Erste E-Mail: Nutze Config-Einstellung
                    anrede_type = self.config['campaign'].get('anrede_type', 'sie')

                # Lade das passende Template basierend auf anrede_type
                template_key = f'email_{email_to_send}_template_{anrede_type}'
                template = self.load_template(self.config['templates'][template_key])

                # Wähle passende Anrede
                if anrede_type == 'du':
                    anrede = row['anrede_du']
                else:
                    anrede = row['anrede']

                # Personalisiere Betreff
                personalized_subject = self.personalize_subject(
                    subject,
                    row['vorname'],
                    row['nachname']
                )

                # Personalisiere E-Mail
                text_content = self.personalize_email(template, anrede)

                # Versende E-Mail
                success = self.send_email(row['email'], personalized_subject, text_content)

                if success:
                    # Aktualisiere CSV
                    row[date_field] = datetime.now().strftime('%Y-%m-%d')

                    # Speichere verwendete Anrede-Form (nur bei E-Mail 1)
                    if email_to_send == 1 and not row.get('anrede_type_used'):
                        row['anrede_type_used'] = anrede_type

                    self.sent_count += 1

                    # Verzögerung zwischen E-Mails (zufällig)
                    if self.sent_count < self.config['campaign']['daily_limit']:
                        delay = random.randint(
                            self.config['campaign']['delay_min_seconds'],
                            self.config['campaign']['delay_max_seconds']
                        )
                        if not self.dry_run:
                            time.sleep(delay)

        # Speichere aktualisierte CSV
        if not self.dry_run:
            self.save_csv(rows, fieldnames)
            self.log(f"\n✅ CSV aktualisiert: {self.config['campaign']['csv_file']}")

        # Zusammenfassung
        self.log("\n" + "=" * 70)
        self.log(f"KAMPAGNE ABGESCHLOSSEN")
        self.log("=" * 70)
        self.log(f"Gesendete E-Mails: {self.sent_count}")
        self.log(f"Verbleibende E-Mails heute: {self.config['campaign']['daily_limit'] - self.sent_count}")
        self.log("=" * 70)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='E-Mail-Kampagne für Therapeuten')
    parser.add_argument('--dry-run', action='store_true', help='Test-Modus ohne echten Versand')
    args = parser.parse_args()

    campaign = EmailCampaign(dry_run=args.dry_run)
    campaign.run()


if __name__ == '__main__':
    main()
