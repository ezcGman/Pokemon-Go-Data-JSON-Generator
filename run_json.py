#!pgodatagen/bin/python

import json
import re
import csv
from stringcase import camelcase
from pprint import pprint


# Read text CSVs
pokemonTexts = {}
with open('text-files/pokemon.txt') as csvfile:
    reader = csv.DictReader(csvfile, dialect='excel-tab', fieldnames=['key', 'en', 'ja', 'fr', 'es', 'de', 'it', 'ko', 'zh-tw', 'pt-br'])
    for row in reader:
        key = row['key']
        del row['key']
        pokemonTexts[key] = row

movesTexts = {}
with open('text-files/moves.txt') as csvfile:
    reader = csv.DictReader(csvfile, dialect='excel-tab', fieldnames=['key', 'en', 'ja', 'fr', 'es', 'de', 'it', 'ko', 'zh-tw', 'pt-br'])
    for row in reader:
        key = row['key']
        del row['key']
        movesTexts[key] = row

itemsTexts = {}
with open('text-files/items.txt') as csvfile:
    reader = csv.DictReader(csvfile, dialect='excel-tab', fieldnames=['key', 'en', 'ja', 'fr', 'es', 'de', 'it', 'ko', 'zh-tw', 'pt-br'])
    for row in reader:
        key = row['key']
        del row['key']
        itemsTexts[key] = row

generalTexts = {}
with open('text-files/general.txt') as csvfile:
    reader = csv.DictReader(csvfile, dialect='excel-tab', fieldnames=['key', 'en', 'ja', 'fr', 'es', 'de', 'it', 'ko', 'zh-tw', 'pt-br'])
    for row in reader:
        key = row['key']
        del row['key']
        generalTexts[key] = row
with open('text-files/gymsv2.txt') as csvfile:
    reader = csv.DictReader(csvfile, dialect='excel-tab', fieldnames=['key', 'en', 'ja', 'fr', 'es', 'de', 'it', 'ko', 'zh-tw', 'pt-br'])
    for row in reader:
        key = row['key']
        del row['key']
        generalTexts[key] = row

# Read GAME_MASTER file
with open('game_master.json', mode='r') as file:
    fileContent = json.loads(file.read())


def camelize(underscoreDict):
    camelDict = {}
    for k,v in underscoreDict.items():
        # Do not touch those, as it would translate 'pt-br' to 'pt'
        if k in ['name', 'description', 'category']:
            camelDict[k] = v
        else:
            camelKey = camelcase(k)
            if isinstance(v, dict):
                camelDict[camelKey] = camelize(v)
            elif isinstance(v, list):
                camelDict[camelKey] = []
                for listItem in v:
                    if isinstance(listItem, dict):
                        camelDict[camelKey].append(camelize(listItem))
                    else:
                        camelDict[camelKey].append(listItem)
            else:
                camelDict[camelKey] = v

    return camelDict


# Process item templates in GAME_MASTER file
moves = {}
pokemons = {}
items = {}
types = {}
badges = {}
playerLevels = {}
gameSettings = {}
for i in fileContent:
    if 'move_settings' in i:
        move = i['move_settings']
        moveId = move['movement_id']

        moveNameKey = 'move_name_{:04d}'.format(moveId)
        if moveNameKey in movesTexts:
            move['name'] = movesTexts[moveNameKey]
        else:
            m = re.search('V[0-9]+_MOVE_(.*)', i['template_id'])
            moveName = m.group(1).replace('_FAST', '').replace('_', ' ').lower().title()

            move['name'] = {'en': moveName}

        move = camelize(move)

        moves[moveId] = move

    elif 'pokemon_settings' in i:
        pokemon = i['pokemon_settings']
        pokemonId = pokemon['pokemon_id']
        familyId = pokemon['family_id']

        parentId = pokemon.get('parent_id', None)

        pokemonTypes = [pokemon['type']]
        del pokemon['type']
        if 'type_2' in pokemon:
            pokemonTypes.append(pokemon['type_2'])
            del pokemon['type_2']
        pokemon['types'] = pokemonTypes

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

        pokemon = camelize(pokemon)

        pokemons[pokemonId] = pokemon

    elif 'item_settings' in i:
        item = i['item_settings']
        itemId = item['item_id']

        m = re.search('ITEM_(.*)', i['template_id'])
        itemName = m.group(1).lower()

        itemNameKey = 'item_{:s}_name'.format(itemName)
        if itemNameKey in itemsTexts:
            item['name'] = itemsTexts[itemNameKey]
        else:
            item['name'] = {'en': itemName.replace('_', ' ').title()}

        itemDescKey = 'item_{:s}_desc'.format(itemName)
        if itemDescKey in itemsTexts:
            item['description'] = itemsTexts[itemDescKey]
        else:
            item['description'] = {'en': ''}

        item = camelize(item)

        items[itemId] = item

    elif 'type_effective' in i:
        type = i['type_effective']
        typeId = type['attack_type']
        del type['attack_type']

        m = re.search('POKEMON_TYPE_(.*)', i['template_id'])
        typeName = m.group(1).replace('_', ' ').lower()

        typeNameKey = 'pokemon_type_{:s}'.format(typeName)
        if typeNameKey in generalTexts:
            type['name'] = generalTexts[typeNameKey]
        else:
            type['name'] = {'en': typeName.title()}

        type = camelize(type)
        type['typeId'] = typeId

        types[typeId] = type

    elif 'badge_settings' in i:
        badge = i['badge_settings']
        badgeId = badge['badge_type']
        del badge['badge_type']

        m = re.search('BADGE_(.*)', i['template_id'])
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

        badge = camelize(badge)
        badge['badgeId'] = badgeId

        badges[badgeId] = badge

    elif 'player_level' in i:
        playerLevel = i['player_level']

        idx = 1
        for requiredExp in playerLevel['required_experience']:
            playerLevels[idx] = {
                'requiredExp': requiredExp,
                'cpMultiplier': playerLevel['cp_multiplier'][idx-1],
                'rankNum': playerLevel['rank_num'][idx-1]
            }
            idx += 1

    elif 'battle_settings' in i or 'gym_badge_settings' in i or 'iap_settings' in i or 'pokemon_upgrades' in i or 'quest_settings' in i or 'weather_affinities' in i or 'weather_bonus_settings' in i:
        # pprint(i.keys())
        del i['template_id']
        settingsKey = list(i.keys())[0]
        if 'battle_settings' in i or 'gym_badge_settings' in i or 'iap_settings' in i or 'pokemon_upgrades' in i or 'weather_bonus_settings' in i:
            gameSettings[settingsKey] = i[settingsKey]
        elif 'quest_settings' in i or 'weather_affinities' in i:
            if settingsKey not in gameSettings:
                gameSettings[settingsKey] = []

            gameSettings[settingsKey].append(i[settingsKey])

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
with open('out/game-settings.json', 'w') as outfile:
    json.dump(gameSettings, outfile)

