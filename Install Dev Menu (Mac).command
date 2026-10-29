#!/bin/zsh
# Frostpunk Dev Menu - macOS launcher.
# This file does NOT change the game. It only finds Python and starts dev_menu.py, which does all
# the work. Without this file:   python3 dev_menu.py
# If Python is missing it can download the official python.org installer and open it; you
# approve and finish that installer yourself (macOS asks for your password).
cd "$(dirname "$0")" || exit 1
PY_PKG="https://www.python.org/ftp/python/3.13.16/python-3.13.16-macos11.pkg"

find_python() {
  PY=""
  for c in /Library/Frameworks/Python.framework/Versions/Current/bin/python3 \
           /opt/homebrew/bin/python3 /usr/local/bin/python3; do
    [[ -x $c ]] && { PY=$c; return; }
  done
  # /usr/bin/python3 is only real once Apple's command line tools are installed; otherwise it
  # pops up an installer dialog instead of running.
  xcode-select -p >/dev/null 2>&1 && [[ -x /usr/bin/python3 ]] && PY=/usr/bin/python3
}

find_python
if [[ -z $PY ]]; then
  echo "This installer needs Python 3, which is not installed on this Mac."
  echo "Python is free; the official installer comes from python.org (about 70 MB)."
  if read -q "?Download and open the Python installer now? [y/N] "; then
    echo
    pkg="$(mktemp -d)/python-installer.pkg"
    if curl -fL --progress-bar -o "$pkg" "$PY_PKG" &&
       pkgutil --check-signature "$pkg" | grep -q "Python Software Foundation"; then
      open "$pkg"
      echo "Click through the Python installer window (it asks for your Mac password)."
      echo "Waiting for it to finish..."
      for i in {1..900}; do
        find_python
        [[ -n $PY ]] && ! pgrep -xq Installer && break
        sleep 1
      done
    else
      echo "Download failed or the file is not signed by the Python Software Foundation."
    fi
  fi
  echo
fi

if [[ -n $PY ]]; then
  "$PY" dev_menu.py "$@"
else
  echo "Python is still not installed. Get it from https://www.python.org/downloads/macos/"
  echo "and then double-click this file again."
fi
if [[ -t 0 ]]; then
  echo
  read -k1 "?Press any key to close this window."
  echo
fi
