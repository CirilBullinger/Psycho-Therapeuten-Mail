#!/usr/bin/env python3
"""
Direkter Test-Versand ohne Interaktion
"""

import json
import smtplib
import ssl
from email.mime.text import MIMEText


def load_config(config_file='config.json'):
    """Lädt die Konfiguration"""
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_template(template_file):
    """Lädt Text-Template"""
    with open(template_file, 'r', encoding='utf-8') as f:
        return f.read()


def send_all_tests(test_recipient):
    """Sendet alle drei Test-E-Mails"""
    print("=" * 70)
    print("E-MAIL TEST-VERSAND")
    print("=" * 70)

    # Lade Config
    config = load_config()

    print(f"\nEmpfänger: {test_recipient}")
    print("\n📧 Sende alle 3 Test-E-Mails...\n")

    # Lade alle drei Templates
    templates = [
        {
            'name': 'E-Mail 1 (Erste Kontaktaufnahme)',
            'subject': config['templates']['email_1_subject'],
            'file': config['templates']['email_1_template']
        },
        {
            'name': 'E-Mail 2 (Follow-up)',
            'subject': config['templates']['email_2_subject'],
            'file': config['templates']['email_2_template']
        },
        {
            'name': 'E-Mail 3 (Letzter Reminder)',
            'subject': config['templates']['email_3_subject'],
            'file': config['templates']['email_3_template']
        }
    ]

    # Test-Daten
    test_anrede = "Geschätzte Frau Musterfrau"
    test_vorname = "Anna"
    test_nachname = "Musterfrau"

    # Sende E-Mails
    success_count = 0
    for i, template_info in enumerate(templates, 1):
        # Personalisiere Betreff
        subject = template_info['subject']
        subject = subject.replace('{{VORNAME}}', test_vorname)
        subject = subject.replace('{{NACHNAME}}', test_nachname)

        print(f"📨 {i}/3 - Versende: {template_info['name']}")
        print(f"    Betreff: {subject}")

        # Lade Template
        template = load_template(template_info['file'])

        # Personalisiere
        text_content = template.replace('{{ANREDE}}', test_anrede)

        try:
            # E-Mail erstellen (Plain Text)
            msg = MIMEText(text_content, 'plain', 'utf-8')
            msg['Subject'] = f"[TEST {i}/3] {subject}"
            msg['From'] = f"{config['email']['from_name']} <{config['email']['from_email']}>"
            msg['To'] = test_recipient

            # SSL-Kontext (ohne Zertifikats-Verifikation für Hostpoint)
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            # Verbindung zu SMTP-Server
            with smtplib.SMTP_SSL(
                config['email']['smtp_server'],
                config['email']['smtp_port'],
                context=context
            ) as server:
                server.login(
                    config['email']['username'],
                    config['email']['password']
                )
                server.send_message(msg)

            print(f"    ✅ Erfolgreich gesendet!\n")
            success_count += 1

        except Exception as e:
            print(f"    ❌ FEHLER: {str(e)}\n")

    print("=" * 70)
    print(f"Test abgeschlossen! {success_count}/3 E-Mails erfolgreich gesendet.")
    print("=" * 70)
    print(f"\n📬 Prüfe dein Postfach: {test_recipient}")
    print("   Suche nach Betreffs mit [TEST 1/3], [TEST 2/3], [TEST 3/3]")


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("❌ Bitte E-Mail-Adresse angeben:")
        print("   python3 send_test.py deine@email.com")
        sys.exit(1)

    test_email = sys.argv[1]
    send_all_tests(test_email)
