import shutil
import os
import yaml
import time

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

def check_free_space(disk_path, min_free_gb):
    """
    Controleer de vrije ruimte op een schijf en verwijder indien nodig bestanden.

    :param disk_path: Pad naar de te controleren schijf
    :param min_free_gb: Minimum vrije ruimte in GB die vereist is
    """
    if os.name == 'nt':  # Windows
        disk_path = disk_path.replace('/', '\\')  # Verander / naar \\

    total, used, free = shutil.disk_usage(disk_path)
    free_gb = free / (2**30)

    if free_gb < min_free_gb:
        print(f"Onvoldoende ruimte! Er is slechts {free_gb:.2f} GB vrij op {disk_path}.")
        verwijder_oudste_bestand(disk_path)
    else:
        print(f"Er is voldoende ruimte! Er is {free_gb:.2f} GB vrij op {disk_path}.")

def verwijder_oudste_bestand(map_pad):
    """
    Verwijdert het oudste bestand in de opgegeven map.

    :param map_pad: De pad naar de map waarin je wilt zoeken naar het oudste bestand.
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
            print(f"Het oudste bestand is verwijderd: {oudste_bestand}")
        except Exception as e:
            print(f"Fout bij verwijderen van {oudste_bestand}: {e}")
    else:
        print("Er zijn geen bestanden gevonden in de opgegeven map.")

def check_en_monitor_schijven(settings):
    """
    Controleer en monitor meerdere schijven zoals gedefinieerd in de instellingen.

    :param settings: Dictionary met instellingen die schijfpaden en minimum vrije ruimte bevatten.
    """
    for disk in settings.get('disks', []):
        disk_path = disk.get('path')
        min_free_gb = disk.get('min_free_gb', 40)
        if disk_path:
            check_free_space(disk_path, min_free_gb)

if __name__ == "__main__":
    settings_pad = os.path.join(os.getcwd(), 'settings.yml')
    settings = laad_settings(settings_pad)

    if 'disks' not in settings:
        settings['disks'] = []

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
        while True:
            print("\nControleren van schijfruimte...")
            check_en_monitor_schijven(settings)
            # Wacht 5 minuten voordat de volgende controle wordt uitgevoerd
            print("--------------------------------")
            print("Wachten 5 minuten voordat de volgende controle wordt uitgevoerd...")
            print("--------------------------------")
            time.sleep(300)
    except KeyboardInterrupt:
        print("\nProgramma wordt afgesloten...")