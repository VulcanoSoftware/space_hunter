# Space Hunter

Space Hunter is een Python-tool die de beschikbare schijfruimte op opgegeven locaties controleert en automatisch bestanden verwijdert wanneer de beschikbare ruimte onder een minimumdrempel komt.

## Functionaliteiten

- Controleert de vrije schijfruimte op meerdere opgegeven locaties.
- Verwijdert automatisch de oudste bestanden als de vrije ruimte onder een ingestelde limiet komt.
- Slaat configuratie-instellingen op in een YAML-bestand (`settings.yml`) voor herbruikbaarheid.

## Vereisten

- Python 3.6 of hoger
- Afhankelijkheden:
  - PyYAML

Installeer de afhankelijkheden via pip:
```bash
pip install pyyaml
