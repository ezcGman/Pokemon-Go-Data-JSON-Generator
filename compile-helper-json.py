#!pgodatagen/bin/python

import json

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
            legacyMoves[legacyMove['pokemonId']]['quickMoves'].append(legacyMove['moveId'])
    else:
        if legacyMove['moveId'] not in legacyMoves[legacyMove['pokemonId']]['cinematicMoves']:
            legacyMoves[legacyMove['pokemonId']]['cinematicMoves'].append(legacyMove['moveId'])

legacyMoves = OrderedDict(sorted(legacyMoves.items(), key=lambda t: int(t[0])))

with open('in/legacy-moves.json', 'w') as outfile:
    json.dump(legacyMoves, outfile)


featureGen3Texts = {}
with open('in/feature-gen3.txt') as csvfile:
    reader = csv.DictReader(csvfile, dialect='excel-tab', fieldnames=['key', 'en', 'ja', 'fr', 'es', 'de', 'it', 'ko', 'zh-tw', 'pt-br'])
    for row in reader:
        key = row['key']
        del row['key']
        # There are some empty strings in there sometimes... drop them
        if None in row:
            del row[None]
        featureGen3Texts[key] = row

generalTexts = {}
with open('in/general.txt') as csvfile:
    reader = csv.DictReader(csvfile, dialect='excel-tab', fieldnames=['key', 'en', 'ja', 'fr', 'es', 'de', 'it', 'ko', 'zh-tw', 'pt-br'])
    for row in reader:
        key = row['key']
        del row['key']
        generalTexts[key] = row

defaultEmptyText = {'en': ''}
formTranslations = {
    'NORMAL': featureGen3Texts['form_normal'],
    'SUNNY': featureGen3Texts['form_sun'],
    'RAINY': featureGen3Texts['form_rain'],
    'SNOWY': featureGen3Texts['form_snow'],
    'ALOLA': generalTexts['alola_pokedex_header'],
    'ATTACK': featureGen3Texts['form_attack'],
    'DEFENSE': featureGen3Texts['form_defense'],
    'SPEED': featureGen3Texts['form_speed'],
    'RATTATA_NORMAL': defaultEmptyText,
    'RATICATE_NORMAL': defaultEmptyText,
    'RAICHU_NORMAL': defaultEmptyText,
    'SANDSHREW_NORMAL': defaultEmptyText,
    'SANDSLASH_NORMAL': defaultEmptyText,
    'VULPIX_NORMAL': defaultEmptyText,
    'NINETALES_NORMAL': defaultEmptyText,
    'DIGLETT_NORMAL': defaultEmptyText,
    'DUGTRIO_NORMAL': defaultEmptyText,
    'MEOWTH_NORMAL': defaultEmptyText,
    'PERSIAN_NORMAL': defaultEmptyText,
    'GEODUDE_NORMAL': defaultEmptyText,
    'GRAVELER_NORMAL': defaultEmptyText,
    'GOLEM_NORMAL': defaultEmptyText,
    'GRIMER_NORMAL': defaultEmptyText,
    'MUK_NORMAL': defaultEmptyText,
    'EXEGGUTOR_NORMAL': defaultEmptyText,
    'MAROWAK_NORMAL': defaultEmptyText
}

with open('in/form-translations.json', 'w') as outfile:
    json.dump(formTranslations, outfile)


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