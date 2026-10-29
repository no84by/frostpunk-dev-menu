#!/bin/zsh
# Frostpunk Dev Menu - macOS launcher.
# This file does NOT change the game. It only finds Python and starts dev_menu.py, which does all
# the work. Without this file:   python3 dev_menu.py
cd "$(dirname "$0")" || exit 1

PY=""
for c in /Library/Frameworks/Python.framework/Versions/Current/bin/python3 \
         /opt/homebrew/bin/python3 /usr/local/bin/python3; do
  [[ -x $c ]] && { PY=$c; break; }
done
# /usr/bin/python3 is only real once Apple's command line tools are installed; otherwise it pops up
# an installer dialog instead of running.
[[ -z $PY ]] && xcode-select -p >/dev/null 2>&1 && [[ -x /usr/bin/python3 ]] && PY=/usr/bin/python3

if [[ -z $PY ]]; then
  echo "This installer needs Python 3, which is not installed on this Mac."
  echo "Python is free; get the macOS installer from https://www.python.org/downloads/macos/"
  echo "then double-click this file again."
  read -q "?Open the download page now? [y/N] " && open "https://www.python.org/downloads/macos/"
  echo
else
  "$PY" dev_menu.py "$@"
fi
if [[ -t 0 ]]; then
  echo
  read -k1 "?Press any key to close this window."
  echo
fi
