#!/usr/bin/env python3
"""
Tägliches Kampagnen-Skript
Führt Response-Tracking und E-Mail-Versand in einem Schritt aus
"""

import subprocess
import sys
from datetime import datetime


def print_header(text):
    """Druckt formatierte Überschrift"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def run_command(script_name, description):
    """Führt ein Python-Skript aus und gibt Fehler zurück"""
    print(f"🔄 {description}...")
    print("-" * 70)

    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=False,
            text=True,
            check=True
        )
        print("-" * 70)
        print(f"✅ {description} abgeschlossen\n")
        return True
    except subprocess.CalledProcessError as e:
        print("-" * 70)
        print(f"❌ FEHLER bei {description}")
        print(f"   Fehlercode: {e.returncode}\n")
        return False


def main():
    """Hauptfunktion - führt komplette Kampagne aus"""

    print_header(f"PSYCARE KAMPAGNE - {datetime.now().strftime('%d.%m.%Y %H:%M')}")

    print("Dieses Skript führt aus:")
    print("  1️⃣  Response-Tracking (prüft auf Antworten)")
    print("  2️⃣  E-Mail-Versand (max. 100 E-Mails)")
    print()

    # Schritt 1: Response-Tracking
    print_header("SCHRITT 1: RESPONSE-TRACKING")
    success_responses = run_command(
        'check_responses.py',
        'Prüfe auf Antworten im Postfach'
    )

    if not success_responses:
        print("⚠️  Response-Tracking hatte Fehler, aber wir machen weiter...\n")

    # Schritt 2: E-Mail-Versand
    print_header("SCHRITT 2: E-MAIL-VERSAND")
    success_campaign = run_command(
        'send_campaign.py',
        'Versende E-Mails'
    )

    # Zusammenfassung
    print_header("ZUSAMMENFASSUNG")

    if success_responses and success_campaign:
        print("✅ Kampagne erfolgreich abgeschlossen!")
        print("   - Response-Tracking: OK")
        print("   - E-Mail-Versand: OK")
    elif success_campaign:
        print("⚠️  Kampagne teilweise erfolgreich")
        print("   - Response-Tracking: FEHLER")
        print("   - E-Mail-Versand: OK")
    else:
        print("❌ Kampagne hatte Fehler")
        print("   Bitte prüfe die Logs oben")

    print("\n" + "=" * 70)
    print(f"  Fertig um {datetime.now().strftime('%H:%M')}")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
