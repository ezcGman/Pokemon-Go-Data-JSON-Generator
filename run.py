#!pgodatagen/bin/python

# TODO:
# further compare in detail what has been changed in json script compated to this
# commit, push

import json
import re

# from v0_73_1_pb2 import *
from pogoprotos.networking.responses.download_item_templates_response_pb2 import *
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import SerializeToJsonError
import csv
from pprint import pprint
from copy import deepcopy


# Read text CSVs
pokemonTexts = {}
with open('in/pokemon.txt') as csvfile:
    reader = csv.DictReader(csvfile, dialect='excel-tab', fieldnames=['key', 'en', 'ja', 'fr', 'es', 'de', 'it', 'ko', 'zh-tw', 'pt-br'])
    for row in reader:
        key = row['key']
        del row['key']
        pokemonTexts[key] = row

movesTexts = {}
with open('in/moves.txt') as csvfile:
    reader = csv.DictReader(csvfile, dialect='excel-tab', fieldnames=['key', 'en', 'ja', 'fr', 'es', 'de', 'it', 'ko', 'zh-tw', 'pt-br'])
    for row in reader:
        key = row['key']
        del row['key']
        movesTexts[key] = row

itemsTexts = {}
with open('in/items.txt') as csvfile:
    reader = csv.DictReader(csvfile, dialect='excel-tab', fieldnames=['key', 'en', 'ja', 'fr', 'es', 'de', 'it', 'ko', 'zh-tw', 'pt-br'])
    for row in reader:
        key = row['key']
        del row['key']
        itemsTexts[key] = row

generalTexts = {}
with open('in/general.txt') as csvfile:
    reader = csv.DictReader(csvfile, dialect='excel-tab', fieldnames=['key', 'en', 'ja', 'fr', 'es', 'de', 'it', 'ko', 'zh-tw', 'pt-br'])
    for row in reader:
        key = row['key']
        del row['key']
        generalTexts[key] = row
with open('in/gymsv2.txt') as csvfile:
    reader = csv.DictReader(csvfile, dialect='excel-tab', fieldnames=['key', 'en', 'ja', 'fr', 'es', 'de', 'it', 'ko', 'zh-tw', 'pt-br'])
    for row in reader:
        key = row['key']
        del row['key']
        generalTexts[key] = row

# Legacy movesets so far (last updated: 2018-01-18)
with open('in/legacy-moves.json', mode='r') as file:
    legacyMoves = json.loads(file.read())
# Convert str to int idx
legacyMoves = {int(k):v for k,v in legacyMoves.items()}

# Form translations
with open('in/form-translations.json', mode='r') as file:
    formTranslations = json.loads(file.read())

# Read GAME_MASTER file
with open('GAME_MASTER', mode='rb') as file: # b is important -> binary
    fileContent = file.read()

decodedGameMaster=DownloadItemTemplatesResponse()
decodedGameMaster.ParseFromString(fileContent)

def messageHasField(message, field):
    try:
        return message.HasField(field)
    except ValueError:
        return False

def extractFreindshipLevel(extractFrom):
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


# Process messages in GAME_MASTER file
# First go over them and find all forms
forms = {}
for i in decodedGameMaster.item_templates:
    if messageHasField(i, 'form_settings'):
        if hasattr(i.form_settings, 'forms') and len(i.form_settings.forms) > 0:
            pokemonId = i.form_settings.pokemon

            jsonObj = MessageToJson(i)
            formSettings = json.loads(jsonObj)['formSettings']

            if pokemonId not in forms:
                forms[pokemonId] = []
            for form in formSettings['forms']:
                forms[pokemonId].append(form['form'])