with open('out/pokemon-base-stats.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=['id', 'name', 'hp', 'atk', 'def', 'type1', 'type2', 'legendary'])
    writer.writeheader()
    for pokemonId, pokemon in pokemons.items():
        pokemonStats = {
            'id': pokemonId,
            'name': pokemon['name']['en'],
            'hp': pokemon['stats']['baseStamina'],
            'atk': pokemon['stats']['baseAttack'],
            'def': pokemon['stats']['baseDefense'],
            'type1': pokemon['types'][0],
            'type2': (pokemon['types'][1] if len(pokemon['types']) >= 2 else None),
            'legendary': ('Y' if 'rarity' in pokemon and pokemon['rarity'] == 1 else None)
        }
        writer.writerow(pokemonStats)

with open('out/types.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=['id', 'name'])
    writer.writeheader()
    for typeId, type in types.items():
        typeData = {
            'id': typeId,
            'name': type['name']['en']
        }
        writer.writerow(typeData)

with open('out/pokemon-quick-moves.csv', 'w') as quickCsvfile:
    with open('out/pokemon-charge-moves.csv', 'w') as chargeCsvfile:
        quickWriter = csv.DictWriter(quickCsvfile, fieldnames=['id', 'name', 'type', 'power', 'staminaLossScalar', 'durationMs', 'dmgWindow', 'damageWindowStartMs', 'damageWindowEndMs', 'energyDelta'])
        quickWriter.writeheader()
        chargeWriter = csv.DictWriter(chargeCsvfile, fieldnames=['id', 'name', 'type', 'power', 'staminaLossScalar', 'healScalar', 'durationMs', 'dmgWindow', 'damageWindowStartMs', 'damageWindowEndMs', 'criticalChance', 'energyDelta'])
        chargeWriter.writeheader()
        for moveId, move in moves.items():
            energyDelta = move.get('energyDelta', 0)
            moveStats = {
                'id': moveId,
                'name': move['name']['en'],
                'type': move['pokemonType'],
                'power': move.get('power', 0),
                'staminaLossScalar': round(move.get('staminaLossScalar', 0), 2),
                'durationMs': move['durationMs'],
                'dmgWindow': move['damageWindowStartMs'],
                'damageWindowStartMs': move['damageWindowEndMs'],
                'damageWindowEndMs': move['damageWindowStartMs'] + move['damageWindowEndMs'],
                'energyDelta': (energyDelta*-1 if energyDelta < 0 else energyDelta)
            }

            # If energy is below 0 (= it costs energy): it's a charge move
            # Special: Struggle (!33) is the only charge move that has 0 energy consumption :/
            if energyDelta < 0 or moveId == 133:
                moveStats['criticalChance'] = int(move.get('criticalChance', 0)*100)
                moveStats['healScalar'] = round(move.get('healScalar', 0), 2)

                chargeWriter.writerow(moveStats)
            # If energy is above 0 (= it adds energy): it's a quick move
            else:
                quickWriter.writerow(moveStats)

with open('out/pokemon-move-combinations.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=['id', 'fast', 'charge'])
    writer.writeheader()
    moveCombis = []
    for pokemonId, pokemon in pokemons.items():
        pokemonName = pokemon['name']['en']
        for quickMove in pokemon['quickMoves']:
            for chargeMove in pokemon['cinematicMoves']:
                moveCombi = {
                    'id': pokemonId,
                    'fast': quickMove,
                    'charge': chargeMove
                }
                writer.writerow(moveCombi)