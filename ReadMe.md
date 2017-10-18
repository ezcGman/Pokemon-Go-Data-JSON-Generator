Simple / dirty / hacky script that generates Pokemon, Moves, Types and Items JSON files to be used e.g. with pgoapi. This is far from being perfect and done, but it does what it should do (for me ;) ). Feel free to fork, further develop and/or send merge requests!

HowTo:
1. Download GAME_MASTER file from your phone, located at 'Android/data/com.nianticlabs.pokemongo/files/remote_config_cache'
2. Change the 'GAME_MASTER' symlink to point to the downloaded GAME_MASTER file
3. Checkout [POGOProtos](https://github.com/AeonLucid/POGOProtos) somewhere outside this repo
4. Checkout Chrales awesome decrypted asset repo [PogoAssets](https://github.com/ZeChrales/PogoAssets) to the same level as this repo
5. Compile the latest working proto definiton to python using 'protoc --python_out=out base/vX.YY.Z.proto'
6. Move the generated 'out/base/vX/YY/Z_pb2.py' to the root folder of Pokemon-Go-Data-JSON-Generator and name it 'vX_YY_Z_pb2.py'
7. Go back to Pokemon-Go-Data-JSON-Generator
8. Edit 'run.py' and change the 'from vX_YY_Z_pb2 import *' line to match the just created one
9. Generate Python virtual env using 'virtualenv pgodatagen'
10. Install requirements: 'pgodatagen/bin/pip3.3 install -r requirements.txt'
11. ./run.py
