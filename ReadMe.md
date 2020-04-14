Simple / dirty / hacky script that generates pokemon, (combat) moves, types, items, badges and move combinations JSON and CSV files to be used with whatever you want :) This is far from being perfect and done, but it does what it should do (for me ;) ). Feel free to fork, further develop and/or send merge requests!

# Setup
## General
1. Checkout Chrales awesome decrypted asset repo [PogoAssets](https://github.com/ZeChrales/PogoAssets) to the same level as this repo
2. Copy the static text files over from the PogoAssets repo: `cp "../PogoAssets/static_assets/txt/merged.txt" in/translations-pt-br.raw.txt && cp "../PogoAssets/static_assets/txt/merged #5.txt" in/translations-zh-tw.raw.txt && cp "../PogoAssets/static_assets/txt/merged #6.txt" in/translations-en.raw.txt && cp "../PogoAssets/static_assets/txt/merged #10.txt" in/translations-fr.raw.txt && cp "../PogoAssets/static_assets/txt/merged #13.txt" in/translations-de.raw.txt && cp "../PogoAssets/static_assets/txt/merged #16.txt" in/translations-it.raw.txt && cp "../PogoAssets/static_assets/txt/merged #19.txt" in/translations-ja.raw.txt && cp "../PogoAssets/static_assets/txt/merged #21.txt" in/translations-ko.raw.txt && cp "../PogoAssets/static_assets/txt/merged #24.txt" in/translations-es.raw.txt`
3. Generate the text and legacy moves JSON and CSVs: `./compile-helper-json.py`
4. Checkout my (or another fork of the) [POGOProtos](https://github.com/gman-php/POGOProtos) repository somewhere outside this repo
5. Change into the checked out folder and compile those proto definitons to python using `./compile.py python`
6. Move the generated `out/pogoprotos` folder to the root of Pokemon-Go-Data-JSON-Generator, so the structure looks like this: `Pokemon-Go-Data-JSON-Generator/pogoprotos/enums/...`
7. Generate Python virtual env using `virtualenv -ppython3.6 pgodatagen`
8. Install requirements: `pgodatagen/bin/pip3.6 install -r requirements.txt`

## Game Master in JSON format:
v1 and v2:
1. Find and download the latest version of the Game Master file converted to JSON in the [Poke Miners game_masters](https://github.com/PokeMiners/game_masters/tree/master/latest) repository and place it in the `in/game-master-files/json` folder.
2. Change the corresponding symlink in the root folder of this repo to the new downloaded file. E.g. if you have downloaded a v2 JSOn file: `ln -sfn <pathToTheNewGMFile> GAME_MASTER-v2.json`

## Game Master in binary (protobuf) format (copied from phone):
### v1:
1. Download GAME_MASTER file from your phone, located at `Android/data/com.nianticlabs.pokemongo/files/remote_config_cache` and place it in the `in/game-master-files/protobuf` folder.
2. Change the v1 protobuf symlink in the root folder of this repo to the new downloaded file: `ln -sfn <pathToTheNewGMFile> GAME_MASTER-v1.protobuf`

### v2:
The protobuf Game Master in version 2 is unfortunately not (yet?) supported.

# Running
## General
1. Check if there are new translations available: Change into the PogoAssets folder and pull the latest changes: `cd ../PogoAssets && git pull`
2. (Only if any updates were pulled) Copy the updated static text files over to our repo: `cd ../Pokemon-Go-Data-JSON-Generator && cp "../PogoAssets/static_assets/txt/merged.txt" in/translations-pt-br.raw.txt && cp "../PogoAssets/static_assets/txt/merged #5.txt" in/translations-zh-tw.raw.txt && cp "../PogoAssets/static_assets/txt/merged #6.txt" in/translations-en.raw.txt && cp "../PogoAssets/static_assets/txt/merged #10.txt" in/translations-fr.raw.txt && cp "../PogoAssets/static_assets/txt/merged #13.txt" in/translations-de.raw.txt && cp "../PogoAssets/static_assets/txt/merged #16.txt" in/translations-it.raw.txt && cp "../PogoAssets/static_assets/txt/merged #19.txt" in/translations-ja.raw.txt && cp "../PogoAssets/static_assets/txt/merged #21.txt" in/translations-ko.raw.txt && cp "../PogoAssets/static_assets/txt/merged #24.txt" in/translations-es.raw.txt`
3. Check if I have added new legacy moves or did other magic: `git pull`
3. (Only if one of the above `git pull` pulled any updates) Generate the text and legacy moves JSON and CSVs: `./compile-helper-json.py`

## Game Master in JSON format:
### v1:
1. `./run.py json v1`

### v2:
1. `./run.py json v2`

## Game Master in binary (protobuf) format (copied from phone):
1. `./run.py protobuf v1`


# Legacy Moveset Helper Changelog
Last change, 2010-03-05:
- February Community Day: Rhyhorn/Rhyperior (Rock Wrecker)
- January Community Day: Piplup/Empoleon (Hydro Cannon)

Change, 2019-11-25:
- November Community Day: Chimchar/Infernape (Blast Burn)

Change, 2019-10-11:
- October Community Day: Trapinch/Flygon (Earth Power)

Change, 2019-09-15:
- September Community Day: Turtwig/Torterra (Frenzy Plant)

Change, 2019-08-28:
- August Community Day: Ralts/Gardevoir/Gallade (Synchronoise)
- Water Festival: Kingler/Crawdaunt (Crabhammer)

Change, 2019-07-22:
- July Community Day: Mudkip/Swampert (Hydro Cannon)

Change, 2019-07-10:
- June Community Day: Slakoth/Slaking (Body Slam)

Change, 2019-05-29:
- Snorlax Special Day: Added QM Yawn

Change, 2019-05-25:
- Lapras Day: Actually not added anything, as were already former legacy moves

Change, 2019-05-19:
- April Community Day: Bagon/Salamence (Outrage)
- May Community Day: Torchic/Blaziken (Blast Burn)

Change, 2019-04-10:
- February Community Day: Swinub/Mamoswine
- March Community Day: Treecko/Sceptile

Change, 2019-01-29:
- Hoenn Event: Breloom

Change, 2018-11-15:
- January Community Day: Totodile/Feraligatr

Change, 2018-11-15:
- October Community Day: Beldum/Metagross
- November Community Day: Cyndaquil/Typhlosion

Change, 2018-09-17:
- Gengar Day (Lick/Psychic)
- MewTwo legacy moves
- All community days up to Eevee
- Snorlax Research Breakthrough
- Bird days
