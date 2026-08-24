#!/bin/bash
# Builds the browser (WASM) version of the game with pygbag and produces
# a web.zip ready to upload to itch.io as an HTML5 game.
set -euo pipefail
cd "$(dirname "$0")"

SRC_FILES=(main.py engine.py entities.py button.py settings.py trivia.py)
SRC_DIRS=(images audios)

rm -rf web_build
mkdir -p web_build

for f in "${SRC_FILES[@]}"; do
    cp "$f" web_build/
done
for d in "${SRC_DIRS[@]}"; do
    cp -R "$d" web_build/
done

cd web_build
python3 -m pygbag --build --archive main.py

echo
echo "Done. Upload web_build/build/web.zip to itch.io (HTML5 embed) or serve web_build/build/web/ directly."
