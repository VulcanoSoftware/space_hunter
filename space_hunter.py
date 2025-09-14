import shutil
import os
import yaml
import time
from datetime import datetime, timedelta
import requests

def stuur_discord_bericht(bericht, webhook_url):
    try:
        data = {
            "content": bericht,
            "avatar_url": "https://www.dropbox.com/scl/fi/7rivhnuaef6yu51wsv6kg/space_hunter.png?rlkey=worm219zj3k7wd1qmyxbfhbgp&st=9n2nf8tu&dl=1"
        }
        requests.post(webhook_url, json=data)
    except Exception as e:
        print(f"Fout bij versturen Discord bericht: {e}")

def print_en_discord(bericht, webhook_url):
    stuur_discord_bericht(bericht, webhook_url)

def laad_settings(bestand_pad):
    if os.path.exists(bestand_pad):
        with open(bestand_pad, 'r') as bestand:
            return yaml.safe_load(bestand) or {}
    return {}

def sla_settings_op(bestand_pad, settings):
    with open(bestand_pad, 'w') as bestand:
        yaml.dump(settings, bestand)

def check_free_space(disk_path, min_free_gb, webhook_url, actie, verplaats_locatie):
    if os.name == 'nt':
        disk_path = disk_path.replace('/', '\\')

    total, used, free = shutil.disk_usage(disk_path)
    free_gb = free / (2**30)

    if free_gb < min_free_gb:
        print_en_discord(f"Onvoldoende ruimte! Er is slechts {free_gb:.2f} GB vrij op {disk_path}.", webhook_url)
        verwijder_oudste_bestand(disk_path, webhook_url, actie, verplaats_locatie)
    else:
        print_en_discord(f"Er is voldoende ruimte! Er is {free_gb:.2f} GB vrij op {disk_path}.", webhook_url)

def verwijder_oudste_bestand(map_pad, webhook_url, actie, verplaats_locatie=None):
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
            if actie == 'verplaatsen' and verplaats_locatie:
                nieuwe_pad = os.path.join(verplaats_locatie, os.path.basename(oudste_bestand))
                shutil.move(oudste_bestand, nieuwe_pad)
                print_en_discord(f"Het oudste bestand is verplaatst: {oudste_bestand} naar {nieuwe_pad}", webhook_url)
            elif actie == 'verwijderen':
                os.remove(oudste_bestand)
                print_en_discord(f"Het oudste bestand is verwijderd: {oudste_bestand}", webhook_url)
            else:
                print_en_discord(f"Ongeldige actie of ontbrekende verplaatsingslocatie: {actie}", webhook_url)
        except Exception as e:
            print_en_discord(f"Fout bij uitvoeren van actie op {oudste_bestand}: {e}", webhook_url)
    else:
        print_en_discord("Er zijn geen bestanden gevonden in de opgegeven map.", webhook_url)

def check_en_monitor_schijven(settings):
    webhook_url = settings.get('webhook_url', '')
    for disk in settings.get('disks', []):
        disk_path = disk.get('path')
        min_free_gb = disk.get('min_free_gb', 40)
        actie = disk.get('actie', 'verwijderen') # Standaard actie is verwijderen
        verplaats_locatie = disk.get('verplaats_locatie')
        if disk_path:
            check_free_space(disk_path, min_free_gb, webhook_url, actie, verplaats_locatie)

if __name__ == "__main__":
    while True:
        try:
            settings_pad = os.path.join(os.getcwd(), 'settings.yml')
            settings = laad_settings(settings_pad)

            if 'disks' not in settings:
                settings['disks'] = []

            if 'webhook_url' not in settings:
                settings['webhook_url'] = input("Voer de Discord webhook URL in: ")
                sla_settings_op(settings_pad, settings)

            webhook_url = settings['webhook_url']

            for i in range(2):
                if len(settings['disks']) <= i:
                    disk_path = input(f"Voer het pad van schijf {i + 1} in: ")
                    min_free_gb = input(f"Voer de minimum vrije ruimte in GB in voor schijf {i + 1} (standaard 40): ")
                    min_free_gb = int(min_free_gb) if min_free_gb.strip().isdigit() else 40

                    actie = input(f"Voer de actie in voor schijf {i + 1} (verplaatsen/verwijderen, standaard verwijderen): ").lower()
                    if actie not in ['verplaatsen', 'verwijderen']:
                        actie = 'verwijderen'

                    verplaats_locatie = None
                    if actie == 'verplaatsen':
                        verplaats_locatie = input(f"Voer de verplaatsingslocatie in voor schijf {i + 1}: ")
                        while not os.path.isdir(verplaats_locatie):
                            print("Ongeldig pad. Zorg ervoor dat de map bestaat.")
                            verplaats_locatie = input(f"Voer de verplaatsingslocatie in voor schijf {i + 1}: ")

                    settings['disks'].append({'path': disk_path, 'min_free_gb': min_free_gb, 'actie': actie, 'verplaats_locatie': verplaats_locatie})
                    sla_settings_op(settings_pad, settings)

            laatste_clear = datetime.now()
            while True:
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
        except Exception as e:
            error_bericht = f"\nEr is een fout opgetreden: {e}"
            print(error_bericht)
            try:
                stuur_discord_bericht(error_bericht, webhook_url)
            except:
                print("Kon de error niet naar Discord sturen")
            print("Het programma zal over 10 seconden opnieuw opstarten...")
            time.sleep(10)
        except KeyboardInterrupt:
            afsluit_bericht = "\nProgramma wordt afgesloten... Druk op Enter om het venster te sluiten."
            print(afsluit_bericht)
            try:
                stuur_discord_bericht(afsluit_bericht, webhook_url)
            except:
                print("Kon het afsluitbericht niet naar Discord sturen")
            input("")
            break