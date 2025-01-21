import shutil
import os
import yaml
import time
from datetime import datetime, timedelta
import requests  # Nieuwe import voor Discord webhook

def stuur_discord_bericht(bericht, webhook_url):
    """Stuur een bericht naar Discord via webhook"""
    try:
        data = {"content": bericht}
        requests.post(webhook_url, json=data)
    except Exception as e:
        print(f"Fout bij versturen Discord bericht: {e}")

def print_en_discord(bericht, webhook_url):
    """Print het bericht naar console en stuur naar Discord"""
    print(bericht)
    stuur_discord_bericht(bericht, webhook_url)

def laad_settings(bestand_pad):
    """
    Laad de instellingen uit een YAML-bestand. Als het bestand niet bestaat, maak een lege dict.

    :param bestand_pad: Pad naar het settings.yml-bestand
    :return: Dictionary met instellingen
    """
    if os.path.exists(bestand_pad):
        with open(bestand_pad, 'r') as bestand:
            return yaml.safe_load(bestand) or {}
    return {}

def sla_settings_op(bestand_pad, settings):
    """
    Sla de instellingen op in een YAML-bestand.

    :param bestand_pad: Pad naar het settings.yml-bestand
    :param settings: Dictionary met instellingen
    """
    with open(bestand_pad, 'w') as bestand:
        yaml.dump(settings, bestand)

def check_free_space(disk_path, min_free_gb, webhook_url):
    """
    Controleer de vrije ruimte op een schijf en verwijder indien nodig bestanden.

    :param disk_path: Pad naar de te controleren schijf
    :param min_free_gb: Minimum vrije ruimte in GB die vereist is
    :param webhook_url: Discord webhook URL
    """
    if os.name == 'nt':  # Windows
        disk_path = disk_path.replace('/', '\\')  # Verander / naar \\

    total, used, free = shutil.disk_usage(disk_path)
    free_gb = free / (2**30)

    if free_gb < min_free_gb:
        print_en_discord(f"Onvoldoende ruimte! Er is slechts {free_gb:.2f} GB vrij op {disk_path}.", webhook_url)
        verwijder_oudste_bestand(disk_path, webhook_url)
    else:
        print_en_discord(f"Er is voldoende ruimte! Er is {free_gb:.2f} GB vrij op {disk_path}.", webhook_url)

def verwijder_oudste_bestand(map_pad, webhook_url):
    """
    Verwijdert het oudste bestand in de opgegeven map.

    :param map_pad: De pad naar de map waarin je wilt zoeken naar het oudste bestand.
    :param webhook_url: Discord webhook URL
    """
    oudste_bestand = None
    oudste_tijd = float('inf')

    for bestand in os.listdir(map_pad):
        bestand_pad = os.path.join(map_pad, bestand)
        if os.path.isfile(bestand_pad):
            laatste_wijziging = os.path.getmtime(bestand_pad)
            if laatste_wijziging < oudste_tijd:
                oudste_tijd = laatste_wijziging
                oudste_bestand = bestand_pad

    if oudste_bestand:
        try:
            os.remove(oudste_bestand)
            print_en_discord(f"Het oudste bestand is verwijderd: {oudste_bestand}", webhook_url)
        except Exception as e:
            print_en_discord(f"Fout bij verwijderen van {oudste_bestand}: {e}", webhook_url)
    else:
        print_en_discord("Er zijn geen bestanden gevonden in de opgegeven map.", webhook_url)

def check_en_monitor_schijven(settings):
    """
    Controleer en monitor meerdere schijven zoals gedefinieerd in de instellingen.

    :param settings: Dictionary met instellingen die schijfpaden en minimum vrije ruimte bevatten.
    """
    webhook_url = settings.get('webhook_url', '')
    for disk in settings.get('disks', []):
        disk_path = disk.get('path')
        min_free_gb = disk.get('min_free_gb', 40)
        if disk_path:
            check_free_space(disk_path, min_free_gb, webhook_url)

if __name__ == "__main__":
    settings_pad = os.path.join(os.getcwd(), 'settings.yml')
    settings = laad_settings(settings_pad)

    if 'disks' not in settings:
        settings['disks'] = []

    # Vraag om Discord webhook URL als deze nog niet is ingesteld
    if 'webhook_url' not in settings:
        settings['webhook_url'] = input("Voer de Discord webhook URL in: ")
        sla_settings_op(settings_pad, settings)

    webhook_url = settings['webhook_url']

    # Eenmalige configuratie van schijven
    for i in range(2):
        if len(settings['disks']) <= i:
            disk_path = input(f"Voer het pad van schijf {i + 1} in: ")
            min_free_gb = input(f"Voer de minimum vrije ruimte in GB in voor schijf {i + 1} (standaard 40): ")
            min_free_gb = int(min_free_gb) if min_free_gb.strip().isdigit() else 40

            settings['disks'].append({'path': disk_path, 'min_free_gb': min_free_gb})
            sla_settings_op(settings_pad, settings)

    # Voeg een while loop toe voor continue monitoring
    try:
        laatste_clear = datetime.now()
        while True:
            # Clear de console elke 6 uur
            if datetime.now() - laatste_clear > timedelta(hours=6):
                os.system('cls' if os.name == 'nt' else 'clear')
                laatste_clear = datetime.now()
                print_en_discord("Console is gewist", webhook_url)

            print_en_discord("\nControleren van schijfruimte...", webhook_url)
            check_en_monitor_schijven(settings)
            print_en_discord("--------------------------------", webhook_url)
            print_en_discord("Wachten 5 minuten voordat de volgende controle wordt uitgevoerd...", webhook_url)
            print_en_discord("--------------------------------", webhook_url)
            time.sleep(300)
    except KeyboardInterrupt:
        print_en_discord("\nProgramma wordt afgesloten...", webhook_url)