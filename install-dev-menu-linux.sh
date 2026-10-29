#!/usr/bin/env bash
# Frostpunk Dev Menu - Linux / Steam Deck launcher (for the Windows version running in Proton).
# This file does NOT change the game. It only finds Python and starts dev_menu.py, which does all
# the work. Without this file:   python3 dev_menu.py
# If Python is missing it can install it with your package manager (sudo asks for your password).
cd "$(dirname "$0")" || exit 1

if ! command -v python3 >/dev/null 2>&1; then
  echo "This installer needs Python 3, which is not installed."
  cmd=""
  if command -v apt-get >/dev/null 2>&1; then cmd="apt-get install -y python3"
  elif command -v dnf >/dev/null 2>&1; then cmd="dnf install -y python3"
  elif command -v pacman >/dev/null 2>&1; then cmd="pacman -S --noconfirm python"
  elif command -v zypper >/dev/null 2>&1; then cmd="zypper install -y python3"
  fi
  if [ -n "$cmd" ] && [ -t 0 ]; then
    read -r -p "Install it now with: sudo $cmd ? [y/N] " yn
    [ "${yn,,}" = "y" ] && sudo $cmd
  elif [ -z "$cmd" ]; then
    echo "Install python3 with your system's package manager, then run this file again."
  fi
fi

if command -v python3 >/dev/null 2>&1; then
  python3 dev_menu.py "$@"
else
  echo "Python 3 is still not installed; install it, then run this file again."
fi
if [ -t 0 ]; then
  echo
  read -r -n1 -p "Press any key to close."
  echo
fi
