#!pgodatagen/bin/python

import json
import re
import csv
from copy import deepcopy
import argparse
# from pprint import pprint

from game_master_reader import GameMasterReader


parser = argparse.ArgumentParser()
parser.add_argument('format', nargs='?', default='json', choices=['json', 'protobuf'], help="Which format of GAME MASTER to parse")
parser.add_argument('version', nargs='?', type=int, default=2, choices=[1, 2], help="Which version to parse")
cmdline_args = parser.parse_args()

gmformat = cmdline_args.format
gmVersion = cmdline_args.version


# Open the GAMER MASTER file
gmFile = open("GAME_MASTER-v{:d}.{:s}".format(gmVersion, gmformat.lower()), mode=('rb' if gmformat == 'protobuf' else 'r'))
gameMasterReader = GameMasterReader(gmFile, gmformat, "v{:d}".format(gmVersion))
decodedGameMaster = gameMasterReader.parse()

# Read translations
translations = {}
languages = ['en', 'ja', 'fr', 'es', 'de', 'it', 'ko', 'zh-tw', 'pt-br']
for langKey in languages:
    with open("in/translations-{:s}.txt".format(langKey), mode='r') as file:
        translation = json.loads(file.read())
        for k, v in translation.items():
            if k not in translations:
                translations[k] = {}
            translations[k][langKey] = v

# Form translations
with open('in/form-translations.json', mode='r') as file:
    formTranslations = json.loads(file.read())

# Legacy movesets. Constantly updated by maintaining 'in/legacy-moves.csv' and compile with './compile-helper-json.py'
with open('in/legacy-moves.json', mode='r') as file:
    legacyMoves = json.loads(file.read())
# Convert str to int idx
legacyMoves = {int(k):v for k,v in legacyMoves.items()}


def extractFriendshipLevel(extractFrom):
    m = re.search('FRIENDSHIP_LEVEL_([0-9]+)', extractFrom)
    friendshipLevel = m.group(1).lower()

    return friendshipLevel

# From https://stackoverflow.com/questions/38987/how-to-merge-two-dictionaries-in-a-single-expression
def mergeDicts(x, y):
    z = {}

    if isinstance(x, dict) and isinstance(y, dict):
        overlappingKeys = x.keys() & y.keys()
        for key in overlappingKeys:
            z[key] = mergeDicts(x[key], y[key])
        for key in x.keys() - overlappingKeys:
            z[key] = deepcopy(x[key])
        for key in y.keys() - overlappingKeys:
            z[key] = deepcopy(y[key])
    else:
        z = x if x is not None and y is None else y

    return z

def addPokemonToList(newPokemonId, newPokemon):
    global pokemons

    if newPokemonId not in pokemons:
        pokemons[newPokemonId] = []
    else:
        for eachPokemon in pokemons[newPokemonId]:
            # pprint('################### iteratePokemon ###################')
            # pprint(eachPokemon)

            # if newPokemonId == 3:
            #     pprint('################### END ###################')
            #     pprint(pokemons)
            #     exit(1)

            if eachPokemon['stats'] == newPokemon['stats'] and eachPokemon['quickMoves'] == newPokemon['quickMoves'] and eachPokemon['cinematicMoves'] == newPokemon['cinematicMoves']:
                formNameEn = newPokemon['formName']['en']
                for langKey in eachPokemon['formName'].keys():
                    eachPokemon['formName'][langKey] = "{:s}/{:s}".format(eachPokemon['formName'][langKey], (newPokemon['formName'][langKey] if langKey in newPokemon['formName'] else formNameEn))

                # pprint(pokemons)
                return

    pokemons[newPokemonId].append(newPokemon)


# Process messages in GAME_MASTER file
# First go over them and find all forms
forms = {}
for i in decodedGameMaster:
    if 'formSettings' in i:
        if 'forms' in i['formSettings']:
            form = i['formSettings']
            pokemonId = form['pokemon']

            if pokemonId not in forms:
                forms[pokemonId] = []

            forms[pokemonId] = [ pokeForm['form'] for pokeForm in form['forms'] ]

