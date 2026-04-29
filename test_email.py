#!/usr/bin/env python3
"""
Test-Skript für E-Mail-Versand
Sendet eine Test-E-Mail an dich selbst
"""

import json
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path


def load_config(config_file='config.json'):
    """Lädt die Konfiguration"""
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_template(template_file):
    """Lädt HTML-Template"""
    with open(template_file, 'r', encoding='utf-8') as f:
        return f.read()


def send_test_email(test_recipient=None):
    """Sendet eine Test-E-Mail"""
    print("=" * 70)
    print("E-MAIL TEST-VERSAND")
    print("=" * 70)

    # Lade Config
    config = load_config()

    # Standard: An dich selbst
    if not test_recipient:
        test_recipient = config['email']['from_email']

    print(f"\nEmpfänger: {test_recipient}")

    # Lade alle drei Templates
    templates = [
        {
            'name': 'E-Mail 1',
            'subject': config['templates']['email_1_subject'],
            'file': config['templates']['email_1_template']
        },
        {
            'name': 'E-Mail 2',
            'subject': config['templates']['email_2_subject'],
            'file': config['templates']['email_2_template']
        },
        {
            'name': 'E-Mail 3',
            'subject': config['templates']['email_3_subject'],
            'file': config['templates']['email_3_template']
        }
    ]

    # Frage welche E-Mail getestet werden soll
    print("\nWelche E-Mail möchtest du testen?")
    print("1 - E-Mail 1 (Erste Kontaktaufnahme)")
    print("2 - E-Mail 2 (Follow-up)")
    print("3 - E-Mail 3 (Letzter Reminder)")
    print("4 - Alle drei E-Mails")

    choice = input("\nDeine Wahl (1-4): ").strip()

    if choice == '4':
        selected_templates = templates
    elif choice in ['1', '2', '3']:
        selected_templates = [templates[int(choice) - 1]]
    else:
        print("❌ Ungültige Auswahl!")
        return

    # Test-Anrede
    test_anrede = "Geschätzte Frau Musterfrau"

    print(f"\n📧 Sende {len(selected_templates)} Test-E-Mail(s)...")

    # Sende E-Mails
    for template_info in selected_templates:
        print(f"\n📨 Versende: {template_info['name']}")
        print(f"   Betreff: {template_info['subject']}")

        # Lade Template
        template = load_template(template_info['file'])

        # Personalisiere
        html_content = template.replace('{{ANREDE}}', test_anrede)

        try:
            # E-Mail erstellen
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"[TEST] {template_info['subject']}"
            msg['From'] = f"{config['email']['from_name']} <{config['email']['from_email']}>"
            msg['To'] = test_recipient

            # HTML-Teil hinzufügen
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)

            # SSL-Kontext
            context = ssl.create_default_context()

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

            print(f"   ✅ Erfolgreich gesendet!")

        except Exception as e:
            print(f"   ❌ FEHLER: {str(e)}")

    print("\n" + "=" * 70)
    print("Test abgeschlossen!")
    print("=" * 70)
    print(f"\n📬 Prüfe dein Postfach: {test_recipient}")


if __name__ == '__main__':
    import sys

    # Optional: E-Mail-Adresse als Argument
    test_email = sys.argv[1] if len(sys.argv) > 1 else None

    send_test_email(test_email)