moves = {}
combatMoveModifiers = {}
combatMoves = {}
pokemons = {}
items = {}
types = {}
badges = {}
gameSettings = {}
genderSettings = {}
for i in decodedGameMaster.item_templates:
    # CHECKED
    if messageHasField(i, 'move_settings'):
        moveId = i.move_settings.movement_id
        moveType = i.move_settings.pokemon_type

        jsonObj = MessageToJson(i)
        move = json.loads(jsonObj)['moveSettings']

        moveNameKey = 'move_name_{:04d}'.format(moveId)
        if moveNameKey in movesTexts:
            move['name'] = movesTexts[moveNameKey]
        else:
            # m = re.search('V[0-9]+_MOVE_(.*)', move['movementId'])
            # moveName = m.group(1).replace('_FAST', '').replace('_', ' ').lower().title()
            moveName = move['movementId'].replace('_FAST', '').replace('_', ' ').lower().title()
            move['name'] = {'en': moveName}

        move['movementId'] = moveId
        move['pokemonType'] = moveType
        move['energyDelta'] = move.get('energyDelta', 0)

        moves[moveId] = move

    elif messageHasField(i, 'combat_move'):
        moveId = i.combat_move.unique_id
        moveType = i.combat_move.type

        jsonObj = MessageToJson(i)
        move = json.loads(jsonObj)['combatMove']

        moveNameKey = 'move_name_{:04d}'.format(moveId)
        if moveNameKey in movesTexts:
            move['name'] = movesTexts[moveNameKey]
        else:
            # m = re.search('V[0-9]+_MOVE_(.*)', move['uniqueId'])
            # moveName = m.group(1).replace('_FAST', '').replace('_', ' ').lower().title()
            moveName = move['uniqueId'].replace('_FAST', '').replace('_', ' ').lower().title()
            move['name'] = {'en': moveName}

        move['movementId'] = moveId
        move['pokemonType'] = moveType
        move['energyDelta'] = move.get('energyDelta', 0)

        # If it's a quick move, 'durationTurns' should be there, but it's missing if it's 1. So add it, but only for quick moves
        # It's a quick move if energyDelta is > 0 or it's move ID 242 (Transform), which does not add any energy
        if move['energyDelta'] > 0 or moveId == 242:
            move['durationTurns'] = move.get('durationTurns', 0)

        del move['uniqueId']
        del move['type']

        combatMoveModifiers[moveId] = move

    # CHECKED
    # WHERE IS LEGENDARY???
    elif messageHasField(i, 'pokemon_settings'):
        # The next section until the MessageToJson() call is done to force the translation of constants to their int vals
        # MessageToJson() translates constants to strings, so the field 'uniqueId' would not have intval 1 for Bulbasaur,
        # but string 'V0001_POKEMON_BULBASAUR'. So we first call all those properties with constant values to later overwrite
        # them in the dict coming out of json-loads(MessageToJson())

        pokemonId = i.pokemon_settings.pokemon_id
        familyId = i.pokemon_settings.family_id
        encounterType = i.pokemon_settings.encounter.movement_type

        # Every pokemon that has a form (castform, alola, deoxys, ...) also have a no-form entry, which makes NO SENSE: Those mons don't exist without a form!
        # Even mons that have an alolan form now have three entries: normal, alolan and one without any form. the last one MAKES NO SENSE!
        # But Unown and Spinda only has one entry... no form entry... So the logic does not apply for Unown...
        # This if will skip the useless entry and only look for the ones with a form
        if pokemonId not in (201, 327) and pokemonId in forms and (not hasattr(i.pokemon_settings, 'form') or i.pokemon_settings.form == 0):
            continue

        quickMoves = []
        for quickMove in i.pokemon_settings.quick_moves:
            quickMoves.append(quickMove)

        cinematicMoves = []
        for cinematicMove in i.pokemon_settings.cinematic_moves:
            cinematicMoves.append(cinematicMove)

        parentId = None
        if hasattr(i.pokemon_settings, 'parent_id') and i.pokemon_settings.parent_id > 0:
            parentId = i.pokemon_settings.parent_id

        pokemonTypes = [i.pokemon_settings.type]
        if hasattr(i.pokemon_settings, 'type_2') and i.pokemon_settings.type_2 > 0:
            pokemonTypes.append(i.pokemon_settings.type_2)

        rarity = None
        if hasattr(i.pokemon_settings, 'rarity') and i.pokemon_settings.rarity > 0:
            rarity = i.pokemon_settings.rarity

        buddySize = None
        if hasattr(i.pokemon_settings, 'buddy_size') and i.pokemon_settings.buddy_size > 0:
            buddySize = i.pokemon_settings.buddy_size

        evolutionIds = None
        if hasattr(i.pokemon_settings, 'evolution_ids') and len(i.pokemon_settings.evolution_ids) > 0:
            evolutionIds = []
            for evolutionId in i.pokemon_settings.evolution_ids:
                evolutionIds.append(evolutionId)

        evolutionBranch = None
        if hasattr(i.pokemon_settings, 'evolution_branch') and len(i.pokemon_settings.evolution_branch) > 0:
            evolutionBranch = []
            for evoBranch in i.pokemon_settings.evolution_branch:
                tmpEvoBranch = {
                    'evolution': evoBranch.evolution,
                    'candyCost': evoBranch.candy_cost
                }
                if evoBranch.evolution_item_requirement:
                    tmpEvoBranch['evolutionItemRequirement'] = evoBranch.evolution_item_requirement

                evolutionBranch.append(tmpEvoBranch)

        formId = None
        if hasattr(i.pokemon_settings, 'form') and i.pokemon_settings.form > 0:
            formId = i.pokemon_settings.form

        jsonObj = MessageToJson(i)
        pokemon = json.loads(jsonObj)['pokemonSettings']
        pokemonTplName = pokemon['pokemonId']

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
            m = re.search('V[0-9]+_POKEMON_(.*)', pokemonTplName)
            pokemonName = pokemonTplName.replace('_male', '♂').replace('_female', '♀').replace('_', ' ').lower().title()
            pokemon['name'] = {'en': pokemonName}

        pokemon['pokemonId'] = pokemonId
        pokemon['familyId'] = familyId
        pokemon['quickMoves'] = quickMoves
        pokemon['cinematicMoves'] = cinematicMoves
        pokemon['encounter']['movementType'] = encounterType

        if parentId is not None:
            pokemon['parentId'] = parentId
        if rarity is not None:
            pokemon['rarity'] = rarity
        if buddySize is not None:
            pokemon['buddySize'] = buddySize
        if evolutionIds is not None:
            pokemon['evolutionIds'] = evolutionIds
        if evolutionBranch is not None:
            pokemon['evolutionBranch'] = evolutionBranch
        if formId is not None:
            m = re.search('{:s}_(.*)'.format(pokemonTplName), pokemon['form'])
            tplFormName = None
            if m is not None:
                tplFormName = m.group(1)

            # First check if we have a translation for the full form name (e.g. 'RATTATA_NORMAL')
            formName = None
            if pokemon['form'] in formTranslations:
                formName = formTranslations[pokemon['form']]
            # If not, check if we have a partial form name (e.g. 'ALOLA' from 'RATTATA_ALOLA')
            elif tplFormName in formTranslations:
                formName = formTranslations[tplFormName]
            else:
                formName = {'en': tplFormName.replace('_', ' ').lower().title()}

            pokemon['form'] = formName
            pokemon['pokemonFormId'] = "{:d}-{:d}".format(pokemonId, formId)

        pokemon['types'] = pokemonTypes
        del pokemon['type']
        if hasattr(i.pokemon_settings, 'type_2') and i.pokemon_settings.type_2 > 0:
            del pokemon['type2']

        if pokemonId not in pokemons:
            pokemons[pokemonId] = []
        pokemons[pokemonId].append(pokemon)

    # CHECKED
    elif messageHasField(i, 'item_settings'):
        itemId = i.item_settings.item_id
        itemCategory = i.item_settings.category
        itemType = i.item_settings.item_type

        jsonObj = MessageToJson(i)
        itemTmp = json.loads(jsonObj)
        item = itemTmp['itemSettings']

        m = re.search('ITEM_(.*)', itemTmp['templateId'])
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

        item['itemId'] = itemId
        item['category'] = itemCategory
        item['itemType'] = itemType

        items[itemId] = item

    # CHECKED
    elif messageHasField(i, 'type_effective'):
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

        del(type['attackType'])
        type['typeId'] = typeId

        types[typeId] = type

    # CHECKED
    elif messageHasField(i, 'badge_settings'):
        badgeId = i.badge_settings.badge_type

        # No idea why a few badges have an int instead of an enum which then raises this error:
        # google.protobuf.json_format.SerializeToJsonError: Enum field contains an integer value which can not mapped to an enum value.
        try:
            jsonObj = MessageToJson(i)
        except SerializeToJsonError:
            pprint(i)
            continue

        badgeTmp = json.loads(jsonObj)
        badge = badgeTmp['badgeSettings']

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

    # CHECKED
    elif messageHasField(i, 'player_level'):
        jsonObj = MessageToJson(i)
        levelsTmp = json.loads(jsonObj)['playerLevel']

        playerLevels = {}
        idx = 1
        for requiredExp in levelsTmp['requiredExperience']:
            playerLevels[idx] = {
                'requiredExp': requiredExp,
                'cpMultiplier': levelsTmp['cpMultiplier'][idx-1],
                'rankNum': levelsTmp['rankNum'][idx-1]
            }
            idx += 1

    elif messageHasField(i, 'battle_settings') or messageHasField(i, 'gym_badge_settings') or messageHasField(i, 'gym_level') or messageHasField(i, 'iap_settings') or messageHasField(i, 'pokemon_upgrades') or messageHasField(i, 'quest_settings') or messageHasField(i, 'weather_affinities') or messageHasField(i, 'weather_bonus_settings') or messageHasField(i, 'encounter_settings') or messageHasField(i, 'friendship_milestone_settings') or messageHasField(i, 'lucky_pokemon_settings') or messageHasField(i, 'ex_raid_settings'):
        jsonObj = MessageToJson(i)
        settings = json.loads(jsonObj)

        templateId = settings['templateId']
        del(settings['templateId'])
        settingsKey = list(settings.keys())[0]
        if settingsKey in ['battleSettings', 'gymBadgeSettings', 'iapSettings', 'pokemonUpgrades', 'weatherBonusSettings', 'luckyPokemonSettings', 'exRaidSettings']:
            if settingsKey == 'exRaidSettings':
                settings[settingsKey]['minimumExRaidShareLevel'] = extractFreindshipLevel(settings[settingsKey]['minimumExRaidShareLevel'])
            gameSettings[settingsKey] = settings[settingsKey]
        elif settingsKey in ['questSettings', 'weatherAffinities', 'friendshipMilestoneSettings']:
            if settingsKey not in gameSettings:
                gameSettings[settingsKey] = []

            if settingsKey == 'friendshipMilestoneSettings':
                settings[settingsKey]['friendshipLevel'] = extractFreindshipLevel(templateId)

            gameSettings[settingsKey].append(settings[settingsKey])
        # elif 'gymLevel' in settings:
            # TODO
        # elif 'encounterSettings' in settings:
            # TODO

    elif messageHasField(i, 'gender_settings'):
        pokemonId = i.gender_settings.pokemon

        jsonObj = MessageToJson(i)
        genderSetting = json.loads(jsonObj)['genderSettings']

        genderSettings[pokemonId] = {
            'femalePercent': genderSetting['gender'].get('femalePercent', 0),
            'malePercent': genderSetting['gender'].get('malePercent', 0),
            'genderlessPercent': genderSetting['gender'].get('genderlessPercent', 0)
        }

    # Do not process these, they (seem to be) uninteresting / only for UX / rendering purposes, or we have them processed already
    elif messageHasField(i, 'move_sequence_settings') or messageHasField(i, 'camera') or messageHasField(i, 'avatar_customization') or messageHasField(i, 'iap_category_display') or messageHasField(i, 'pokemon_scale_settings') or messageHasField(i, 'iap_item_display') or messageHasField(i, 'form_settings'):
        continue

    else:
        print('########## NEW FIELD IN GAME MASTER ##########')
        jsonObj = MessageToJson(i)
        newField = json.loads(jsonObj)
        pprint(newField)

        # for field, value in i.ListFields():
        #     pprint(field.name)

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
    json.dump(pokemons, outfile)
