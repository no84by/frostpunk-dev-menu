#!/usr/bin/env bash
# Frostpunk Dev Menu - Linux / Steam Deck launcher (for the Windows version running in Proton).
# This file does NOT change the game. It only finds Python and starts dev_menu.py, which does all
# the work. Without this file:   python3 dev_menu.py
cd "$(dirname "$0")" || exit 1

if command -v python3 >/dev/null 2>&1; then
  python3 dev_menu.py "$@"
else
  echo "This installer needs Python 3, which is not installed."
  echo "Install it with your package manager, for example:"
  echo "  Debian/Ubuntu/Mint:  sudo apt install python3"
  echo "  Fedora:              sudo dnf install python3"
  echo "  Arch/Manjaro:        sudo pacman -S python"
  echo "Then run this file again."
fi
if [ -t 0 ]; then
  echo
  read -r -n1 -p "Press any key to close."
  echo
fi
