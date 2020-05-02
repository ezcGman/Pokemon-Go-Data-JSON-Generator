from pogoprotos.networking.responses.download_item_templates_response_pb2 import *
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import SerializeToJsonError

# Needed for JSON parsing
from pogoprotos.data.player.player_avatar_type_pb2 import *
from pogoprotos.data.avatar.avatar_customization_unlock_type_pb2 import *
from pogoprotos.data.avatar.slot_pb2 import *
from pogoprotos.enums.badge_type_pb2 import *
from pogoprotos.enums.battle_hub_section_pb2 import *
from pogoprotos.enums.battle_hub_subsection_pb2 import *
from pogoprotos.enums.buddy.buddy_activity_pb2 import *
from pogoprotos.enums.buddy.buddy_activity_category_pb2 import *
from pogoprotos.enums.buddy.buddy_animation_pb2 import *
from pogoprotos.enums.buddy.buddy_emotion_level_pb2 import *
from pogoprotos.enums.buddy.buddy_level_pb2 import *
from pogoprotos.enums.buddy_size_pb2 import *
from pogoprotos.enums.buddy.buddy_trait_pb2 import *
from pogoprotos.enums.camera_interpolation_pb2 import *
from pogoprotos.enums.camera_target_pb2 import *
from pogoprotos.enums.condition_type_pb2 import *
from pogoprotos.enums.costume_pb2 import *
from pogoprotos.enums.form_pb2 import *
from pogoprotos.enums.friendship_level_milestone_pb2 import *
from pogoprotos.enums.iap_item_category_pb2 import *
from pogoprotos.enums.party_recommendation_mode_pb2 import *
from pogoprotos.enums.pokemon_anim_pb2 import *
from pogoprotos.enums.pokemon_id_pb2 import *
from pogoprotos.enums.pokemon_family_id_pb2 import *
from pogoprotos.enums.pokemon_move_pb2 import *
from pogoprotos.enums.pokemon_movement_type_pb2 import *
from pogoprotos.enums.pokemon_rarity_pb2 import *
from pogoprotos.enums.pokemon_scale_mode_pb2 import *
from pogoprotos.enums.pokemon_trading_type_pb2 import *
from pogoprotos.enums.pokemon_type_pb2 import *
from pogoprotos.enums.quest_type_pb2 import *
from pogoprotos.enums.weather_condition_pb2 import *
from pogoprotos.inventory.item.item_id_pb2 import *

