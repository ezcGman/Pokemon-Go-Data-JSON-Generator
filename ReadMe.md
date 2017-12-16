Simple / dirty / hacky script that generates Pokemon, Moves, Types and Items JSON files to be used e.g. with pgoapi. This is far from being perfect and done, but it does what it should do (for me ;) ). Feel free to fork, further develop and/or send merge requests!

# Setup
## General
1. Checkout Chrales awesome decrypted asset repo [PogoAssets](https://github.com/ZeChrales/PogoAssets) to the same level as this repo
2. Generate Python virtual env using 'virtualenv pgodatagen'
3. Install requirements: 'pgodatagen/bin/pip3.3 install -r requirements.txt'

## Game Master in JSON format:
1. Download the Game Master file via the API and place it in the root dir of this repo
2. Change the 'game_master.json' symlink to point to the downloaded GAME_MASTER file
3. ./run_json.py

## Game Master in binary format (copied from phone):
1. Download GAME_MASTER file from your phone, located at 'Android/data/com.nianticlabs.pokemongo/files/remote_config_cache' and place it in the root dir of this repo
2. Change the 'GAME_MASTER' symlink to point to the downloaded GAME_MASTER file
3. Checkout [POGOProtos](https://github.com/AeonLucid/POGOProtos) somewhere outside this repo
4. Compile the latest working proto definiton to python using 'protoc --python_out=out base/vX.YY.Z.proto'
5. Move the generated 'out/base/vX/YY/Z_pb2.py' to the root folder of Pokemon-Go-Data-JSON-Generator and name it 'vX_YY_Z_pb2.py'
6. Go back to Pokemon-Go-Data-JSON-Generator
7. Edit 'run.py' and change the 'from vX_YY_Z_pb2 import *' line to match the just created one
8. ./run.py
