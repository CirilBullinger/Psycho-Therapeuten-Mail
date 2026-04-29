#!/usr/bin/env python3
"""
Test-Skript - Sendet alle 6 Templates (Sie + Du)
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


def send_all_templates(test_recipient):
    """Sendet alle 6 Templates"""
    print("=" * 70)
    print("TEST ALLER TEMPLATES (SIE + DU)")
    print("=" * 70)

    config = load_config()

    print(f"\nEmpfänger: {test_recipient}")
    print("\n📧 Sende alle 6 Templates...\n")

    # Test-Daten
    test_anrede_sie = "Geschätzte Frau Musterfrau"
    test_anrede_du = "Geschätzte Anna"
    test_vorname = "Anna"
    test_nachname = "Musterfrau"

    # Alle Templates
    templates = [
        # SIE-Form
        {
            'name': 'E-Mail 1 (SIE-Form)',
            'subject': config['templates']['email_1_subject'],
            'file': config['templates']['email_1_template_sie'],
            'anrede': test_anrede_sie
        },
        {
            'name': 'E-Mail 2 (SIE-Form)',
            'subject': config['templates']['email_2_subject'],
            'file': config['templates']['email_2_template_sie'],
            'anrede': test_anrede_sie
        },
        {
            'name': 'E-Mail 3 (SIE-Form)',
            'subject': config['templates']['email_3_subject'],
            'file': config['templates']['email_3_template_sie'],
            'anrede': test_anrede_sie
        },
        # DU-Form
        {
            'name': 'E-Mail 1 (DU-Form)',
            'subject': config['templates']['email_1_subject'],
            'file': config['templates']['email_1_template_du'],
            'anrede': test_anrede_du
        },
        {
            'name': 'E-Mail 2 (DU-Form)',
            'subject': config['templates']['email_2_subject'],
            'file': config['templates']['email_2_template_du'],
            'anrede': test_anrede_du
        },
        {
            'name': 'E-Mail 3 (DU-Form)',
            'subject': config['templates']['email_3_subject'],
            'file': config['templates']['email_3_template_du'],
            'anrede': test_anrede_du
        }
    ]

    success_count = 0
    for i, template_info in enumerate(templates, 1):
        # Personalisiere Betreff
        subject = template_info['subject']
        subject = subject.replace('{{VORNAME}}', test_vorname)
        subject = subject.replace('{{NACHNAME}}', test_nachname)

        print(f"📨 {i}/6 - Versende: {template_info['name']}")
        print(f"    Betreff: {subject}")

        # Lade Template
        template = load_template(template_info['file'])

        # Personalisiere
        text_content = template.replace('{{ANREDE}}', template_info['anrede'])

        try:
            # E-Mail erstellen (Plain Text)
            msg = MIMEText(text_content, 'plain', 'utf-8')
            msg['Subject'] = f"[TEST {i}/6] {subject}"
            msg['From'] = f"{config['email']['from_name']} <{config['email']['from_email']}>"
            msg['To'] = test_recipient

            # SSL-Kontext
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
    print(f"Test abgeschlossen! {success_count}/6 E-Mails erfolgreich gesendet.")
    print("=" * 70)
    print(f"\n📬 Prüfe dein Postfach: {test_recipient}")
    print("\nDu solltest 6 E-Mails erhalten:")
    print("  [TEST 1/6] E-Mail 1 (SIE-Form)")
    print("  [TEST 2/6] E-Mail 2 (SIE-Form)")
    print("  [TEST 3/6] E-Mail 3 (SIE-Form)")
    print("  [TEST 4/6] E-Mail 1 (DU-Form)")
    print("  [TEST 5/6] E-Mail 2 (DU-Form)")
    print("  [TEST 6/6] E-Mail 3 (DU-Form)")


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("❌ Bitte E-Mail-Adresse angeben:")
        print("   python3 test_all_templates.py deine@email.com")
        sys.exit(1)

    test_email = sys.argv[1]
    send_all_templates(test_email)
