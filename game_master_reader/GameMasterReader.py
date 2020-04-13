from pogoprotos.networking.responses.download_item_templates_response_pb2 import *
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import SerializeToJsonError

# Needed for JSON parsing
from pogoprotos.enums.badge_type_pb2 import *
from pogoprotos.enums.buddy_size_pb2 import *
from pogoprotos.enums.form_pb2 import *
from pogoprotos.enums.pokemon_anim_pb2 import *
from pogoprotos.enums.pokemon_id_pb2 import *
from pogoprotos.enums.pokemon_family_id_pb2 import *
from pogoprotos.enums.pokemon_move_pb2 import *
from pogoprotos.enums.pokemon_movement_type_pb2 import *
from pogoprotos.enums.pokemon_rarity_pb2 import *
from pogoprotos.enums.pokemon_type_pb2 import *
from pogoprotos.inventory.item.item_id_pb2 import *

from pprint import pprint
import json
import re


class GameMasterReader:
    gmFileIo = None
    gmFormats = ["json", "protobuf"]
    gmVersions = {"json": ["v1", "v2"], "protobuf": ["v1"]}
    gmFormat = None
    gmVersion = None

    def __init__(self, gmFileIo, gmFormat="protobuf", gmVersion="v1"):
        self.gmFileIo = gmFileIo

        if gmFormat not in self.gmFormats:
            raise Exception("Unsupported format. 'gmFormat' must be one of: {:s}".format(", ".join(self.gmFormats)))
        self.gmFormat = gmFormat

        if gmVersion not in self.gmVersions[gmFormat]:
            raise Exception("Unsupported version for '{:s}'. 'gmVersion' must be one of: {:s}".format(gmFormat, ", ".join(self.gmVersions)))
        self.gmVersion = gmVersion

    def parse(self):
        if self.gmFormat == "protobuf":
            return self.parseProtobuf()
        elif self.gmFormat == "json":
            return self.parseJson()

    def parseProtobuf(self):
        if self.gmFileIo.mode != "rb":
            raise Exception("FileIO must be binary read (rb)")

        with self.gmFileIo:
            fileContent = self.gmFileIo.read()

        decodedGameMaster=DownloadItemTemplatesResponse()
        decodedGameMaster.ParseFromString(fileContent)

        itemTemplates = []
        for i in decodedGameMaster.item_templates:
            if self.messageHasField(i, 'pokemon_settings'):
                # The next section until the MessageToJson() call is done to force the translation of constants to their int vals
                # MessageToJson() translates constants to strings, so the field 'uniqueId' would not have intval 1 for Bulbasaur,
                # but string 'V0001_POKEMON_BULBASAUR'. So we first call all those properties with constant values to later overwrite
                # them in the dict coming out of json-loads(MessageToJson())
                pokemonId = i.pokemon_settings.pokemon_id
                type1 = i.pokemon_settings.type
                type2 = None
                if hasattr(i.pokemon_settings, 'type_2') and i.pokemon_settings.type_2 > 0:
                    type2 = i.pokemon_settings.type_2
                quickMoves = None
                if hasattr(i.pokemon_settings, 'quick_moves') and len(i.pokemon_settings.quick_moves) > 0:
                    quickMoves = [ quickMove for quickMove in i.pokemon_settings.quick_moves ]
                cinematicMoves = None
                if hasattr(i.pokemon_settings, 'cinematic_moves') and len(i.pokemon_settings.cinematic_moves) > 0:
                    cinematicMoves = [ cinematicMove for cinematicMove in i.pokemon_settings.cinematic_moves ]
                evolutionIds = None
                if hasattr(i.pokemon_settings, 'evolution_ids') and len(i.pokemon_settings.evolution_ids) > 0:
                    evolutionIds = [ evolutionId for evolutionId in i.pokemon_settings.evolution_ids ]
                familyId = i.pokemon_settings.family_id
                formId = None
                if hasattr(i.pokemon_settings, 'form') and i.pokemon_settings.form > 0:
                    formId = i.pokemon_settings.form
                buddySize = None
                if hasattr(i.pokemon_settings, 'buddy_size') and i.pokemon_settings.buddy_size > 0:
                    buddySize = i.pokemon_settings.buddy_size
                rarity = None
                if hasattr(i.pokemon_settings, 'rarity') and i.pokemon_settings.rarity > 0:
                    rarity = i.pokemon_settings.rarity
                encounterMoveType = None
                if hasattr(i.pokemon_settings.encounter, 'movement_type') and i.pokemon_settings.encounter.movement_type > 0:
                    encounterMoveType = i.pokemon_settings.encounter.movement_type

                evolutionBranch = None
                if hasattr(i.pokemon_settings, 'evolution_branch') and len(i.pokemon_settings.evolution_branch) > 0:
                    evolutionBranch = i.pokemon_settings.evolution_branch

                jsonObj = MessageToJson(i)
                pokemon = json.loads(jsonObj)

                pokemon['pokemonSettings']['pokemonName'] = pokemon['pokemonSettings']['pokemonId']
                pokemon['pokemonSettings']['pokemonId'] = pokemonId
                pokemon['pokemonSettings']['typeName'] = pokemon['pokemonSettings']['type']
                pokemon['pokemonSettings']['type'] = type1
                if type2 is not None:
                    pokemon['pokemonSettings']['type2Name'] = pokemon['pokemonSettings']['type2']
                    pokemon['pokemonSettings']['type2'] = type2
                if quickMoves is not None:
                    pokemon['pokemonSettings']['quickMoveNames'] = pokemon['pokemonSettings']['quickMoves']
                    pokemon['pokemonSettings']['quickMoves'] = quickMoves
                if cinematicMoves is not None:
                    pokemon['pokemonSettings']['cinematicMoveNames'] = pokemon['pokemonSettings']['cinematicMoves']
                    pokemon['pokemonSettings']['cinematicMoves'] = cinematicMoves
                if evolutionIds is not None:
                    pokemon['pokemonSettings']['evolutionNames'] = pokemon['pokemonSettings']['evolutionIds']
                    pokemon['pokemonSettings']['evolutionIds'] = evolutionIds
                pokemon['pokemonSettings']['familyName'] = pokemon['pokemonSettings']['familyId']
                # Determine unknown forms
                if pokemon['pokemonSettings']['familyId'] == familyId:
                    print("Unknown family: (templateId: '{:s}', familyId: '{:d}')".format(i.template_id, familyId))
                pokemon['pokemonSettings']['familyId'] = familyId
                if formId is not None:
                    # Determine unknown forms
                    if pokemon['pokemonSettings']['form'] == formId:
                        print("Unknown form: (templateId: '{:s}', formId: '{:d}')".format(i.template_id, formId))

                    pokemon['pokemonSettings']['formName'] = pokemon['pokemonSettings']['form']
                    pokemon['pokemonSettings']['form'] = formId
                if buddySize is not None:
                    pokemon['pokemonSettings']['buddySizeName'] = pokemon['pokemonSettings']['buddySize']
                    pokemon['pokemonSettings']['buddySize'] = buddySize
                if rarity is not None:
                    pokemon['pokemonSettings']['rarityName'] = pokemon['pokemonSettings']['rarity']
                    pokemon['pokemonSettings']['rarity'] = rarity
                if encounterMoveType is not None:
                    pokemon['pokemonSettings']['encounter']['movementTypeName'] = pokemon['pokemonSettings']['encounter']['movementType']
                    pokemon['pokemonSettings']['encounter']['movementType'] = encounterMoveType
                if evolutionBranch is not None:
                    # Note: There is a slight chance that the order of the list after converting it to JSON has changed! So there is the possibility of a bug here!
                    for j, evoBranch in enumerate(evolutionBranch):
                        # Usually, there should be no need to check for this field, as it must always be there. But currently DARMANITAN (#555) is bugged and has candy cost, but no evolution...
                        if hasattr(evoBranch, 'evolution') and evoBranch.evolution > 0:
                            pokemon['pokemonSettings']['evolutionBranch'][j]['evolutionName'] = pokemon['pokemonSettings']['evolutionBranch'][j]['evolution']
                            pokemon['pokemonSettings']['evolutionBranch'][j]['evolution'] = evoBranch.evolution
                        if hasattr(evoBranch, 'form') and evoBranch.form > 0:
                            pokemon['pokemonSettings']['evolutionBranch'][j]['formName'] = pokemon['pokemonSettings']['evolutionBranch'][j]['form']
                            pokemon['pokemonSettings']['evolutionBranch'][j]['form'] = evoBranch.form
                        if hasattr(evoBranch, 'evolution_item_requirement') and evoBranch.evolution_item_requirement > 0:
                            pokemon['pokemonSettings']['evolutionBranch'][j]['evolutionItemRequirementName'] = pokemon['pokemonSettings']['evolutionBranch'][j]['evolutionItemRequirement']
                            pokemon['pokemonSettings']['evolutionBranch'][j]['evolutionItemRequirement'] = evoBranch.evolution_item_requirement


                itemTemplates.append(pokemon)
                # pprint(pokemon)

            elif self.messageHasField(i, 'gender_settings'):
                pokemonId = i.gender_settings.pokemon

                jsonObj = MessageToJson(i)
                genderSetting = json.loads(jsonObj)

                genderSetting['genderSettings']['pokemonName'] = genderSetting['genderSettings']['pokemon']
                genderSetting['genderSettings']['pokemon'] = pokemonId

                itemTemplates.append(genderSetting)
                # pprint(genderSetting)

            elif self.messageHasField(i, 'form_settings'):
                forms = None
                if hasattr(i.form_settings, 'forms') and len(i.form_settings.forms) > 0:
                    forms = i.form_settings.forms
                pokemonId = i.form_settings.pokemon

                jsonObj = MessageToJson(i)
                formSetting = json.loads(jsonObj)

                if forms is not None:
                    # Note: There is a slight chance that the order of the list after converting it to JSON has changed! So there is the possibility of a bug here!
                    for j, form in enumerate(forms):
                        formSetting['formSettings']['forms'][j]['formName'] = formSetting['formSettings']['forms'][j]['form']
                        formSetting['formSettings']['forms'][j]['form'] = form.form
                formSetting['formSettings']['pokemonName'] = formSetting['formSettings']['pokemon']
                formSetting['formSettings']['pokemon'] = pokemonId

                itemTemplates.append(formSetting)
                # pprint(formSetting)

            elif self.messageHasField(i, 'type_effective'):
                typeId = i.type_effective.attack_type

                jsonObj = MessageToJson(i)
                typeEffective = json.loads(jsonObj)

                typeEffective['typeEffective']['attackTypeName'] = typeEffective['typeEffective']['attackType']
                typeEffective['typeEffective']['attackType'] = typeId

                itemTemplates.append(typeEffective)
                # pprint(typeEffective)

            elif self.messageHasField(i, 'move_settings'):
                animationId = i.move_settings.animation_id
                moveId = i.move_settings.movement_id
                moveType = i.move_settings.pokemon_type

                jsonObj = MessageToJson(i)
                move = json.loads(jsonObj)

                move['moveSettings']['animationName'] = move['moveSettings']['animationId']
                move['moveSettings']['animationId'] = animationId
                move['moveSettings']['movementName'] = move['moveSettings']['movementId']

                if move['moveSettings']['movementId'] == moveId:
                    print("Unknown move: (templateId: '{:s}', moveId: '{:d}')".format(i.template_id, moveId))
                move['moveSettings']['movementId'] = moveId
                move['moveSettings']['pokemonTypeName'] = move['moveSettings']['pokemonType']
                move['moveSettings']['pokemonType'] = moveType

                move['moveSettings']['energyDelta'] = move['moveSettings'].get('energyDelta', 0)

                itemTemplates.append(move)
                # pprint(move)

            elif self.messageHasField(i, 'combat_move'):
                moveId = i.combat_move.unique_id
                moveType = i.combat_move.type

                jsonObj = MessageToJson(i)
                move = json.loads(jsonObj)

                move['combatMove']['uniqueName'] = move['combatMove']['uniqueId']
                move['combatMove']['uniqueId'] = moveId
                move['combatMove']['typeName'] = move['combatMove']['type']
                move['combatMove']['type'] = moveType

                move['combatMove']['energyDelta'] = move['combatMove'].get('energyDelta', 0)

                itemTemplates.append(move)
                # pprint(move)

            elif self.messageHasField(i, 'item_settings'):
                itemId = i.item_settings.item_id
                itemCategory = i.item_settings.category
                itemType = i.item_settings.item_type

                jsonObj = MessageToJson(i)
                item = json.loads(jsonObj)
                item['item'] = item['itemSettings'].copy()
                del item['itemSettings']

                item['item']['itemName'] = item['item']['itemId']

                if item['item']['itemId'] == itemId:
                    print("Unknown item: (templateId: '{:s}', itemId: '{:d}')".format(i.template_id, itemId))
                item['item']['itemId'] = itemId
                item['item']['categoryName'] = item['item']['category']
                item['item']['category'] = itemCategory
                item['item']['itemTypeName'] = item['item']['itemType']
                item['item']['itemType'] = itemType

                itemTemplates.append(item)
                # pprint(item)

            elif self.messageHasField(i, 'badge_settings'):
                badgeId = i.badge_settings.badge_type

                jsonObj = MessageToJson(i)
                badge = json.loads(jsonObj)
                badge['badge'] = badge['badgeSettings'].copy()
                del badge['badgeSettings']

                badge['badge']['badgeTypeName'] = badge['badge']['badgeType']

                if badge['badge']['badgeType'] == badgeId:
                    print("Unknown badge: (templateId: '{:s}', badgeId: '{:d}')".format(i.template_id, badgeId))
                badge['badge']['badgeType'] = badgeId

                itemTemplates.append(badge)
                # pprint(badge)

            elif self.messageHasField(i, 'weather_affinities'):
                pokemonTypes = [ pokemonType for pokemonType in i.weather_affinities.pokemon_type ]
                weatherCondition = i.weather_affinities.weather_condition

                jsonObj = MessageToJson(i)
                weatherAffinity = json.loads(jsonObj)

                weatherAffinity['weatherAffinities']['weatherConditionName'] = weatherAffinity['weatherAffinities']['weatherCondition']
                weatherAffinity['weatherAffinities']['weatherCondition'] = weatherCondition
                weatherAffinity['weatherAffinities']['pokemonTypeNames'] = weatherAffinity['weatherAffinities']['pokemonType']
                weatherAffinity['weatherAffinities']['pokemonType'] = pokemonTypes

                itemTemplates.append(weatherAffinity)
                # pprint(weatherAffinity)

            elif self.messageHasField(i, 'ex_raid_settings'):
                minShareLvl = i.ex_raid_settings.minimum_ex_raid_share_level

                jsonObj = MessageToJson(i)
                exRaidSettings = json.loads(jsonObj)

                exRaidSettings['exRaidSettings']['minimumExRaidShareLevelName'] = exRaidSettings['exRaidSettings']['minimumExRaidShareLevel']
                exRaidSettings['exRaidSettings']['minimumExRaidShareLevel'] = minShareLvl

                itemTemplates.append(exRaidSettings)
                # pprint(exRaidSettings)

            elif self.messageHasField(i, 'friendship_milestone_settings'):
                unlockedTradings = [ unlockedTrading for unlockedTrading in i.friendship_milestone_settings.unlocked_trading ]

                jsonObj = MessageToJson(i)
                friendshipMilestone = json.loads(jsonObj)

                friendshipMilestone['friendshipMilestoneSettings']['unlockedTradingNames'] = friendshipMilestone['friendshipMilestoneSettings']['unlockedTrading']
                friendshipMilestone['friendshipMilestoneSettings']['unlockedTrading'] = unlockedTradings

                itemTemplates.append(friendshipMilestone)
                # pprint(friendshipMilestone)

            elif self.messageHasField(i, 'quest_settings'):
                questType = i.quest_settings.quest_type

                jsonObj = MessageToJson(i)
                quest = json.loads(jsonObj)

                quest['questSettings']['questTypeName'] = quest['questSettings']['questType']
                quest['questSettings']['questType'] = questType

                itemTemplates.append(quest)
                # pprint(quest)

            elif self.messageHasField(i, 'iap_item_display'):
                category = i.iap_item_display.category

                jsonObj = MessageToJson(i)
                iapItemDisplay = json.loads(jsonObj)

                iapItemDisplay['iapItemDisplay']['categoryName'] = iapItemDisplay['iapItemDisplay']['category']
                iapItemDisplay['iapItemDisplay']['category'] = category

                itemTemplates.append(iapItemDisplay)
                # pprint(iapItemDisplay)

            elif self.messageHasField(i, 'avatar_customization'):
                avatarType = None
                if hasattr(i.avatar_customization, 'avatar_type') and i.avatar_customization.avatar_type > 0:
                    avatarType = i.avatar_customization.avatar_type
                slots = [ slot for slot in i.avatar_customization.slot ]
                unlockType = i.avatar_customization.unlock_type
                unlockBadgeType = None
                if hasattr(i.avatar_customization, 'unlock_badge_type') and i.avatar_customization.unlock_badge_type > 0:
                    unlockBadgeType = i.avatar_customization.unlock_badge_type

                jsonObj = MessageToJson(i)
                avatarCustomization = json.loads(jsonObj)

                if avatarType is not None:
                    avatarCustomization['avatarCustomization']['avatarTypeName'] = avatarCustomization['avatarCustomization']['avatarType']
                    avatarCustomization['avatarCustomization']['avatarType'] = avatarType
                avatarCustomization['avatarCustomization']['slotNames'] = avatarCustomization['avatarCustomization']['slot']
                avatarCustomization['avatarCustomization']['slot'] = slots
                avatarCustomization['avatarCustomization']['unlockTypeName'] = avatarCustomization['avatarCustomization']['unlockType']
                avatarCustomization['avatarCustomization']['unlockType'] = unlockType
                if unlockBadgeType is not None:
                    avatarCustomization['avatarCustomization']['unlockBadgeTypeName'] = avatarCustomization['avatarCustomization']['unlockBadgeType']
                    avatarCustomization['avatarCustomization']['unlockBadgeType'] = unlockBadgeType

                itemTemplates.append(avatarCustomization)
                # pprint(avatarCustomization)

            elif self.messageHasField(i, 'camera'):
                interpolations = [ interpolation for interpolation in i.camera.interpolation ]
                targetTypes = [ targetType for targetType in i.camera.target_type ]

                jsonObj = MessageToJson(i)
                camera = json.loads(jsonObj)

                camera['camera']['interpolationNames'] = camera['camera']['interpolation']
                camera['camera']['interpolation'] = interpolations
                camera['camera']['targetTypeNames'] = camera['camera']['targetType']
                camera['camera']['targetType'] = targetTypes

                itemTemplates.append(camera)
                # pprint(camera)

            elif self.messageHasField(i, 'pokemon_scale_settings'):
                pokemonScaleMode = None
                if hasattr(i.pokemon_scale_settings, 'pokemon_scale_mode') and i.pokemon_scale_settings.pokemon_scale_mode > 0:
                    pokemonScaleMode = i.pokemon_scale_settings.pokemon_scale_mode

                jsonObj = MessageToJson(i)
                scaleSetting = json.loads(jsonObj)

                if pokemonScaleMode is not None:
                    scaleSetting['pokemonScaleSettings']['pokemonScaleModeName'] = scaleSetting['pokemonScaleSettings']['pokemonScaleMode']
                    scaleSetting['pokemonScaleSettings']['pokemonScaleMode'] = pokemonScaleMode

                itemTemplates.append(scaleSetting)
                # pprint(scaleSetting)

            elif self.messageHasField(i, 'iap_category_display'):
                category = i.iap_category_display.category

                jsonObj = MessageToJson(i)
                iapCategoryDisplay = json.loads(jsonObj)

                iapCategoryDisplay['iapCategoryDisplay']['categoryName'] = iapCategoryDisplay['iapCategoryDisplay']['category']
                iapCategoryDisplay['iapCategoryDisplay']['category'] = category

                itemTemplates.append(iapCategoryDisplay)
                # pprint(iapCategoryDisplay)

            elif self.messageHasField(i, 'beluga_pokemon_whitelist'):
                costumesAllowed = [ costumeAllowed for targetType in i.camera.target_type ]
                additionalPokemonAllowed = [ additionalPokemon for targetType in i.camera.target_type ]

                jsonObj = MessageToJson(i)
                belugaPokemonWhitelist = json.loads(jsonObj)

                belugaPokemonWhitelist['belugaPokemonWhitelist']['costumesAllowedNames'] = belugaPokemonWhitelist['belugaPokemonWhitelist']['costumesAllowed']
                belugaPokemonWhitelist['belugaPokemonWhitelist']['costumesAllowed'] = costumesAllowed
                belugaPokemonWhitelist['belugaPokemonWhitelist']['additionalPokemonAllowedNames'] = belugaPokemonWhitelist['belugaPokemonWhitelist']['additionalPokemonAllowed']
                belugaPokemonWhitelist['belugaPokemonWhitelist']['additionalPokemonAllowed'] = additionalPokemonAllowed

                itemTemplates.append(belugaPokemonWhitelist)
                # pprint(belugaPokemonWhitelist)

            # YES, capital 'S'!!!
            elif self.messageHasField(i, 'buddy_activity_Settings'):
                activity = i.buddy_activity_Settings.activity
                activityCategory = i.buddy_activity_Settings.activity_category

                jsonObj = MessageToJson(i)
                buddyActivity = json.loads(jsonObj)

                buddyActivity['buddyActivitySettings']['activityName'] = buddyActivity['buddyActivitySettings']['activity']
                buddyActivity['buddyActivitySettings']['activity'] = activity
                buddyActivity['buddyActivitySettings']['activityCategoryName'] = buddyActivity['buddyActivitySettings']['activityCategory']
                buddyActivity['buddyActivitySettings']['activityCategory'] = activityCategory

                itemTemplates.append(buddyActivity)
                # pprint(buddyActivity)

            elif self.messageHasField(i, 'buddy_activity_category_settings'):
                activityCategory = i.buddy_activity_category_settings.activity_category

                jsonObj = MessageToJson(i)
                buddyActivityCategory = json.loads(jsonObj)

                buddyActivityCategory['buddyActivityCategorySettings']['activityCategoryName'] = buddyActivityCategory['buddyActivityCategorySettings']['activityCategory']
                buddyActivityCategory['buddyActivityCategorySettings']['activityCategory'] = activityCategory

                itemTemplates.append(buddyActivityCategory)
                # pprint(buddyActivityCategory)

            elif self.messageHasField(i, 'buddy_level_settings'):
                level = i.buddy_level_settings.level
                unlockedTraits = None
                if hasattr(i.buddy_level_settings, 'unlocked_traits') and len(i.buddy_level_settings.unlocked_traits) > 0:
                    unlockedTraits = [ unlockedTrait for unlockedTrait in i.buddy_level_settings.unlocked_traits ]

                jsonObj = MessageToJson(i)
                buddyLevel = json.loads(jsonObj)

                buddyLevel['buddyLevelSettings']['levelName'] = buddyLevel['buddyLevelSettings']['level']
                buddyLevel['buddyLevelSettings']['level'] = level
                if unlockedTraits is not None:
                    buddyLevel['buddyLevelSettings']['unlockedTraitNames'] = buddyLevel['buddyLevelSettings']['unlockedTraits']
                    buddyLevel['buddyLevelSettings']['unlockedTraits'] = unlockedTraits

                itemTemplates.append(buddyLevel)
                # pprint(buddyLevel)

            elif self.messageHasField(i, 'combat_type'):
                theType = i.combat_type.type

                jsonObj = MessageToJson(i)
                combatType = json.loads(jsonObj)

                combatType['combatType']['typeName'] = combatType['combatType']['type']
                combatType['combatType']['type'] = theType

                itemTemplates.append(combatType)
                # pprint(combatType)

            elif self.messageHasField(i, 'onboarding_v2_settings'):
                pokedexIds = [ pokedexId for pokedexId in i.onboarding_v2_settings.pokedex_id ]

                jsonObj = MessageToJson(i)
                v2Settings = json.loads(jsonObj)

                v2Settings['onboardingV2Settings']['pokedexName'] = v2Settings['onboardingV2Settings']['pokedexId']
                v2Settings['onboardingV2Settings']['pokedexId'] = pokedexIds

                itemTemplates.append(v2Settings)
                # pprint(v2Settings)

            elif self.messageHasField(i, 'party_recommendation_settings'):
                theMode = i.party_recommendation_settings.mode

                jsonObj = MessageToJson(i)
                partySettings = json.loads(jsonObj)

                partySettings['partyRecommendationSettings']['modeName'] = partySettings['partyRecommendationSettings']['mode']
                partySettings['partyRecommendationSettings']['mode'] = theMode

                itemTemplates.append(partySettings)
                # pprint(partySettings)

            elif self.messageHasField(i, 'smeargle_moves_settings'):
                cinematicMoves = [ cinematicMove for cinematicMove in i.smeargle_moves_settings.cinematic_moves ]
                quickMoves = [ quickMove for quickMove in i.smeargle_moves_settings.quick_moves ]

                jsonObj = MessageToJson(i)
                smeargleMoves = json.loads(jsonObj)

                smeargleMoves['smeargleMovesSettings']['cinematicMoveNames'] = smeargleMoves['smeargleMovesSettings']['cinematicMoves']
                smeargleMoves['smeargleMovesSettings']['cinematicMoves'] = cinematicMoves
                smeargleMoves['smeargleMovesSettings']['quickMoveNames'] = smeargleMoves['smeargleMovesSettings']['quickMoves']
                smeargleMoves['smeargleMovesSettings']['quickMoves'] = quickMoves

                itemTemplates.append(smeargleMoves)
                # pprint(smeargleMoves)

            # TODO
            elif self.messageHasField(i, 'combat_league'):
                itemTemplates.append(json.loads(MessageToJson(i)))
                # pprint(i)

            # TODO
            elif self.messageHasField(i, 'combat_npc_trainer'):
                itemTemplates.append(json.loads(MessageToJson(i)))
                # pprint(i)

            else:
                # Currently these: 'background_mode_settings', 'battle_settings', 'buddy_encounter_cameo_settings', 'invasion_npc_display_settings', 'combat_league_settings', 'buddy_swap_settings', 'combat_competitive_season_settings', 'combat_ranking_proto_settings', 'combat_settings', 'combat_stat_stage_settings', 'encounter_settings', 'gym_badge_settings', 'gym_level', 'iap_settings', 'lucky_pokemon_settings', 'player_level', 'pokecoin_purchase_display_gmt', 'pokemon_upgrades', 'combat_npc_personality', 'vs_seeker_client_settings', 'weather_bonus_settings', 'adventure_sync_v2_gmt', 'move_sequence_settings'
                itemTemplates.append(json.loads(MessageToJson(i)))

        return itemTemplates

    def messageHasField(self, message, field):
        try:
            return message.HasField(field)
        except ValueError:
            return False

    def parseJson(self):
        with self.gmFileIo:
            fileContent = self.gmFileIo.read()

        decodedGameMaster = json.loads(fileContent)

        itemTemplates = None
        if self.gmVersion == "v1":
            itemTemplates = decodedGameMaster
        elif self.gmVersion == "v2":
            itemTemplates = []
            for i in decodedGameMaster:
                if 'templateId' not in i["data"]:
                    i['data']['templateId'] = i['templateId']
                itemTemplates.append(i["data"])

        for i in itemTemplates:
            if 'pokemonSettings' in i:
                pokemon = i['pokemonSettings']

                if 'buddySize' in pokemon:
                    pokemon['buddySizeName'] = pokemon['buddySize']
                    try:
                        pokemon['buddySize'] = BuddySize.Value(pokemon['buddySize'])
                    except ValueError:
                        print("Unknown pokemon buddy size: (templateId: '{:s}', buddySizeName: '{:s}')".format(i['templateId'], pokemon['buddySize']))

                if 'cinematicMoves' in pokemon:
                    pokemon['cinematicMoveNames'] = pokemon['cinematicMoves']
                    cinematicMoves = []
                    for cinematicMove in pokemon['cinematicMoves']:
                        cinematicMoveId = None
                        try:
                            cinematicMoves.append(PokemonMove.Value(cinematicMove))
                        except ValueError:
                            # Already logged in "move" case
                            # print("Unknown move: (templateId: '{:s}', moveName: '{:s}')".format(i['templateId'], cinematicMove))
                            cinematicMoves.append(cinematicMove)
                    pokemon['cinematicMoves'] = cinematicMoves

                if 'movementType' in pokemon['encounter']:
                    pokemon['encounter']['movementTypeName'] = pokemon['encounter']['movementType']
                    try:
                        pokemon['encounter']['movementType'] = PokemonMovementType.Value(pokemon['encounter']['movementType'])
                    except ValueError:
                        print("Unknown pokemon encounter movement type: (templateId: '{:s}', familyName: '{:s}')".format(i['templateId'], pokemon['encounter']['movementType']))

                if 'evolutionIds' in pokemon:
                    pokemon['evolutionNames'] = pokemon['evolutionIds']
                    evolutionIds = []
                    for evolution in pokemon['evolutionIds']:
                        evolutionId = None
                        try:
                            evolutionIds.append(PokemonId.Value(evolution))
                        except ValueError:
                            # Already logged in "pokemon" case
                            # print("Unknown pokemon: (templateId: '{:s}', pokemonName: '{:s}')".format(i['templateId'], evolution))
                            evolutionIds.append(evolution)
                    pokemon['evolutionIds'] = evolutionIds

                if 'evolutionBranch' in pokemon:
                    for j, evoBranch in enumerate(pokemon['evolutionBranch']):
                        if 'evolution' in evoBranch:
                            pokemon['evolutionBranch'][j]['evolutionName'] = evoBranch['evolution']
                            try:
                                pokemon['evolutionBranch'][j]['evolution'] = PokemonId.Value(evoBranch['evolution'])
                            except ValueError:
                                # Already logged in "pokemon" case
                                # print("Unknown pokemon: (templateId: '{:s}', pokemonName: '{:s}')".format(i['templateId'], evoBranch['evolution']))
                                pass
                        if 'form' in evoBranch:
                            pokemon['evolutionBranch'][j]['formName'] = evoBranch['form']
                            try:
                                pokemon['evolutionBranch'][j]['form'] = Form.Value(evoBranch['form'])
                            except ValueError:
                                # Already logged in "formSettings" case
                                # print("Unknown form: (templateId: '{:s}', formName: '{:s}')".format(i['templateId'], evoBranch['form']))
                                pass
                        if 'evolutionItemRequirement' in evoBranch:
                            pokemon['evolutionBranch'][j]['evolutionItemRequirementName'] = evoBranch['evolutionItemRequirement']
                            try:
                                pokemon['evolutionBranch'][j]['evolutionItemRequirement'] = ItemId.Value(evoBranch['evolutionItemRequirement'])
                            except ValueError:
                                # Already logged in "item" case
                                # print("Unknown item: (templateId: '{:s}', itemName: '{:s}')".format(i['templateId'], evoBranch['evolutionItemRequirement']))
                                pass

                pokemon['familyName'] = pokemon['familyId']
                try:
                    pokemon['familyId'] = PokemonFamilyId.Value(pokemon['familyId'])
                except ValueError:
                    print("Unknown pokemon family: (templateId: '{:s}', familyName: '{:s}')".format(i['templateId'], pokemon['familyId']))
                if 'form' in pokemon:
                    pokemon['formName'] = pokemon['form']
                    try:
                        pokemon['form'] = Form.Value(pokemon['form'])
                    except ValueError:
                        # Already logged in "formSettings" case
                        # print("Unknown form: (templateId: '{:s}', formName: '{:s}')".format(i['templateId'], pokemon['form']))
                        pass

                pokemon['pokemonName'] = pokemon['pokemonId']
                pokemonId = None
                try:
                    pokemonId = PokemonId.Value(pokemon['pokemonId'])
                except ValueError:
                    print("Unknown pokemon: (templateId: '{:s}', pokemonName: '{:s}')".format(i['templateId'], pokemon['pokemonId']))
                    m = re.search('^V([0-9]+)_POKEMON_.*', i['templateId'])
                    if m is not None:
                        pokemonId = int(m.group(1))
                if pokemonId is not None:
                    pokemon['pokemonId'] = pokemonId

                if 'quickMoves' in pokemon:
                    pokemon['quickMoveNames'] = pokemon['quickMoves']
                    quickMoves = []
                    for quickMove in pokemon['quickMoves']:
                        quickMoveId = None
                        try:
                            quickMoves.append(PokemonMove.Value(quickMove))
                        except ValueError:
                            # Already logged in "move" case
                            # print("Unknown move: (templateId: '{:s}', moveName: '{:s}')".format(i['templateId'], quickMove)
                            quickMoves.append(quickMove)
                    pokemon['quickMoves'] = quickMoves

                if 'rarity' in pokemon:
                    pokemon['rarityName'] = pokemon['rarity']
                    try:
                        pokemon['rarity'] = PokemonRarity.Value(pokemon['rarity'])
                    except ValueError:
                        print("Unknown pokemon rarity: (templateId: '{:s}', rarityName: '{:s}')".format(i['templateId'], pokemon['rarity']))

                pokemon['typeName'] = pokemon['type']
                try:
                    pokemon['type'] = PokemonType.Value(pokemon['type'])
                except ValueError:
                    # Already logged in "typeEffective" case
                    # print("Unknown type: (templateId: '{:s}', typeName: '{:s}')".format(i['templateId'], pokemon['type']))
                    pass
                if 'type2' in pokemon:
                    pokemon['type2Name'] = pokemon['type2']
                    try:
                        pokemon['type2'] = PokemonType.Value(pokemon['type2'])
                    except ValueError:
                        # Already logged in "typeEffective" case
                        # print("Unknown type: (templateId: '{:s}', typeName: '{:s}')".format(i['templateId'], pokemon['type2']))
                        pass

            elif 'genderSettings' in i:
                i['genderSettings']['pokemonName'] = i['genderSettings']['pokemon']
                try:
                    i['genderSettings']['pokemon'] = PokemonId.Value(i['genderSettings']['pokemon'])
                except ValueError:
                    # Already logged in "pokemon" case
                    # print("Unknown pokemon: (templateId: '{:s}', pokemonName: '{:s}')".format(i['templateId'], i['genderSettings']['pokemon']))
                    pass

            elif 'formSettings' in i:
                formSetting = i['formSettings']

                if 'forms' in formSetting:
                    for j, form in enumerate(formSetting['forms']):
                        formSetting['forms'][j]['formName'] = form['form']
                        try:
                            formSetting['forms'][j]['form'] = Form.Value(form['form'])
                        except ValueError:
                            print("Unknown form: (templateId: '{:s}', formName: '{:s}')".format(i['templateId'], form['form']))
                formSetting['pokemonName'] = formSetting['pokemon']
                try:
                    formSetting['pokemon'] = PokemonId.Value(formSetting['pokemon'])
                except ValueError:
                    # Already logged in "pokemon" case
                    # print("Unknown pokemon: (templateId: '{:s}', pokemonName: '{:s}')".format(i['templateId'], formSetting['pokemon']))
                    pass

            elif 'typeEffective' in i:
                i['typeEffective']['attackTypeName'] = i['typeEffective']['attackType']
                try:
                    i['typeEffective']['attackType'] = PokemonType.Value(i['typeEffective']['attackType'])
                except ValueError:
                    print("Unknown type: (templateId: '{:s}', typeName: '{:s}')".format(i['templateId'], i['typeEffective']['attackType']))

            elif 'moveSettings' in i:
                move = i['moveSettings']

                move['animationName'] = move['animationId']
                # JSON files from https://github.com/PokeMiners/game_masters has it already converted to int :/ strange
                # try:
                    # move['animationId'] = PokemonAnim.Value(move['animationId'])
                # except ValueError:
                    # print("Unknown move animation: (templateId: '{:s}', animationName: '{:s}')".format(i['templateId'], move['animationId']))

                move['movementName'] = move['movementId']
                moveId = None
                try:
                    moveId = PokemonMove.Value(move['movementId'])
                except ValueError:
                    print("Unknown move: (templateId: '{:s}', moveName: '{:s}')".format(i['templateId'], move['movementId']))
                    m = re.search('^V([0-9]+)_MOVE_.*', i['templateId'])
                    if m is not None:
                        moveId = int(m.group(1))
                if moveId is not None:
                    move['movementId'] = moveId

                move['pokemonTypeName'] = move['pokemonType']
                try:
                    move['pokemonType'] = PokemonType.Value(move['pokemonType'])
                except ValueError:
                    # Already logged in "typeEffective" case
                    # print("Unknown type: (templateId: '{:s}', typeName: '{:s}')".format(i['templateId'], move['pokemonType']))
                    pass
                move['energyDelta'] = move.get('energyDelta', 0)

            elif 'combatMove' in i:
                combatMove = i['combatMove']

                combatMove['uniqueName'] = combatMove['uniqueId']
                moveId = None
                try:
                    moveId = PokemonMove.Value(combatMove['uniqueId'])
                except ValueError:
                    # Already logged in "move" case
                    # print("Unknown move: (templateId: '{:s}', moveName: '{:s}')".format(i['templateId'], combatMove['movementId']))
                    m = re.search('^COMBAT_V([0-9]+)_MOVE_.*', i['templateId'])
                    if m is not None:
                        moveId = int(m.group(1))
                if moveId is not None:
                    combatMove['uniqueId'] = moveId

                combatMove['typeName'] = combatMove['type']
                try:
                    combatMove['type'] = PokemonType.Value(combatMove['type'])
                except ValueError:
                    # Already logged in "typeEffective" case
                    # print("Unknown type: (templateId: '{:s}', typeName: '{:s}')".format(i['templateId'], combatMove['type']))
                    pass
                combatMove['energyDelta'] = combatMove.get('energyDelta', 0)

            elif 'itemSettings' in i:
                item = i['itemSettings']

                item['itemName'] = item['itemId']
                try:
                    item['itemId'] = ItemId.Value(item['itemId'])
                except ValueError:
                    print("Unknown item: (templateId: '{:s}', itemName: '{:s}')".format(i['templateId'], item['itemId']))
                item['categoryName'] = item['category']
                item['itemTypeName'] = item['itemType']

            elif 'badgeSettings' in i:
                i['badgeSettings']['badgeTypeName'] = i['badgeSettings']['badgeType']
                try:
                    i['badgeSettings']['badgeType'] = BadgeType.Value(i['badgeSettings']['badgeType'])
                except ValueError:
                    print("Unknown badge: (templateId: '{:s}', typeName: '{:s}')".format(i['templateId'], i['badgeSettings']['badgeType']))

        return itemTemplates