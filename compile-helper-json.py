#!pgodatagen/bin/python

import json
import re
import csv

from pprint import pprint
from collections import OrderedDict


# Helper snippet to create the in/legacy-moves.json
legacyMovesCsv = []
with open('in/legacy-moves.csv') as csvfile:
    hasHeader = csv.Sniffer().has_header(csvfile.read(256))
    csvfile.seek(0)
    reader = csv.DictReader(csvfile, fieldnames=['pokemonId', 'moveId', 'isQuickMove'])

    rownum = 0
    for row in reader:
        rownum += 1
        if hasHeader and rownum == 1:
            continue

        legacyMovesCsv.append(row)

legacyMoves = {}
for legacyMove in legacyMovesCsv:
    if legacyMove['pokemonId'] not in legacyMoves:
        legacyMoves[legacyMove['pokemonId']] = {
            'quickMoves': [],
            'cinematicMoves': []
        }
    if legacyMove['isQuickMove'] == "1":
        if legacyMove['moveId'] not in legacyMoves[legacyMove['pokemonId']]['quickMoves']:
            legacyMoves[legacyMove['pokemonId']]['quickMoves'].append(int(legacyMove['moveId']))
    else:
        if legacyMove['moveId'] not in legacyMoves[legacyMove['pokemonId']]['cinematicMoves']:
            legacyMoves[legacyMove['pokemonId']]['cinematicMoves'].append(int(legacyMove['moveId']))

legacyMoves = OrderedDict(sorted(legacyMoves.items(), key=lambda t: int(t[0])))

with open('in/legacy-moves.json', 'w') as outfile:
    json.dump(legacyMoves, outfile)


languages = ['en', 'ja', 'fr', 'es', 'de', 'it', 'ko', 'zh-tw', 'pt-br']
translations = {}
for langKey in languages:
    f = open("in/translations-{:s}.raw.txt".format(langKey), 'r')
    translations[langKey] = {}
    for line in f:
        # m = re.search(pattern=r'string Key = \"(.*?)\"\n.*?string Translation = \"(.*?)\"', string=line, flags=re.MULTILINE)
        mKey = re.search(r'string Key = \"(.*?)\"', line)
        if mKey is not None:
            mValue = re.search(r'string Translation = \"(.*?)\"', f.readline())
            if mValue is not None:
                translations[langKey][mKey.group(1)] = mValue.group(1)

    translations[langKey] = OrderedDict(sorted(translations[langKey].items()))
    with open("in/translations-{:s}.txt".format(langKey), 'w') as outfile:
        json.dump(translations[langKey], outfile, sort_keys=True)

defaultEmptyText = {'en': ''}
formTranslationKeys = {
    # For whatever reason, there is no "form_alola", but this stupid key... so copy it for convienance:
    'form_alola': 'alola_pokedex_header',
    'CASTFORM_RAINY': 'form_rain',
    'CASTFORM_SNOWY': 'form_snow',
    'CASTFORM_SUNNY': 'form_sun',
    'BURMY_PLANT': 'form_plant_cloak',
    'BURMY_SANDY': 'form_sandy_cloak',
    'BURMY_TRASH': 'form_trash_cloak',
    'WORMADAM_PLANT': 'form_plant_cloak',
    'WORMADAM_SANDY': 'form_sandy_cloak',
    'WORMADAM_TRASH': 'form_trash_cloak',
    'CHERRIM_SUNNY': 'form_sunshine'
}
formTranslations = {}
for targetKey, origKey in formTranslationKeys.items():
    for langKey in languages:
        if targetKey not in formTranslations:
            formTranslations[targetKey] = {}
        formTranslations[targetKey][langKey] = translations[langKey][origKey]

formTranslations = OrderedDict(sorted(formTranslations.items()))

with open('in/form-translations.json', 'w') as outfile:
    json.dump(formTranslations, outfile, sort_keys=True)


'''
with open('in/legacy-moves2.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=['pokemonId', 'moveId', 'isQuickMove'])
    writer.writeheader()
    for pokemonId, pokemon in legacyMovesJson.items():
        for moveType in ['quickMoves', 'cinematicMoves']:
            for move in pokemon[moveType]:
                pokemonMove = {
                    'pokemonId': pokemonId,
                    'moveId': move,
                    'isQuickMove': (1 if moveType == 'quickMoves' else 0)
                }
                writer.writerow(pokemonMove)
exit(1)
'''