#!/bin/sh
# Builds the release zips:
#   dist/FrostpunkDevMenu-<version>.zip         full: Python script + double-click launchers (GitHub)
#   dist/FrostpunkDevMenu-<version>-nexus.zip   dev_menu.py only (Nexus blocks script launchers)
set -e
cd "$(dirname "$0")"
v=$(python3 dev_menu.py --version)
chmod +x "Install Dev Menu (Mac).command" install-dev-menu-linux.sh
rm -rf dist && mkdir -p "dist/Frostpunk Dev Menu"
cp dev_menu.py "Install Dev Menu (Windows).bat" "Install Dev Menu (Mac).command" \
   install-dev-menu-linux.sh "READ ME FIRST.txt" LICENSE "dist/Frostpunk Dev Menu/"
(cd dist && zip -qrX "FrostpunkDevMenu-$v.zip" "Frostpunk Dev Menu")
rm -rf "dist/Frostpunk Dev Menu" && mkdir -p "dist/Frostpunk Dev Menu"
cp dev_menu.py "dist/Frostpunk Dev Menu/"
(cd dist && zip -qrX "FrostpunkDevMenu-$v-nexus.zip" "Frostpunk Dev Menu")
rm -rf "dist/Frostpunk Dev Menu"
ls dist/*.zip