singleTplSettings = ['battleSettings', 'gymBadgeSettings', 'iapSettings', 'pokemonUpgrades', 'weatherBonusSettings', 'luckyPokemonSettings', 'exRaidSettings', 'encounterSettings', 'combatStatStageSettings', 'combatSettings', 'backgroundModeSettings', 'partyRecommendationSettings', 'onboardingV2Settings', 'combatLeagueSettings', 'buddyEncounterCameoSettings', 'buddyHungerSettings', 'buddySwapSettings', 'buddyWalkSettings', 'combatCompetitiveSeasonSettings', 'combatRankingProtoSettings', 'platypusRolloutSettings', 'vsSeekerClientSettings']
singleTplSpecialSettings = ['playerLevel', 'gymLevel', 'pokestopInvasionAvailabilitySettings']
multiTplSettingsKeyMap = {'questSettings': 'questType', 'weatherAffinities': 'weatherCondition', 'friendshipMilestoneSettings': 'friendshipLevel'}

moves = {}
combatMoveModifiers = {}
combatMoves = {}
pokemons = {}
items = {}
types = {}
badges = {}
gameSettings = {}
genderSettings = {}
playerLevels = {}
for i in decodedGameMaster:
    if 'moveSettings' in i:
        move = i['moveSettings']
        move['moveId'] = move['movementId']
        del move['movementId']
        move['name'] = move['movementName']
        del move['movementName']

        moveNameKey = 'move_name_{:04d}'.format(move['moveId'])
        if moveNameKey in translations:
            move['name'] = translations[moveNameKey]
        else:
            # m = re.search('V[0-9]+_MOVE_(.*)', move['moveId'])
            # moveName = m.group(1).replace('_FAST', '').replace('_', ' ').lower().title()
            moveName = move['name'].replace('_FAST', '').replace('_', ' ').lower().title()
            move['name'] = {'en': moveName}

        moves[move['moveId']] = move

    elif 'combatMove' in i:
        move = i['combatMove']
        move['moveId'] = move['uniqueId']
        del move['uniqueId']
        move['name'] = move['uniqueName']
        del move['uniqueName']

        moveNameKey = 'move_name_{:04d}'.format(move['moveId'])
        if moveNameKey in translations:
            move['name'] = translations[moveNameKey]
        else:
            # m = re.search('V[0-9]+_MOVE_(.*)', move['moveId'])
            # moveName = m.group(1).replace('_FAST', '').replace('_', ' ').lower().title()
            moveName = move['name'].replace('_FAST', '').replace('_', ' ').lower().title()
            move['name'] = {'en': moveName}

        # If it's a quick move, 'durationTurns' should be there, but it's missing if it's 1. So add it, but only for quick moves
        # It's a quick move if energyDelta is > 0 or it's move ID 242 (Transform), which does not add any energy
        if move['energyDelta'] > 0 or move['moveId'] == 242:
            move['durationTurns'] = move.get('durationTurns', 0)

        combatMoveModifiers[move['moveId']] = move

    elif 'pokemonSettings' in i:
        pokemon = i['pokemonSettings']
        pokemonId = pokemon['pokemonId']
        pokemon['name'] = pokemon['pokemonName']
        del pokemon['pokemonName']

        # Every pokemon that has a form (castform, alola, deoxys, ...) also have a no-form entry, which makes NO SENSE: Those mons don't exist without a form!
        # Even mons that have an alolan form now have three entries: normal, alolan and one without any form. the last one MAKES NO SENSE!
        # But Unown and Spinda only has one entry... no form entry... So the logic does not apply for Unown...
        # This 'if' will skip the useless entry and only look for the ones with a form
        if pokemonId not in (201, 327) and pokemonId in forms and ('form' not in pokemon or pokemon['form'] == 0):
            continue


        pokemonCategoryKey = 'pokemon_category_{:04d}'.format(pokemonId)
        pokemon['category'] = {'en': ''}
        if pokemonCategoryKey in translations:
            pokemon['category'] = translations[pokemonCategoryKey]

        pokemonDescKey = 'pokemon_desc_{:04d}'.format(pokemonId)
        pokemon['description'] = {'en': ''}
        if pokemonDescKey in translations:
            pokemon['description'] = translations[pokemonDescKey]

        if 'form' in pokemon:
            # pokemonName: 'TORNADUS'
            # formName: 'TORNADUS_INCARNATE'
            ## Will find: 'INCARNATE'
            m = re.search('{:s}_(.*)'.format(pokemon['name']), pokemon['formName'])

            tplFormName = None
            if m is not None:
                tplFormName = "form_{:s}".format(m.group(1)).lower()

            formName = None

            # First check if we have a translation for the full form name (e.g. 'RATTATA_NORMAL')
            if pokemon['formName'] in formTranslations:
                formName = deepcopy(formTranslations[pokemon['formName']])
            # If not, check if we have a partial form name (e.g. 'ALOLA' from 'RATTATA_ALOLA')
            elif tplFormName in translations:
                formName = deepcopy(translations[tplFormName])
            else:
                formName = {'en': tplFormName.replace('form_', '').replace('_', ' ').lower().title()}

            pokemon['formName'] = formName
            pokemon['pokemonFormId'] = "{:d}-{:d}".format(pokemonId, pokemon['form'])

        pokemonNameKey = 'pokemon_name_{:04d}'.format(pokemonId)
        if pokemonNameKey in translations:
            pokemon['name'] = translations[pokemonNameKey]
        else:
            pokemonName = pokemon['name'].replace('_male', '♂').replace('_female', '♀').replace('_', ' ').lower().title()
            pokemon['name'] = {'en': pokemonName}

        pokemonTypes = [pokemon['type']]
        pokemonTypeNames = [pokemon['typeName']]
        if 'type2' in pokemon:
            pokemonTypes.append(pokemon['type2'])
            pokemonTypeNames.append(pokemon['type2Name'])
            del pokemon['type2']
            del pokemon['type2Name']
        pokemon['types'] = pokemonTypes
        pokemon['typeNames'] = pokemonTypeNames
        del pokemon['type']
        del pokemon['typeName']

        addPokemonToList(pokemonId, pokemon)

    elif 'itemSettings' in i:
        item = i['itemSettings']
        item['name'] = item['itemName']
        del item['itemName']

        m = re.search('ITEM_(.*)', i['templateId'])

        itemName = m.group(1).lower()

        itemNameKey = 'item_{:s}_name'.format(itemName)
        if itemNameKey in translations:
            item['name'] = translations[itemNameKey]
        else:
            item['name'] = {'en': itemName.replace('_', ' ').title()}

        itemDescKey = 'item_{:s}_desc'.format(itemName)
        if itemDescKey in translations:
            item['description'] = translations[itemDescKey]
        else:
            item['description'] = {'en': ''}

        items[item['itemId']] = item

    elif 'typeEffective' in i:
        typeEffective = i['typeEffective']
        typeEffective['typeId'] = typeEffective['attackType']
        del typeEffective['attackType']
        typeEffective['name'] = typeEffective['attackTypeName']
        del typeEffective['attackTypeName']

        m = re.search('POKEMON_TYPE_(.*)', i['templateId'])
        typeName = m.group(1).replace('_', ' ').lower()

        typeNameKey = 'pokemon_type_{:s}'.format(typeName)
        if typeNameKey in translations:
            typeEffective['name'] = translations[typeNameKey]
        else:
            typeEffective['name'] = {'en': typeName.title()}

        types[typeEffective['typeId']] = typeEffective

    elif 'badgeSettings' in i:
        badge = i['badgeSettings']
        badge['badgeId'] = badge['badgeType']
        del badge['badgeType']
        badge['name'] = badge['badgeTypeName']
        del badge['badgeTypeName']

        m = re.search('BADGE_(.*)', i['templateId'])
        badgeName = m.group(1).lower()

        badgeNameKey = 'badge_{:s}_title'.format(badgeName)
        if badgeNameKey in translations:
            badge['name'] = translations[badgeNameKey]
        else:
            badge['name'] = {'en': badgeName.replace('_', ' ').title()}

        badgeDescKey = 'badge_{:s}'.format(badgeName)
        if badgeDescKey in translations:
            badge['description'] = translations[badgeDescKey].copy()
            badge['descriptionClean'] = translations[badgeDescKey].copy()
            for key, desc in badge['descriptionClean'].items():
                badgeDescClean = desc.replace('{0}', ' ').replace('{0:0.#}', ' ')
                badge['descriptionClean'][key] = " ".join(badgeDescClean.split())
        else:
            badge['description'] = {'en': ''}

        badges[badge['badgeId']] = badge

    elif 'genderSettings' in i:
        genderSetting = i['genderSettings']

        genderSettings[genderSetting['pokemon']] = {
            'femalePercent': genderSetting['gender'].get('femalePercent', 0),
            'malePercent': genderSetting['gender'].get('malePercent', 0),
            'genderlessPercent': genderSetting['gender'].get('genderlessPercent', 0)
        }

    # TODO: 'gymLevel'
    elif any(y in singleTplSettings + singleTplSpecialSettings + list(multiTplSettingsKeyMap.keys()) for y in i):
        templateId = i['templateId']
        del(i['templateId'])
        settingsKey = list(i.keys())[0]

        if settingsKey in singleTplSettings:
            gameSettings[settingsKey] = i[settingsKey]
        elif settingsKey in multiTplSettingsKeyMap.keys():
            if settingsKey not in gameSettings:
                gameSettings[settingsKey] = {}

            if settingsKey == 'friendshipMilestoneSettings':
                i[settingsKey]['friendshipLevel'] = extractFriendshipLevel(templateId)

            gameSettings[settingsKey][i[settingsKey][multiTplSettingsKeyMap[settingsKey]]] = i[settingsKey]
        elif 'playerLevel' in i:
            playerLevels = i['playerLevel']

            playerLevels['levels'] = {}
            idx = 1
            for requiredExp in playerLevels['requiredExperience']:
                playerLevels['levels'][idx] = {
                    'requiredExperience': requiredExp,
                    'cpMultiplier': playerLevels['cpMultiplier'][idx-1],
                    'rankNum': playerLevels['rankNum'][idx-1]
                }
                idx += 1

            del playerLevels['requiredExperience']
            del playerLevels['cpMultiplier']
            del playerLevels['rankNum']

            gameSettings['playerLevel'] = playerLevels
        # TODO
        # elif 'gymLevel' in i:
            # pprint(i)
            # exit(1)
        elif 'pokestopInvasionAvailabilitySettings' in i:
            if 'pokestopInvasionAvailabilitySettings' not in gameSettings:
                gameSettings['pokestopInvasionAvailabilitySettings'] = {}

            m = re.search('INVASION_AVAILABILITY_SETTINGS_(.*)', templateId)
            dayName = m.group(1)

            gameSettings['pokestopInvasionAvailabilitySettings'][dayName] = i['pokestopInvasionAvailabilitySettings']

