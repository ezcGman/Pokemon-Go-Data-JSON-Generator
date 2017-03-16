Simple / dirty / hacky script that generates Pokemon, Moves, Types and Items JSON files to be used e.g. with pgoapi. This is far from being perfect and done, but it does what it should do (for me ;) ). Feel free to fork, further develop and/or send merge requests!

HowTo:
1. Download GAME_MASTER file from your phone, located at 'Android/data/com.nianticlabs.pokemongo/files/remote_config_cache'
2. Change the 'GAME_MASTER' symlink to point to the downloaded GAME_MASTER file
3. Checkout POGOProtos
4. Compile the latest working proto definiton to python using 'protoc --python_out=out base/v0.47.1.proto'
5. Move the generated 'out/base/v0/47/1_pb2.py' to the root folder of Pokemon-Go-Data-JSON-Generator and name it 'v0_47_1_pb2.py'
6. Go back to Pokemon-Go-Data-JSON-Generator
7. Generate Python virtual env using 'virtualenv pgodatagen'
8. Install requirements: 'pgodatagen/bin/pip3.3 install -r requirements.txt'
9. ./run.py
