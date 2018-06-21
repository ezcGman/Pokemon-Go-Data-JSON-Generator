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
pprint(legacyMoves)

with open('in/legacy-moves.json', 'w') as outfile:
    json.dump(legacyMoves, outfile)


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