with open('out/moves.json', 'w') as outfile:
    json.dump(moves, outfile)
with open('out/combat-moves.json', 'w') as outfile:
    json.dump(combatMoves, outfile)
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
    writer = csv.DictWriter(csvfile, fieldnames=['id', 'pokemonFormId', 'name', 'form', 'hp', 'atk', 'def', 'type1', 'type2', 'legendary'])
    writer.writeheader()
    for pokemonId, pokemonForms in pokemons.items():
        for pokemon in pokemonForms:
            pokemonStats = {
                'id': pokemonId,
                'pokemonFormId': (pokemon['pokemonFormId'] if 'pokemonFormId' in pokemon else pokemonId),
                'name': pokemon['name']['en'],
                'form': (pokemon['form']['en'] if 'form' in pokemon else None),
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
        quickWriter = csv.DictWriter(quickCsvfile, fieldnames=['id', 'name', 'type', 'power', 'durationMs', 'energyDelta'])
        quickWriter.writeheader()
        chargeWriter = csv.DictWriter(chargeCsvfile, fieldnames=['id', 'name', 'type', 'power', 'durationMs', 'criticalChance', 'energyDelta'])
        chargeWriter.writeheader()
        for moveId, move in moves.items():
            energyDelta = move.get('energyDelta', 0)
            moveStats = {
                'id': moveId,
                'name': move['name']['en'],
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
            if energyDelta < 0 or moveId == 133:
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
            if pokemonId in legacyMoves:
                pokemon['quickMoves'] = pokemon['quickMoves'] + legacyMoves[pokemonId]['quickMoves']
                pokemon['cinematicMoves'] = pokemon['cinematicMoves'] + legacyMoves[pokemonId]['cinematicMoves']

            for quickMove in pokemon['quickMoves']:
                fastIsLegacy = 0
                if pokemonId in legacyMoves and quickMove in legacyMoves[pokemonId]['quickMoves']:
                    fastIsLegacy = 1

                for chargeMove in pokemon['cinematicMoves']:
                    chargeIsLegacy = 0
                    if pokemonId in legacyMoves and chargeMove in legacyMoves[pokemonId]['cinematicMoves']:
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
