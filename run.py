#!pgodatagen/bin/python

import json
import re

# from v0_47_1_pb2 import *
from v0_57_2_pb2 import *
from google.protobuf.json_format import MessageToJson
import csv
from pprint import pprint


# Read text CSVs
pokemonTexts = {}
with open('text-files/pokemon.txt') as csvfile:
    reader = csv.DictReader(csvfile, dialect='excel-tab', fieldnames=['key', 'en', 'ja', 'fr', 'es', 'de', 'it', 'kr'])
    for row in reader:
        key = row['key']
        del row['key']
        pokemonTexts[key] = row

movesTexts = {}
with open('text-files/moves.txt') as csvfile:
    reader = csv.DictReader(csvfile, dialect='excel-tab', fieldnames=['key', 'en', 'ja', 'fr', 'es', 'de', 'it', 'kr'])
    for row in reader:
        key = row['key']
        del row['key']
        movesTexts[key] = row

generalTexts = {}
with open('text-files/general.txt') as csvfile:
    reader = csv.DictReader(csvfile, dialect='excel-tab', fieldnames=['key', 'en', 'ja', 'fr', 'es', 'de', 'it', 'kr'])
    for row in reader:
        key = row['key']
        del row['key']
        generalTexts[key] = row

# Read GAME_MASTER file
with open('GAME_MASTER', mode='rb') as file: # b is important -> binary
    fileContent = file.read()

decodedGameMaster=GetGameMasterClientTemplatesOutProto()
decodedGameMaster.ParseFromString(fileContent)

# Process messages in GAME_MASTER file
moves = {}
pokemons = {}
items = []
types = {}
badges = {}
for i in decodedGameMaster.items:
    if i.HasField('move'):
        moveId = i.move.unique_id

        jsonObj = MessageToJson(i)
        move = json.loads(jsonObj)['move']

        moveNameKey = 'move_name_{:04d}'.format(moveId)
        if moveNameKey in movesTexts:
            move['name'] = movesTexts[moveNameKey]
        else:
            m = re.search('V[0-9]+_MOVE_(.*)', move['uniqueId'])
            moveName = m.group(1).replace('_FAST', '').replace('_', ' ').lower().title()

            move['name'] = {'en': moveName}

        move['moveId'] = moveId

        moves[moveId] = move

    elif i.HasField('pokemon'):
        # There seems to be a buddy size 4, but it's not in the definition...
        if i.pokemon.buddy_size > 3:
            i.pokemon.buddy_size = 0

        pokemonId = i.pokemon.unique_id
        pokemonTypes = [i.pokemon.type1]
        if i.pokemon.type2:
            pokemonTypes.append(i.pokemon.type2)

        jsonObj = MessageToJson(i)
        pokemon = json.loads(jsonObj)['pokemon']

        pokemonCategoryKey = 'pokemon_category_{:04d}'.format(pokemonId)
        pokemon['category'] = {'en': ''}
        if pokemonCategoryKey in pokemonTexts:
            pokemon['category'] = pokemonTexts[pokemonCategoryKey]

        pokemonDescKey = 'pokemon_desc_{:04d}'.format(pokemonId)
        pokemon['description'] = {'en': ''}
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

        pokemon['types'] = pokemonTypes
        del pokemon['type1']
        if i.pokemon.type2:
            del pokemon['type2']

        pokemons[pokemonId] = pokemon

    elif i.HasField('item'):
        jsonObj = MessageToJson(i)
        items.append(jsonObj)

    elif i.HasField('type_effective'):
        typeId = i.type_effective.attack_type

        jsonObj = MessageToJson(i)
        typeTmp = json.loads(jsonObj)
        type = typeTmp['typeEffective']

        m = re.search('POKEMON_TYPE_(.*)', typeTmp['templateId'])
        typeName = m.group(1).replace('_', ' ').lower()

        typeNameKey = 'pokemon_type_{:s}'.format(typeName)
        if typeNameKey in generalTexts:
            type['name'] = generalTexts[typeNameKey]
        else:
            type['name'] = {'en': typeName.title()}

        type['typeId'] = typeId

        types[typeId] = type

    elif i.HasField('badge'):
        badgeId = i.badge.badge_type

        jsonObj = MessageToJson(i)
        badgeTmp = json.loads(jsonObj)
        badge = badgeTmp['badge']

        m = re.search('BADGE_(.*)', badgeTmp['templateId'])
        badgeName = m.group(1).lower()

        badgeNameKey = 'badge_{:s}_title'.format(badgeName)
        if badgeNameKey in generalTexts:
            badge['name'] = generalTexts[badgeNameKey]
        else:
            badge['name'] = {'en': badgeName.replace('_', ' ').title()}

        badgeDescKey = 'badge_{:s}'.format(badgeName)
        if badgeDescKey in generalTexts:
            badge['description'] = generalTexts[badgeDescKey].copy()
            badge['descriptionClean'] = generalTexts[badgeDescKey].copy()
            for key, desc in badge['descriptionClean'].items():
                badgeDescClean = desc.replace('{0}', ' ').replace('{0:0.#}', ' ')
                badge['descriptionClean'][key] = " ".join(badgeDescClean.split())
        else:
            badge['description'] = {'en': ''}

        badge['badgeId'] = badgeId

        badges[badgeId] = badge

    elif i.HasField('player_level'):
        jsonObj = MessageToJson(i)
        levelsTmp = json.loads(jsonObj)['playerLevel']

        playerLevels = {}
        idx = 1
        for requiredExp in levelsTmp['requiredExp']:
            playerLevels[idx] = {
                'requiredExp': requiredExp,
                'cpMultiplier': levelsTmp['cpMultiplier'][idx-1],
                'rankNum': levelsTmp['rankNum'][idx-1]
            }
            idx += 1


with open('out/pokemon.json', 'w') as outfile:
    json.dump(pokemons, outfile)
with open('out/moves.json', 'w') as outfile:
    json.dump(moves, outfile)
with open('out/types.json', 'w') as outfile:
    json.dump(types, outfile)
with open('out/badges.json', 'w') as outfile:
    json.dump(badges, outfile)
with open('out/items.json', 'w') as outfile:
    json.dump(items, outfile)
with open('out/player-levels.json', 'w') as outfile:
    json.dump(playerLevels, outfile)
