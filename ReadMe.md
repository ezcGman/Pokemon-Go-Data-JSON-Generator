Simple / dirty / hacky script that generates Pokemon, Moves, Types and Items JSON files to be used e.g. with pgoapi. This is far from being perfect and done, but it does what it should do (for me ;) ). Feel free to fork, further develop and/or send merge requests!

# Setup
## General
1. Checkout Chrales awesome decrypted asset repo [PogoAssets](https://github.com/ZeChrales/PogoAssets) to the same level as this repo
2. Generate Python virtual env using 'virtualenv -ppython3.5 pgodatagen'
3. Install requirements: 'pgodatagen/bin/pip3.5 install -r requirements.txt'

## Game Master in JSON format:
1. Download the Game Master file via the API and place it in the root dir of this repo
2. Change the 'game_master.json' symlink to point to the downloaded Game Master file
3. ./run_json.py

## Game Master in binary format (copied from phone):
1. Download GAME_MASTER file from your phone, located at 'Android/data/com.nianticlabs.pokemongo/files/remote_config_cache' and place it in the root dir of this repo
2. Change the 'GAME_MASTER' symlink to point to the downloaded GAME_MASTER file
3. Checkout [POGOProtos](https://github.com/Furtif/POGOProtos) (AeonLucids POGOProtos are not maintained anymore) somewhere outside this repo
4. Change into the checked out folder and compile those proto definitons to python using `./compile.py python`
5. Move the generated 'out/pogoprotos' folder to the root of Pokemon-Go-Data-JSON-Generator, so the structure looks like this: 'Pokemon-Go-Data-JSON-Generator/pogoprotos/neworking/...'
6. Go back to Pokemon-Go-Data-JSON-Generator
8. `./run.py`

# Legacy Moveset Helper Changelog
Last change, 2019-01-29:
- Hoenn Event: Breloom

Change, 2018-11-15:
- November Community Day: Totodile

Change, 2018-11-15:
- October Community Day: Beldum
- November Community Day: Cyndaquill

Change, 2018-09-17:
- MewTwo legacy moves
- All community days up to Eevee
- Snorlax Research Breakthrough
- Bird days