import json
import re
from pprint import pprint


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
            # Pokemon
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

            # Gender possibilities per pokemon, nobody knows why that is not part of 'pokemon_settings'
            elif self.messageHasField(i, 'gender_settings'):
                pokemonId = i.gender_settings.pokemon

                jsonObj = MessageToJson(i)
                genderSetting = json.loads(jsonObj)

                genderSetting['genderSettings']['pokemonName'] = genderSetting['genderSettings']['pokemon']
                genderSetting['genderSettings']['pokemon'] = pokemonId

                itemTemplates.append(genderSetting)
                # pprint(genderSetting)

            # Forms
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

            # Types
            elif self.messageHasField(i, 'type_effective'):
                typeId = i.type_effective.attack_type

                jsonObj = MessageToJson(i)
                typeEffective = json.loads(jsonObj)

                typeEffective['typeEffective']['attackTypeName'] = typeEffective['typeEffective']['attackType']
                typeEffective['typeEffective']['attackType'] = typeId

                itemTemplates.append(typeEffective)
                # pprint(typeEffective)

            # Moves
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

            # Combat moves
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

            # Items
            elif self.messageHasField(i, 'item_settings'):
                itemId = i.item_settings.item_id
                itemCategory = i.item_settings.category
                itemType = i.item_settings.item_type

                jsonObj = MessageToJson(i)
                item = json.loads(jsonObj)

                item['itemSettings']['itemName'] = item['itemSettings']['itemId']

                if item['itemSettings']['itemId'] == itemId:
                    print("Unknown item: (templateId: '{:s}', itemId: '{:d}')".format(i.template_id, itemId))
                item['itemSettings']['itemId'] = itemId
                item['itemSettings']['categoryName'] = item['itemSettings']['category']
                item['itemSettings']['category'] = itemCategory
                item['itemSettings']['itemTypeName'] = item['itemSettings']['itemType']
                item['itemSettings']['itemType'] = itemType

                itemTemplates.append(item)
                # pprint(item)

            # Badges
            elif self.messageHasField(i, 'badge_settings'):
                badgeId = i.badge_settings.badge_type

                jsonObj = MessageToJson(i)
                badge = json.loads(jsonObj)

                badge['badgeSettings']['badgeTypeName'] = badge['badgeSettings']['badgeType']

                if badge['badgeSettings']['badgeType'] == badgeId:
                    print("Unknown badge: (templateId: '{:s}', badgeId: '{:d}')".format(i.template_id, badgeId))
                badge['badgeSettings']['badgeType'] = badgeId

                itemTemplates.append(badge)
                # pprint(badge)

            # Weather affinities
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

            # Friendship levels
            elif self.messageHasField(i, 'friendship_milestone_settings'):
                unlockedTradings = [ unlockedTrading for unlockedTrading in i.friendship_milestone_settings.unlocked_trading ]

                jsonObj = MessageToJson(i)
                friendshipMilestone = json.loads(jsonObj)

                friendshipMilestone['friendshipMilestoneSettings']['unlockedTradingNames'] = friendshipMilestone['friendshipMilestoneSettings']['unlockedTrading']
                friendshipMilestone['friendshipMilestoneSettings']['unlockedTrading'] = unlockedTradings

                itemTemplates.append(friendshipMilestone)
                # pprint(friendshipMilestone)

            # Ex Raid Settings
            elif self.messageHasField(i, 'ex_raid_settings'):
                minShareLvl = i.ex_raid_settings.minimum_ex_raid_share_level

                jsonObj = MessageToJson(i)
                exRaidSettings = json.loads(jsonObj)

                exRaidSettings['exRaidSettings']['minimumExRaidShareLevelName'] = exRaidSettings['exRaidSettings']['minimumExRaidShareLevel']
                exRaidSettings['exRaidSettings']['minimumExRaidShareLevel'] = minShareLvl

                itemTemplates.append(exRaidSettings)
                # pprint(exRaidSettings)

            # Daily quests
            elif self.messageHasField(i, 'quest_settings'):
                questType = i.quest_settings.quest_type

                jsonObj = MessageToJson(i)
                quest = json.loads(jsonObj)

                quest['questSettings']['questTypeName'] = quest['questSettings']['questType']
                quest['questSettings']['questType'] = questType

                # itemTemplates.append(quest)

            # Battle party recommendation settings
            elif self.messageHasField(i, 'party_recommendation_settings'):
                theMode = i.party_recommendation_settings.mode

                jsonObj = MessageToJson(i)
                partySettings = json.loads(jsonObj)

                partySettings['partyRecommendationSettings']['modeName'] = partySettings['partyRecommendationSettings']['mode']
                partySettings['partyRecommendationSettings']['mode'] = theMode

                itemTemplates.append(partySettings)
                # pprint(partySettings)

            # Combat leagues (e.g. great, ultra, etc.) settings
            elif self.messageHasField(i, 'combat_league'):
                bannedPokemon = None
                if hasattr(i.combat_league, 'banned_pokemon') and len(i.combat_league.banned_pokemon) > 0:
                    bannedPokemon = [ bannedPoke for bannedPoke in i.combat_league.banned_pokemon ]
                unlockConditions = None
                if hasattr(i.combat_league, 'unlock_condition') and len(i.combat_league.unlock_condition) > 0:
                    unlockConditions = i.combat_league.unlock_condition
                pokemonConditions = None
                if hasattr(i.combat_league, 'pokemon_condition') and len(i.combat_league.pokemon_condition) > 0:
                    pokemonConditions = i.combat_league.pokemon_condition
                badgeType = i.combat_league.badge_type

                jsonObj = MessageToJson(i)
                combatLeague = json.loads(jsonObj)

                if bannedPokemon is not None:
                    combatLeague['combatLeague']['bannedPokemonNames'] = combatLeague['combatLeague']['bannedPokemon']
                    combatLeague['combatLeague']['bannedPokemon'] = bannedPokemon
                if unlockConditions is not None:
                    # Note: There is a slight chance that the order of the list after converting it to JSON has changed! So there is the possibility of a bug here!
                    for j, unlockCondition in enumerate(unlockConditions):
                        combatLeague['combatLeague']['unlockCondition'][j]['typeName'] = combatLeague['combatLeague']['unlockCondition'][j]['type']
                        combatLeague['combatLeague']['unlockCondition'][j]['type'] = unlockCondition.type
                if pokemonConditions is not None:
                    # Note: There is a slight chance that the order of the list after converting it to JSON has changed! So there is the possibility of a bug here!
                    for j, pokemonCondition in enumerate(pokemonConditions):
                        combatLeague['combatLeague']['pokemonCondition'][j]['typeName'] = combatLeague['combatLeague']['pokemonCondition'][j]['type']
                        combatLeague['combatLeague']['pokemonCondition'][j]['type'] = pokemonCondition.type
                combatLeague['combatLeague']['badgeTypeName'] = combatLeague['combatLeague']['badgeType']
                combatLeague['combatLeague']['badgeType'] = badgeType

                itemTemplates.append(combatLeague)
                # pprint(combatLeague)

            # The three trainers with their lineup for each combat league
            elif self.messageHasField(i, 'combat_npc_trainer'):
                availablePokemon = None
                if hasattr(i.combat_npc_trainer, 'available_pokemon') and len(i.combat_npc_trainer.available_pokemon) > 0:
                    availablePokemon = i.combat_npc_trainer.available_pokemon

                jsonObj = MessageToJson(i)
                combatNpcTrainer = json.loads(jsonObj)

                if availablePokemon is not None:
                    # Note: There is a slight chance that the order of the list after converting it to JSON has changed! So there is the possibility of a bug here!
                    for j, availablePoke in enumerate(availablePokemon):
                        combatNpcTrainer['combatNpcTrainer']['availablePokemon'][j]['pokemonTypeName'] = combatNpcTrainer['combatNpcTrainer']['availablePokemon'][j]['pokemonType']
                        combatNpcTrainer['combatNpcTrainer']['availablePokemon'][j]['pokemonType'] = availablePoke.pokemon_type

                        if hasattr(availablePoke, 'pokemon_display') and hasattr(availablePoke.pokemon_display, 'form') and availablePoke.pokemon_display.form > 0:
                            combatNpcTrainer['combatNpcTrainer']['availablePokemon'][j]['pokemonDisplay']['formName'] = combatNpcTrainer['combatNpcTrainer']['availablePokemon'][j]['pokemonDisplay']['form']
                            combatNpcTrainer['combatNpcTrainer']['availablePokemon'][j]['pokemonDisplay']['form'] = availablePoke.pokemon_display.form

                itemTemplates.append(combatNpcTrainer)
                # pprint(combatNpcTrainer)

            # Whitelist of Pokemon allowed to be transferred to "Pokemon Let's Go" games on Nintendo Switch
            elif self.messageHasField(i, 'beluga_pokemon_whitelist'):
                costumesAllowed = [ costumeAllowed for costumeAllowed in i.beluga_pokemon_whitelist.costumes_allowed ]
                additionalPokemonAllowed = [ additionalPokemon for additionalPokemon in i.beluga_pokemon_whitelist.additional_pokemon_allowed ]

                jsonObj = MessageToJson(i)
                belugaPokemonWhitelist = json.loads(jsonObj)

                belugaPokemonWhitelist['belugaPokemonWhitelist']['costumesAllowedNames'] = belugaPokemonWhitelist['belugaPokemonWhitelist']['costumesAllowed']
                belugaPokemonWhitelist['belugaPokemonWhitelist']['costumesAllowed'] = costumesAllowed
                belugaPokemonWhitelist['belugaPokemonWhitelist']['additionalPokemonAllowedNames'] = belugaPokemonWhitelist['belugaPokemonWhitelist']['additionalPokemonAllowed']
                belugaPokemonWhitelist['belugaPokemonWhitelist']['additionalPokemonAllowed'] = additionalPokemonAllowed

                itemTemplates.append(belugaPokemonWhitelist)
                # pprint(belugaPokemonWhitelist)

            # Moves Smeargles can learn
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

            # Avatar clothes / items available in store
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

            # Not sure what this is
            elif self.messageHasField(i, 'onboarding_v2_settings'):
                pokedexIds = [ pokedexId for pokedexId in i.onboarding_v2_settings.pokedex_id ]

                jsonObj = MessageToJson(i)
                v2Settings = json.loads(jsonObj)

                v2Settings['onboardingV2Settings']['pokedexNames'] = v2Settings['onboardingV2Settings']['pokedexId']
                v2Settings['onboardingV2Settings']['pokedexId'] = pokedexIds

                itemTemplates.append(v2Settings)
                # pprint(v2Settings)

            # Out of interest
            elif self.messageHasField(i, 'iap_category_display'):
                category = i.iap_category_display.category

                jsonObj = MessageToJson(i)
                iapCategoryDisplay = json.loads(jsonObj)

                iapCategoryDisplay['iapCategoryDisplay']['categoryName'] = iapCategoryDisplay['iapCategoryDisplay']['category']
                iapCategoryDisplay['iapCategoryDisplay']['category'] = category

                itemTemplates.append(iapCategoryDisplay)
                # pprint(iapCategoryDisplay)

            # Out of interest
            elif self.messageHasField(i, 'iap_item_display'):
                category = i.iap_item_display.category

                jsonObj = MessageToJson(i)
                iapItemDisplay = json.loads(jsonObj)

                iapItemDisplay['iapItemDisplay']['categoryName'] = iapItemDisplay['iapItemDisplay']['category']
                iapItemDisplay['iapItemDisplay']['category'] = category

                itemTemplates.append(iapItemDisplay)
                # pprint(iapItemDisplay)

            # Out of interest
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

            # Out of interest
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

            else:
                # Currently these: 'background_mode_settings', 'battle_settings', 'combat_league_settings', 'combat_settings', 'combat_stat_stage_settings', 'encounter_settings', 'gym_badge_settings', 'gym_level', 'iap_settings', 'lucky_pokemon_settings', 'player_level', 'pokecoin_purchase_display_gmt', 'pokemon_upgrades', 'combat_npc_personality', 'weather_bonus_settings', 'adventure_sync_v2_gmt', 'move_sequence_settings'
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
            ### Already in v1 ###
            if 'pokemonSettings' in i:
                pokemon = i['pokemonSettings']

                if 'buddySize' in pokemon:
                    pokemon['buddySizeName'] = pokemon['buddySize']
                    try:
                        pokemon['buddySize'] = BuddySize.Value(pokemon['buddySize'])
                    except ValueError:
                        print("Unknown pokemon buddy size: (templateId: '{:s}', buddySizeName: '{:s}')".format(i['templateId'], pokemon['buddySize']))

                pokemonMovesKeyMap = {'quickMoves': 'quickMoveNames', 'cinematicMoves': 'cinematicMoveNames'}
                for pokemonMovesKey in pokemonMovesKeyMap.keys():
                    if pokemonMovesKey in pokemon:
                        pokemon[pokemonMovesKeyMap[pokemonMovesKey]] = pokemon[pokemonMovesKey]
                        moveList = []
                        for theMove in pokemon[pokemonMovesKey]:
                            try:
                                moveList.append(PokemonMove.Value(theMove))
                            except ValueError:
                                print("Unknown move: (templateId: '{:s}', moveName: '{:s}')".format(i['templateId'], theMove))
                                moveList.append(theMove)
                        pokemon[pokemonMovesKey] = moveList

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
                        try:
                            evolutionIds.append(PokemonId.Value(evolution))
                        except ValueError:
                            print("Unknown pokemon: (templateId: '{:s}', pokemonName: '{:s}')".format(i['templateId'], evolution))
                            evolutionIds.append(evolution)
                    pokemon['evolutionIds'] = evolutionIds

                if 'evolutionBranch' in pokemon:
                    for j, evoBranch in enumerate(pokemon['evolutionBranch']):
                        if 'evolution' in evoBranch:
                            evoBranch['evolutionName'] = evoBranch['evolution']
                            try:
                                evoBranch['evolution'] = PokemonId.Value(evoBranch['evolution'])
                            except ValueError:
                                print("Unknown pokemon: (templateId: '{:s}', pokemonName: '{:s}')".format(i['templateId'], evoBranch['evolution']))
                        if 'form' in evoBranch:
                            evoBranch['formName'] = evoBranch['form']
                            try:
                                evoBranch['form'] = Form.Value(evoBranch['form'])
                            except ValueError:
                                print("Unknown form: (templateId: '{:s}', formName: '{:s}')".format(i['templateId'], evoBranch['form']))
                        if 'evolutionItemRequirement' in evoBranch:
                            evoBranch['evolutionItemRequirementName'] = evoBranch['evolutionItemRequirement']
                            try:
                                evoBranch['evolutionItemRequirement'] = ItemId.Value(evoBranch['evolutionItemRequirement'])
                            except ValueError:
                                print("Unknown item: (templateId: '{:s}', itemName: '{:s}')".format(i['templateId'], evoBranch['evolutionItemRequirement']))

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
                        print("Unknown form: (templateId: '{:s}', formName: '{:s}')".format(i['templateId'], pokemon['form']))

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
                    print("Unknown type: (templateId: '{:s}', typeName: '{:s}')".format(i['templateId'], pokemon['type']))
                if 'type2' in pokemon:
                    pokemon['type2Name'] = pokemon['type2']
                    try:
                        pokemon['type2'] = PokemonType.Value(pokemon['type2'])
                    except ValueError:
                        print("Unknown type: (templateId: '{:s}', typeName: '{:s}')".format(i['templateId'], pokemon['type2']))

            elif 'genderSettings' in i:
                i['genderSettings']['pokemonName'] = i['genderSettings']['pokemon']
                try:
                    i['genderSettings']['pokemon'] = PokemonId.Value(i['genderSettings']['pokemon'])
                except ValueError:
                    print("Unknown pokemon: (templateId: '{:s}', pokemonName: '{:s}')".format(i['templateId'], i['genderSettings']['pokemon']))

            elif 'formSettings' in i:
                formSetting = i['formSettings']

                if 'forms' in formSetting:
                    for j, form in enumerate(formSetting['forms']):
                        form['formName'] = form['form']
                        try:
                            form['form'] = Form.Value(form['form'])
                        except ValueError:
                            print("Unknown form: (templateId: '{:s}', formName: '{:s}')".format(i['templateId'], form['form']))
                formSetting['pokemonName'] = formSetting['pokemon']
                try:
                    formSetting['pokemon'] = PokemonId.Value(formSetting['pokemon'])
                except ValueError:
                    print("Unknown pokemon: (templateId: '{:s}', pokemonName: '{:s}')".format(i['templateId'], formSetting['pokemon']))

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
                    print("Unknown type: (templateId: '{:s}', typeName: '{:s}')".format(i['templateId'], move['pokemonType']))
                move['energyDelta'] = move.get('energyDelta', 0)

            elif 'combatMove' in i:
                combatMove = i['combatMove']

                combatMove['uniqueName'] = combatMove['uniqueId']
                moveId = None
                try:
                    moveId = PokemonMove.Value(combatMove['uniqueId'])
                except ValueError:
                    print("Unknown move: (templateId: '{:s}', moveName: '{:s}')".format(i['templateId'], combatMove['movementId']))
                    m = re.search('^COMBAT_V([0-9]+)_MOVE_.*', i['templateId'])
                    if m is not None:
                        moveId = int(m.group(1))
                if moveId is not None:
                    combatMove['uniqueId'] = moveId

                combatMove['typeName'] = combatMove['type']
                try:
                    combatMove['type'] = PokemonType.Value(combatMove['type'])
                except ValueError:
                    print("Unknown type: (templateId: '{:s}', typeName: '{:s}')".format(i['templateId'], combatMove['type']))
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
                    print("Unknown badge: (templateId: '{:s}', badgeName: '{:s}')".format(i['templateId'], i['badgeSettings']['badgeType']))

            elif 'weatherAffinities' in i:
                weatherAffinity = i['weatherAffinities']

                weatherAffinity['pokemonTypeNames'] = weatherAffinity['pokemonType']
                pokemonTypes = []
                for pokemonType in weatherAffinity['pokemonType']:
                    try:
                        pokemonTypes.append(PokemonType.Value(pokemonType))
                    except ValueError:
                        print("Unknown type: (templateId: '{:s}', typeName: '{:s}')".format(i['templateId'], pokemonType))
                        pokemonTypes.append(pokemonType)
                weatherAffinity['pokemonType'] = pokemonTypes

                weatherAffinity['weatherConditionName'] = weatherAffinity['weatherCondition']
                try:
                    weatherAffinity['weatherCondition'] = WeatherCondition.Value(weatherAffinity['weatherCondition'])
                except ValueError:
                    print("Unknown weather condition: (templateId: '{:s}', weatherCondition: '{:s}')".format(i['templateId'], item['weatherCondition']))

            elif 'friendshipMilestoneSettings' in i:
                friendshipMilestone = i['friendshipMilestoneSettings']

                friendshipMilestone['unlockedTradingNames'] = friendshipMilestone['unlockedTrading']
                unlockedTradings = []
                for unlockedTrading in friendshipMilestone['unlockedTrading']:
                    try:
                        unlockedTradings.append(PokemonTradingType.Value(unlockedTrading))
                    except ValueError:
                        print("Unknown trading unlock: (templateId: '{:s}', unlockedTradingName: '{:s}')".format(i['templateId'], unlockedTrading))
                        unlockedTradings.append(unlockedTrading)
                friendshipMilestone['unlockedTrading'] = unlockedTradings

            elif 'exRaidSettings' in i:
                i['exRaidSettings']['minimumExRaidShareLevelName'] = i['exRaidSettings']['minimumExRaidShareLevel']
                try:
                    i['exRaidSettings']['minimumExRaidShareLevel'] = FriendshipLevelMilestone.Value(i['exRaidSettings']['minimumExRaidShareLevel'])
                except ValueError:
                    print("Unknown friendship level: (templateId: '{:s}', friendshipLevelName: '{:s}')".format(i['templateId'], i['exRaidSettings']['minimumExRaidShareLevel']))

            elif 'questSettings' in i:
                i['questSettings']['questTypeName'] = i['questSettings']['questType']
                try:
                    i['questSettings']['questType'] = QuestType.Value(i['questSettings']['questType'])
                except ValueError:
                    print("Unknown quest type: (templateId: '{:s}', questTypeName: '{:s}')".format(i['templateId'], i['questSettings']['questType']))

            elif 'partyRecommendationSettings' in i:
                i['partyRecommendationSettings']['modeName'] = i['partyRecommendationSettings']['mode']
                try:
                    i['partyRecommendationSettings']['mode'] = PartyRecommendationMode.Value(i['partyRecommendationSettings']['mode'])
                except ValueError:
                    print("Unknown party recommendation mode: (templateId: '{:s}', mode: '{:s}')".format(i['templateId'], i['partyRecommendationSettings']['mode']))

            elif 'combatLeague' in i:
                combatLeague = i['combatLeague']

                combatLeague['badgeTypeName'] = combatLeague['badgeType']
                try:
                    combatLeague['badgeType'] = BadgeType.Value(combatLeague['badgeType'])
                except ValueError:
                    print("Unknown badge: (templateId: '{:s}', badgeName: '{:s}')".format(i['templateId'], combatLeague['badgeType']))

                combatLeague['bannedPokemonNames'] = combatLeague['bannedPokemon']
                bannedPokemon = []
                for bannedPoke in combatLeague['bannedPokemon']:
                    try:
                        bannedPokemon.append(PokemonId.Value(bannedPoke))
                    except ValueError:
                        print("Unknown pokemon: (templateId: '{:s}', pokemonName: '{:s}')".format(i['templateId'], bannedPoke))
                        bannedPokemon.append(bannedPoke)
                combatLeague['bannedPokemon'] = bannedPokemon

                for condition in ['pokemonCondition', 'unlockCondition']:
                    if condition in combatLeague:
                        for j, theCondition in enumerate(combatLeague[condition]):
                            theCondition['typeName'] = theCondition['type']
                            try:
                                theCondition['type'] = ConditionType.Value(theCondition['type'])
                            except ValueError:
                                print("Unknown condition type: (templateId: '{:s}', conditionTypeName: '{:s}')".format(i['templateId'], theCondition['type']))

            elif 'combatNpcTrainer' in i:
                for j, availablePokemon in enumerate(i['combatNpcTrainer']['availablePokemon']):
                    availablePokemon['pokemonTypeName'] = availablePokemon['pokemonType']
                    try:
                        availablePokemon['pokemonType'] = PokemonId.Value(availablePokemon['pokemonType'])
                    except ValueError:
                        print("Unknown pokemon: (templateId: '{:s}', pokemonName: '{:s}')".format(i['templateId'], availablePokemon['pokemonType']))

                    if 'pokemonDisplay' in availablePokemon and 'form' in availablePokemon['pokemonDisplay']:
                        availablePokemon['pokemonDisplay']['formName'] = availablePokemon['pokemonDisplay']['form']
                        try:
                            availablePokemon['pokemonDisplay']['form'] = Form.Value(availablePokemon['pokemonDisplay']['form'])
                        except ValueError:
                            print("Unknown form: (templateId: '{:s}', formName: '{:s}')".format(i['templateId'], availablePokemon['pokemonDisplay']['form']))

            elif 'belugaPokemonWhitelist' in i:
                belugaWhitelist = i['belugaPokemonWhitelist']

                belugaWhitelist['additionalPokemonAllowedNames'] = belugaWhitelist['additionalPokemonAllowed']
                additionalPokemonAllowed = []
                for additionalPokemon in belugaWhitelist['additionalPokemonAllowed']:
                    try:
                        additionalPokemonAllowed.append(PokemonId.Value(additionalPokemon))
                    except ValueError:
                        print("Unknown pokemon: (templateId: '{:s}', pokemonName: '{:s}')".format(i['templateId'], additionalPokemon))
                        additionalPokemonAllowed.append(additionalPokemon)
                belugaWhitelist['additionalPokemonAllowed'] = additionalPokemonAllowed

                belugaWhitelist['costumesAllowedNames'] = belugaWhitelist['costumesAllowed']
                costumesAllowed = []
                for costume in belugaWhitelist['costumesAllowed']:
                    try:
                        costumesAllowed.append(Costume.Value(costume))
                    except ValueError:
                        print("Unknown costume: (templateId: '{:s}', costume: '{:s}')".format(i['templateId'], costume))
                        costumesAllowed.append(costume)
                belugaWhitelist['costumesAllowed'] = costumesAllowed

            elif 'smeargleMovesSettings' in i:
                smeargleMoves = i['smeargleMovesSettings']

                smeargleMovesKeyMap = {'quickMoves': 'quickMoveNames', 'cinematicMoves': 'cinematicMoveNames'}
                for smeargleMovesKey in smeargleMovesKeyMap.keys():
                    smeargleMoves[smeargleMovesKeyMap[smeargleMovesKey]] = smeargleMoves[smeargleMovesKey]
                    moveList = []
                    for theMove in smeargleMoves[smeargleMovesKey]:
                        try:
                            moveList.append(PokemonMove.Value(theMove))
                        except ValueError:
                            print("Unknown move: (templateId: '{:s}', moveName: '{:s}')".format(i['templateId'], theMove))
                            moveList.append(theMove)
                    smeargleMoves[smeargleMovesKey] = moveList

            elif 'avatarCustomization' in i:
                avatarCustom = i['avatarCustomization']

                if 'avatarType' in avatarCustom:
                    avatarCustom['avatarTypeName'] = avatarCustom['avatarType']
                    try:
                        avatarCustom['avatarType'] = PlayerAvatarType.Value(avatarCustom['avatarType'])
                    except ValueError:
                        print("Unknown avatar type: (templateId: '{:s}', avatarTypeName: '{:s}')".format(i['templateId'], avatarCustom['avatarType']))

                avatarCustom['slotNames'] = avatarCustom['slot']
                slots = []
                for theSlot in avatarCustom['slot']:
                    try:
                        slots.append(Slot.Value(theSlot))
                    except ValueError:
                        print("Unknown avatar slot: (templateId: '{:s}', slotName: '{:s}')".format(i['templateId'], theSlot))
                        slots.append(theSlot)
                avatarCustom['slot'] = slots

                avatarCustom['unlockTypeName'] = avatarCustom['unlockType']
                try:
                    avatarCustom['unlockType'] = AvatarCustomizationUnlockType.Value(avatarCustom['unlockType'])
                except ValueError:
                    print("Unknown avatar unlock type: (templateId: '{:s}', avatarUnlockTypeName: '{:s}')".format(i['templateId'], avatarCustom['unlockType']))

                if 'unlockBadgeType' in avatarCustom:
                    avatarCustom['unlockBadgeTypeName'] = avatarCustom['unlockBadgeType']
                    try:
                        avatarCustom['unlockBadgeType'] = BadgeType.Value(avatarCustom['unlockBadgeType'])
                    except ValueError:
                        print("Unknown badge: (templateId: '{:s}', badgeName: '{:s}')".format(i['templateId'], avatarCustom['unlockBadgeType']))

            elif 'onboardingV2Settings' in i:
                i['onboardingV2Settings']['pokedexNames'] = i['onboardingV2Settings']['pokedexId']
                pokedexIds = []
                for pokedexId in i['onboardingV2Settings']['pokedexId']:
                    try:
                        pokedexIds.append(PokemonId.Value(pokedexId))
                    except ValueError:
                        print("Unknown pokemon: (templateId: '{:s}', pokemonName: '{:s}')".format(i['templateId'], pokedexId))
                        pokedexIds.append(pokedexId)
                i['onboardingV2Settings']['pokedexId'] = pokedexIds

            elif 'iapCategoryDisplay' in i:
                i['iapCategoryDisplay']['categoryName'] = i['iapCategoryDisplay']['category']
                try:
                    i['iapCategoryDisplay']['category'] = HoloIapItemCategory.Value(i['iapCategoryDisplay']['category'])
                except ValueError:
                    print("Unknown store category: (templateId: '{:s}', categoryName: '{:s}')".format(i['templateId'], i['iapCategoryDisplay']['category']))

            elif 'iapItemDisplay' in i:
                i['iapItemDisplay']['categoryName'] = i['iapItemDisplay']['category']
                try:
                    i['iapItemDisplay']['category'] = HoloIapItemCategory.Value(i['iapItemDisplay']['category'])
                except ValueError:
                    print("Unknown store category: (templateId: '{:s}', categoryName: '{:s}')".format(i['templateId'], i['iapItemDisplay']['category']))

            elif 'camera' in i:
                i['camera']['interpolationNames'] = i['camera']['interpolation']
                interpolations = []
                for interpolation in i['camera']['interpolation']:
                    try:
                        interpolations.append(CameraInterpolation.Value(interpolation))
                    except ValueError:
                        print("Unknown camera interpolation: (templateId: '{:s}', interpolationName: '{:s}')".format(i['templateId'], interpolation))
                        interpolations.append(interpolation)
                i['camera']['interpolation'] = interpolations

                i['camera']['targetTypeNames'] = i['camera']['targetType']
                targetTypes = []
                for targetType in i['camera']['targetType']:
                    try:
                        targetTypes.append(CameraTarget.Value(targetType))
                    except ValueError:
                        print("Unknown camera target type: (templateId: '{:s}', targetTypeName: '{:s}')".format(i['templateId'], targetType))
                        targetTypes.append(targetType)
                i['camera']['targetType'] = targetTypes

            elif 'pokemonScaleSettings' in i:
                if 'pokemonScaleMode' in i['pokemonScaleSettings']:
                    i['pokemonScaleSettings']['pokemonScaleModeName'] = i['pokemonScaleSettings']['pokemonScaleMode']
                    try:
                        i['pokemonScaleSettings']['pokemonScaleMode'] = PokemonScaleMode.Value(i['pokemonScaleSettings']['pokemonScaleMode'])
                    except ValueError:
                        print("Unknown scale mode: (templateId: '{:s}', scaleModeName: '{:s}')".format(i['templateId'], i['pokemonScaleSettings']['pokemonScaleMode']))

            ### New in v2 ###

            elif 'awardLevelSettings' in i:
                i['awardLevelSettings']['rewardItemNames'] = i['awardLevelSettings']['rewardItem']
                rewardItems = []
                for rewardItem in i['awardLevelSettings']['rewardItem']:
                    try:
                        rewardItems.append(ItemId.Value(rewardItem))
                    except ValueError:
                        print("Unknown item: (templateId: '{:s}', itemName: '{:s}')".format(i['templateId'], rewardItem))
                        rewardItems.append(rewardItem)
                i['awardLevelSettings']['rewardItem'] = rewardItems

            elif 'battleHubBadgeSettings' in i:
                i['battleHubBadgeSettings']['combatHubDisplayedBadgeNames'] = i['battleHubBadgeSettings']['combatHubDisplayedBadges']
                badges = []
                for badge in i['battleHubBadgeSettings']['combatHubDisplayedBadges']:
                    try:
                        badges.append(BadgeType.Value(badge))
                    except ValueError:
                        print("Unknown badge: (templateId: '{:s}', badgeName: '{:s}')".format(i['templateId'], badge))
                        badges.append(badge)
                i['battleHubBadgeSettings']['combatHubDisplayedBadges'] = badges

            elif 'battleHubOrderSettings' in i:
                battleHub = i['battleHubOrderSettings']
                for j, section in enumerate(battleHub['section']):
                    section['mainSectionName'] = section['mainSection']
                    try:
                        section['mainSection'] = BattleHubSection.Value(section['mainSection'])
                    except ValueError:
                        print("Unknown battle hub section: (templateId: '{:s}', sectionName: '{:s}')".format(i['templateId'], section['mainSection']))

                    section['subsectionNames'] = section['subsection']
                    subsections = []
                    for subsection in section['subsection']:
                        try:
                            subsections.append(BattleHubSubsection.Value(subsection))
                        except ValueError:
                            print("Unknown battle hub subsection: (templateId: '{:s}', subsectionName: '{:s}')".format(i['templateId'], subsection))
                            subsections.append(subsection)
                    section['subsection'] = subsections

                for j, sectionGroup in enumerate(battleHub['sectionGroup']):
                    sectionGroup['sectionNames'] = sectionGroup['section']
                    sections = []
                    for groupSection in sectionGroup['section']:
                        try:
                            sections.append(BattleHubSection.Value(groupSection))
                        except ValueError:
                            print("Unknown battle hub section: (templateId: '{:s}', subsectionName: '{:s}')".format(i['templateId'], groupSection))
                            sections.append(groupSection)
                    sectionGroup['section'] = sections

            elif 'buddyActivityCategorySettings' in i:
                i['buddyActivityCategorySettings']['activityCategoryName'] = i['buddyActivityCategorySettings']['activityCategory']
                try:
                    i['buddyActivityCategorySettings']['activityCategory'] = BuddyActivityCategory.Value(i['buddyActivityCategorySettings']['activityCategory'])
                except ValueError:
                    print("Unknown buddy activity category: (templateId: '{:s}', activityCategoryName: '{:s}')".format(i['templateId'], i['buddyActivityCategorySettings']['activityCategory']))

            elif 'buddyActivitySettings' in i:
                buddyActivity = i['buddyActivitySettings']

                buddyActivity['activityName'] = buddyActivity['activity']
                try:
                    buddyActivity['activity'] = BuddyActivity.Value(buddyActivity['activity'])
                except ValueError:
                    print("Unknown buddy activity: (templateId: '{:s}', buddyActivityName: '{:s}')".format(i['templateId'], buddyActivity['activity']))

                buddyActivity['activityCategoryName'] = buddyActivity['activityCategory']
                try:
                    buddyActivity['activityCategory'] = BuddyActivityCategory.Value(buddyActivity['activityCategory'])
                except ValueError:
                    print("Unknown buddy activity category: (templateId: '{:s}', activityCategoryName: '{:s}')".format(i['templateId'], buddyActivity['activityCategory']))

            elif 'buddyEmotionLevelSettings' in i:
                buddyEmotion = i['buddyEmotionLevelSettings']

                if 'emotionAnimation' in buddyEmotion:
                    buddyEmotion['emotionAnimationName'] = buddyEmotion['emotionAnimation']
                    try:
                        buddyEmotion['emotionAnimation'] = BuddyAnimation.Value(buddyEmotion['emotionAnimation'])
                    except ValueError:
                        print("Unknown buddy animation: (templateId: '{:s}', buddyAnimationName: '{:s}')".format(i['templateId'], buddyEmotion['emotionAnimation']))

                buddyEmotion['emotionLevelName'] = buddyEmotion['emotionLevel']
                try:
                    buddyEmotion['emotionLevel'] = BuddyEmotionLevel.Value(buddyEmotion['emotionLevel'])
                except ValueError:
                    print("Unknown buddy emotion level: (templateId: '{:s}', emotionLevelName: '{:s}')".format(i['templateId'], buddyActivity['emotionLevel']))

            elif 'buddyInteractionSettings' in i:
                i['buddyInteractionSettings']['feedItemWhitelistNames'] = i['buddyInteractionSettings']['feedItemWhitelist']
                feedItems = []
                for feedItem in i['buddyInteractionSettings']['feedItemWhitelist']:
                    try:
                        feedItems.append(ItemId.Value(feedItem))
                    except ValueError:
                        print("Unknown item: (templateId: '{:s}', itemName: '{:s}')".format(i['templateId'], feedItem))
                        feedItems.append(feedItem)
                i['buddyInteractionSettings']['feedItemWhitelist'] = feedItems

            elif 'buddyLevelSettings' in i:
                buddyLevel = i['buddyLevelSettings']

                buddyLevel['levelName'] = buddyLevel['level']
                try:
                    buddyLevel['level'] = BuddyLevel.Value(buddyLevel['level'])
                except ValueError:
                    print("Unknown buddy level: (templateId: '{:s}', levelName: '{:s}')".format(i['templateId'], buddyLevel['level']))

                if 'unlockedTraits' in buddyLevel:
                    buddyLevel['unlockedTraitNames'] = buddyLevel['unlockedTraits']
                    traits = []
                    for trait in buddyLevel['unlockedTraits']:
                        try:
                            traits.append(BuddyTrait.Value(trait))
                        except ValueError:
                            print("Unknown buddy trait: (templateId: '{:s}', traitName: '{:s}')".format(i['templateId'], trait))
                            traits.append(trait)
                    buddyLevel['unlockedTraits'] = traits

            elif 'combatType' in i:
                i['combatType']['typeName'] = i['combatType']['type']
                try:
                    i['combatType']['type'] = PokemonType.Value(i['combatType']['type'])
                except ValueError:
                    print("Unknown type: (templateId: '{:s}', typeName: '{:s}')".format(i['templateId'], i['combatType']['type']))

            elif 'vsSeekerLoot' in i:
                for j, reward in enumerate(i['vsSeekerLoot']['reward']):
                    # Yes, double/nested 'item'
                    if 'item' in reward and 'item' in reward['item']:
                        reward['item']['itemName'] = reward['item']['item']
                        try:
                            reward['item']['item'] = ItemId.Value(reward['item']['item'])
                        except ValueError:
                            print("Unknown item: (templateId: '{:s}', itemName: '{:s}')".format(i['templateId'], reward['item']['item']))

            elif 'vsSeekerPokemonRewards' in i:
                for j, availablePokemon in enumerate(i['vsSeekerPokemonRewards']['availablePokemon']):
                    thePokemon = None
                    if 'pokemon' in availablePokemon:
                        thePokemon = availablePokemon['pokemon']
                    elif 'guaranteedLimitedPokemonReward' in availablePokemon:
                        thePokemon = availablePokemon['guaranteedLimitedPokemonReward']['pokemon']

                    if thePokemon is not None:
                        thePokemon['pokemonName'] = thePokemon['pokemonId']
                        try:
                            thePokemon['pokemonId'] = PokemonId.Value(thePokemon['pokemonId'])
                        except ValueError:
                            print("Unknown pokemon: (templateId: '{:s}', pokemonName: '{:s}')".format(i['templateId'], availablePokemon['pokemonId']))

                        if 'pokemonDisplay' in thePokemon and 'form' in thePokemon['pokemonDisplay']:
                            thePokemon['pokemonDisplay']['formName'] = thePokemon['pokemonDisplay']['form']
                            try:
                                thePokemon['pokemonDisplay']['form'] = Form.Value(thePokemon['pokemonDisplay']['form'])
                            except ValueError:
                                print("Unknown form: (templateId: '{:s}', formName: '{:s}')".format(i['templateId'], thePokemon['pokemonDisplay']['form']))

            # Find new templates
            else:
                # All of these need no processing / have no enums:
                # Currently these:
                # Already in v1: 'backgroundModeSettings', 'battleSettings', 'combatLeagueSettings', 'combatSettings', 'combatStatStageSettings', 'encounterSettings', 'gymBadgeSettings', 'gymLevel', 'iapSettings', 'luckyPokemonSettings', 'playerLevel', 'pokecoinPurchaseDisplayGmt', 'pokemonUpgrades', 'combatNpcPersonality', 'weatherBonusSettings', 'adventureSyncV2Gmt', 'moveSequenceSettings'
                # New in v2: 'buddyEncounterCameoSettings', 'buddyHungerSettings', 'buddySwapSettings', 'buddyWalkSettings', 'invasionNpcDisplaySettings', 'combatCompetitiveSeasonSettings', 'combatRankingProtoSettings', 'pokestopInvasionAvailabilitySettings', 'limitedPurchaseSkuSettings', 'platypusRolloutSettings', 'vsSeekerClientSettings', 'raidSettings'
                if not any(z in ['backgroundModeSettings', 'battleSettings', 'combatLeagueSettings', 'combatSettings', 'combatStatStageSettings', 'encounterSettings', 'gymBadgeSettings', 'gymLevel', 'iapSettings', 'luckyPokemonSettings', 'playerLevel', 'pokecoinPurchaseDisplayGmt', 'pokemonUpgrades', 'combatNpcPersonality', 'weatherBonusSettings', 'adventureSyncV2Gmt', 'moveSequenceSettings', 'buddyEncounterCameoSettings', 'buddyHungerSettings', 'buddySwapSettings', 'buddyWalkSettings', 'invasionNpcDisplaySettings', 'combatCompetitiveSeasonSettings', 'combatRankingProtoSettings', 'pokestopInvasionAvailabilitySettings', 'limitedPurchaseSkuSettings', 'platypusRolloutSettings', 'vsSeekerClientSettings', 'raidSettings'] for z in i):
                    print('### NEW TEMPLATE FOUND ###')
                    pprint(i.keys())

        return itemTemplates