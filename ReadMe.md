Simple / dirty / hacky script that generates pokemon, (combat) moves, types, items, badges and move combinations JSON and CSV files to be used with whatever you want :) This is far from being perfect and done, but it does what it should do (for me ;) ). Feel free to fork, further develop and/or send merge requests!

# Setup
## General
1. Checkout Chrales awesome decrypted asset repo [PogoAssets](https://github.com/ZeChrales/PogoAssets) to the same level as this repo
2. Copy the static text files over from the PogoAssets repo: `cp "../PogoAssets/static_assets/txt/merged.txt" in/translations-pt-br.raw.txt && cp "../PogoAssets/static_assets/txt/merged #5.txt" in/translations-zh-tw.raw.txt && cp "../PogoAssets/static_assets/txt/merged #6.txt" in/translations-en.raw.txt && cp "../PogoAssets/static_assets/txt/merged #10.txt" in/translations-fr.raw.txt && cp "../PogoAssets/static_assets/txt/merged #13.txt" in/translations-de.raw.txt && cp "../PogoAssets/static_assets/txt/merged #16.txt" in/translations-it.raw.txt && cp "../PogoAssets/static_assets/txt/merged #19.txt" in/translations-ja.raw.txt && cp "../PogoAssets/static_assets/txt/merged #21.txt" in/translations-ko.raw.txt && cp "../PogoAssets/static_assets/txt/merged #24.txt" in/translations-es.raw.txt`
3. Generate the text as also the legacy moves JSON and CSVs: `./compile-helper-json.py`
4. Generate Python virtual env using `virtualenv -ppython3.6 pgodatagen`
5. Install requirements: `pgodatagen/bin/pip3.6 install -r requirements.txt`

## Game Master in JSON format:
Supports both v1 and v2 JSON files provided by Poke Miners: https://github.com/PokeMiners/game_masters. The repo already has the last v1 that was ever sent out and the most up-2-date v2 file at time of last commit. if you need newer files, get them from the linked Poke Miners repo.
Step by step guide coming in next commit!

## Game Master in binary format (copied from phone):
v1 guide:
1. Download GAME_MASTER file from your phone, located at `Android/data/com.nianticlabs.pokemongo/files/remote_config_cache` and place it in the root dir of this repo
2. Change the `GAME_MASTER` symlink to point to the downloaded GAME_MASTER file
3. Checkout [POGOProtos](https://github.com/Furtif/POGOProtos) (AeonLucids POGOProtos are not maintained anymore) somewhere outside this repo
4. Change into the checked out folder and compile those proto definitons to python using `./compile.py python`
5. Move the generated `out/pogoprotos` folder to the root of Pokemon-Go-Data-JSON-Generator, so the structure looks like this: `Pokemon-Go-Data-JSON-Generator/pogoprotos/neworking/...`
v2 guide coming in next commit!

# Running
## Game Master in JSON format:
Step by step guide coming in next commit!

## Game Master in binary format (copied from phone):
Updated step by step guide coming in next commit!
1. Generate the text as also the legacy moves JSON and CSVs: `./compile-helper-json.py`


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
