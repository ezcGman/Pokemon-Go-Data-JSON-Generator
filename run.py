#!pgodatagen/bin/python

import json
import re

# from v0_47_1_pb2 import *
from v0_57_2_pb2 import *
from google.protobuf.json_format import MessageToJson
import csv


# Read text CSVs
pokemonTexts = {}
with open('text-files/pokemon.txt') as csvfile:
    reader = csv.DictReader(csvfile, dialect='excel-tab', fieldnames=['key', 'en', 'ja', 'fr', 'es', 'de', 'it', 'comment'])
    for row in reader:
        key = row['key']
        del row['key']
        del row['comment']
        pokemonTexts[key] = row

# Read GAME_MASTER file
with open('GAME_MASTER', mode='rb') as file: # b is important -> binary
    fileContent = file.read()

decodedGameMaster=GetGameMasterClientTemplatesOutProto()
decodedGameMaster.ParseFromString(fileContent)

# Process messages in GAME_MASTER file
moves = {}
pokemons = {}
items = []
types = []
for i in decodedGameMaster.items:
    if i.HasField('move'):
        moveId = i.move.unique_id

        jsonObj = MessageToJson(i)
        move = json.loads(jsonObj)['move']

        m = re.search('V[0-9]+_MOVE_(.*)', move['uniqueId'])
        move['name'] = m.group(1).replace('_FAST', '').replace('_', ' ').lower().title()

        move['moveId'] = moveId

        moves[moveId] = move

    elif i.HasField('pokemon'):
        # There seems to be a buddy size 4, but it's not in the definition...
        if i.pokemon.buddy_size > 3:
            i.pokemon.buddy_size = 0

        pokemonId = i.pokemon.unique_id

        jsonObj = MessageToJson(i)
        pokemon = json.loads(jsonObj)['pokemon']

        pokemonCategoryKey = 'pokemon_category_{:04d}'.format(pokemonId)
        pokemon['category'] = None
        if pokemonCategoryKey in pokemonTexts:
            pokemon['category'] = pokemonTexts[pokemonCategoryKey]

        pokemonDescKey = 'pokemon_desc_{:04d}'.format(pokemonId)
        pokemon['description'] = None
        if pokemonDescKey in pokemonTexts:
            pokemon['description'] = pokemonTexts[pokemonDescKey]

        pokemonNameKey = 'pokemon_name_{:04d}'.format(pokemonId)
        if pokemonNameKey in pokemonTexts:
            pokemon['name'] = pokemonTexts[pokemonNameKey]
        else:
            m = re.search('V[0-9]+_POKEMON_(.*)', pokemon['uniqueId'])
            pokemonName = m.group(1).replace('_', ' ').lower().title()
            if pokemonId == 29:
                pokemonName += ' ♀'
            elif pokemonId == 32:
                pokemonName += ' ♂'

            pokemon['name'] = {'en': pokemonName}

        pokemon['pokemonId'] = pokemonId

        pokemons[pokemonId] = pokemon

    elif i.HasField('item'):
        jsonObj = MessageToJson(i)
        items.append(jsonObj)

    elif i.HasField('type_effective'):
        jsonObj = MessageToJson(i)
        types.append(jsonObj)


with open('out/pokemon.json', 'w') as outfile:
    json.dump(pokemons, outfile)
with open('out/moves.json', 'w') as outfile:
    json.dump(moves, outfile)
with open('out/types.json', 'w') as outfile:
    json.dump(types, outfile)
with open('out/items.json', 'w') as outfile:
    json.dump(items, outfile)
