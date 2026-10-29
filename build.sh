#!/bin/sh
# Builds dist/FrostpunkDevMenu-<version>.zip, the file uploaded to Nexus and GitHub Releases.
set -e
cd "$(dirname "$0")"
v=$(python3 dev_menu.py --version)
chmod +x "Install Dev Menu (Mac).command" install-dev-menu-linux.sh
rm -rf dist && mkdir -p "dist/Frostpunk Dev Menu"
cp dev_menu.py "Install Dev Menu (Windows).bat" "Install Dev Menu (Mac).command" \
   install-dev-menu-linux.sh "READ ME FIRST.txt" LICENSE "dist/Frostpunk Dev Menu/"
(cd dist && zip -qrX "FrostpunkDevMenu-$v.zip" "Frostpunk Dev Menu")
rm -rf "dist/Frostpunk Dev Menu"
echo "dist/FrostpunkDevMenu-$v.zip"