for i in genderSettings:
    if i in pokemons:
        for j, pokemon in enumerate(pokemons[i]):
            pokemons[i][j]['genderPossibilities'] = genderSettings[i]

# Merge moves and combat move modifiers
combatMoves = mergeDicts(moves, combatMoveModifiers)
# Todo: Delete these keys in all items:
# del damageWindowEndMs
# del damageWindowStartMs
# del durationMs

with open('out/pokemon.json', 'w') as outfile:
    json.dump(pokemons, outfile, sort_keys=True)
with open('out/moves.json', 'w') as outfile:
    json.dump(moves, outfile, sort_keys=True)
with open('out/combat-moves.json', 'w') as outfile:
    json.dump(combatMoves, outfile, sort_keys=True)
with open('out/types.json', 'w') as outfile:
    json.dump(types, outfile, sort_keys=True)
with open('out/badges.json', 'w') as outfile:
    json.dump(badges, outfile, sort_keys=True)
with open('out/items.json', 'w') as outfile:
    json.dump(items, outfile, sort_keys=True)
with open('out/player-levels.json', 'w') as outfile:
    json.dump(playerLevels, outfile, sort_keys=True)
with open('out/game-settings.json', 'w') as outfile:
    json.dump(gameSettings, outfile, sort_keys=True)

with open('out/pokemon-base-stats.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=['id', 'pokemonFormId', 'name-en', 'name-ja', 'name-fr', 'name-es', 'name-de', 'name-it', 'name-ko', 'name-zh-tw', 'name-pt-br', 'form', 'hp', 'atk', 'def', 'type1', 'type2', 'legendary', 'mythical'])
    writer.writeheader()
    for pokemonId, pokemonForms in pokemons.items():
        for pokemon in pokemonForms:
            pokemonStats = {
                'id': pokemonId,
                'pokemonFormId': (pokemon['pokemonFormId'] if 'pokemonFormId' in pokemon else pokemonId),
                'name-en': pokemon['name']['en'],
                'name-ja': pokemon['name']['ja'] if 'ja' in pokemon['name'] else pokemon['name']['en'],
                'name-fr': pokemon['name']['fr'] if 'fr' in pokemon['name'] else pokemon['name']['en'],
                'name-es': pokemon['name']['es'] if 'es' in pokemon['name'] else pokemon['name']['en'],
                'name-de': pokemon['name']['de'] if 'de' in pokemon['name'] else pokemon['name']['en'],
                'name-it': pokemon['name']['it'] if 'it' in pokemon['name'] else pokemon['name']['en'],
                'name-ko': pokemon['name']['ko'] if 'ko' in pokemon['name'] else pokemon['name']['en'],
                'name-zh-tw': pokemon['name']['zh-tw'] if 'zh-tw' in pokemon['name'] else pokemon['name']['en'],
                'name-pt-br': pokemon['name']['pt-br'] if 'pt-br' in pokemon['name'] else pokemon['name']['en'],
                'form': (pokemon['formName']['en'] if 'form' in pokemon else None),
                'hp': pokemon['stats']['baseStamina'],
                'atk': pokemon['stats']['baseAttack'],
                'def': pokemon['stats']['baseDefense'],
                'type1': pokemon['types'][0],
                'type2': (pokemon['types'][1] if len(pokemon['types']) >= 2 else None),
                'legendary': ('Y' if 'rarity' in pokemon and pokemon['rarity'] == 1 else None),
                'mythical': ('Y' if 'rarity' in pokemon and pokemon['rarity'] == 2 else None)
            }
            writer.writerow(pokemonStats)

with open('out/types.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=['id', 'name-en', 'name-ja', 'name-fr', 'name-es', 'name-de', 'name-it', 'name-ko', 'name-zh-tw', 'name-pt-br'])
    writer.writeheader()
    for typeId, type in types.items():
        typeData = {
            'id': typeId,
            'name-en': type['name']['en'],
            'name-ja': type['name']['ja'] if 'ja' in pokemon['name'] else pokemon['name']['en'],
            'name-fr': type['name']['fr'] if 'fr' in pokemon['name'] else pokemon['name']['en'],
            'name-es': type['name']['es'] if 'es' in pokemon['name'] else pokemon['name']['en'],
            'name-de': type['name']['de'] if 'de' in pokemon['name'] else pokemon['name']['en'],
            'name-it': type['name']['it'] if 'it' in pokemon['name'] else pokemon['name']['en'],
            'name-ko': type['name']['ko'] if 'ko' in pokemon['name'] else pokemon['name']['en'],
            'name-zh-tw': type['name']['zh-tw'] if 'zh-tw' in pokemon['name'] else pokemon['name']['en'],
            'name-pt-br': type['name']['pt-br'] if 'pt-br' in pokemon['name'] else pokemon['name']['en']
        }
        writer.writerow(typeData)

with open('out/pokemon-quick-moves.csv', 'w') as quickCsvfile:
    with open('out/pokemon-charge-moves.csv', 'w') as chargeCsvfile:
        quickWriter = csv.DictWriter(quickCsvfile, fieldnames=['id', 'name-en', 'name-ja', 'name-fr', 'name-es', 'name-de', 'name-it', 'name-ko', 'name-zh-tw', 'name-pt-br', 'type', 'power', 'durationMs', 'energyDelta'])
        quickWriter.writeheader()
        chargeWriter = csv.DictWriter(chargeCsvfile, fieldnames=['id', 'name-en', 'name-ja', 'name-fr', 'name-es', 'name-de', 'name-it', 'name-ko', 'name-zh-tw', 'name-pt-br', 'type', 'power', 'durationMs', 'criticalChance', 'energyDelta'])
        chargeWriter.writeheader()

        for moveId, move in moves.items():
            energyDelta = move.get('energyDelta', 0)
            moveStats = {
                'id': moveId,
                'name-en': move['name']['en'],
                'name-ja': move['name']['ja'] if 'ja' in move['name'] else move['name']['en'],
                'name-fr': move['name']['fr'] if 'fr' in move['name'] else move['name']['en'],
                'name-es': move['name']['es'] if 'es' in move['name'] else move['name']['en'],
                'name-de': move['name']['de'] if 'de' in move['name'] else move['name']['en'],
                'name-it': move['name']['it'] if 'it' in move['name'] else move['name']['en'],
                'name-ko': move['name']['ko'] if 'ko' in move['name'] else move['name']['en'],
                'name-zh-tw': move['name']['zh-tw'] if 'zh-tw' in move['name'] else move['name']['en'],
                'name-pt-br': move['name']['pt-br'] if 'pt-br' in move['name'] else move['name']['en'],
                'type': move['pokemonType'],
                'power': move.get('power', 0),
                'durationMs': move['durationMs'],
                'energyDelta': (energyDelta*-1 if energyDelta < 0 else energyDelta)
            }

            # If energy is below 0 (= it costs energy): it's a charge move
            # Special: Struggle (133) is the only charge move that has 0 energy consumption :/
            if energyDelta < 0 or moveId == 133:
                moveStats['criticalChance'] = int(move.get('criticalChance', 0)*100)

                chargeWriter.writerow(moveStats)
            # If energy is above 0 (= it adds energy): it's a quick move
            # Special: Transform (242) is the only quick move that adds 0 energy :/
            else:
                quickWriter.writerow(moveStats)

with open('out/combat-quick-moves.csv', 'w') as cQuickCsvfile:
    with open('out/combat-charge-moves.csv', 'w') as cChargeCsvfile:
        quickWriter = csv.DictWriter(cQuickCsvfile, fieldnames=['id', 'name', 'type', 'power', 'energyDelta', 'durationTurns'])
        quickWriter.writeheader()
        chargeWriter = csv.DictWriter(cChargeCsvfile, fieldnames=['id', 'name', 'type', 'power', 'energyDelta', 'criticalChance'])
        chargeWriter.writeheader()
        for moveId, move in combatMoves.items():
            energyDelta = move.get('energyDelta', 0)
            moveStats = {
                'id': moveId,
                'name': move['name']['en'],
                'type': move['pokemonType'],
                'power': move.get('power', 0),
                'energyDelta': (energyDelta*-1 if energyDelta < 0 else energyDelta)
            }

            # If energy is below 0 (= it costs energy): it's a charge move
            # Special: Struggle (133) is the only charge move that has 0 energy consumption :/
            if energyDelta <= 0 or moveId == 133:
                moveStats['criticalChance'] = int(move.get('criticalChance', 0)*100)

                chargeWriter.writerow(moveStats)
            # If energy is above 0 (= it adds energy): it's a quick move
            # Special: Transform (242) is the only quick move that adds 0 energy :/
            else:
                moveStats['durationTurns'] = move['durationTurns']

                quickWriter.writerow(moveStats)

with open('out/pokemon-move-combinations.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=['id', 'pokemonFormId', 'fast', 'charge', 'fastIsLegacy', 'chargeIsLegacy'])
    writer.writeheader()
    moveCombis = []
    for pokemonId, pokemonForms in pokemons.items():
        for pokemon in pokemonForms:
            pokemonQuickMoves = pokemon['quickMoves'] if 'quickMoves' in pokemon else []
            pokemonCinematicMoves = pokemon['cinematicMoves'] if 'cinematicMoves' in pokemon else []
            pokemon['allQuickMoves'] = pokemonQuickMoves
            pokemon['allCinematicMoves'] = pokemonCinematicMoves
            if pokemonId in legacyMoves:
                # list(set()) is used to get unique values
                pokemon['allQuickMoves'] = list(set(pokemonQuickMoves + legacyMoves[pokemonId]['quickMoves']))
                pokemon['allCinematicMoves'] = list(set(pokemonCinematicMoves + legacyMoves[pokemonId]['cinematicMoves']))

            for quickMove in pokemon['allQuickMoves']:
                fastIsLegacy = 0
                # If the move is a legacy move but is not currently obtainable, it's considered legacy!
                if pokemonId in legacyMoves and quickMove in legacyMoves[pokemonId]['quickMoves'] and quickMove not in pokemonQuickMoves:
                    fastIsLegacy = 1

                for chargeMove in pokemon['allCinematicMoves']:
                    chargeIsLegacy = 0
                    # If the move is a legacy move but is not currently obtainable, it's considered legacy!
                    if pokemonId in legacyMoves and chargeMove in legacyMoves[pokemonId]['cinematicMoves'] and chargeMove not in pokemonCinematicMoves:
                        chargeIsLegacy = 1

                    moveCombi = {
                        'id': pokemonId,
                        'pokemonFormId': (pokemon['pokemonFormId'] if 'pokemonFormId' in pokemon else pokemonId),
                        'fast': quickMove,
                        'charge': chargeMove,
                        'fastIsLegacy': fastIsLegacy,
                        'chargeIsLegacy': chargeIsLegacy
                    }
                    writer.writerow(moveCombi)



'''
# Helper snippet to create the in/legacy-moves.json
with open('in/legacy-moves-in.json', mode='r') as file:
    legacyMovesJson = json.loads(file.read())
legacyMovesCsv = []
with open('in/legacy-moves.csv') as csvfile:
    reader = csv.DictReader(csvfile, dialect='excel-tab', fieldnames=['pokemonId', 'moveId', 'isQuickMove'])
    for row in reader:
        legacyMovesCsv.append(row)

for legacyMove in legacyMovesCsv:
    if legacyMove['isQuickMove'] == "1":
        legacyMovesJson[legacyMove['pokemonId']]['quickMoves'].append(legacyMove['moveId'])
    else:
        legacyMovesJson[legacyMove['pokemonId']]['cinematicMoves'].append(legacyMove['moveId'])

with open('in/legacy-moves.json', 'w') as outfile:
    json.dump(legacyMovesJson, outfile)

pprint(legacyMovesJson)
exit(1)
'''