# Nexus Mods upload: form fields

Paste these into the Nexus "Add a mod" form (game: Frostpunk).

**Mod name:** Dev Menu (F10) - Built-in Developer Panel

**Version:** 1.0.0

**Category:** Cheats and God items (or Utilities)

**Summary** (max 255 chars):
Press F10 in a city to open Frostpunk's own built-in developer panel (made by 11 bit studios; this mod only enables it): infinite resources, instant build/research, immortal citizens, weather and more. Windows, Mac, Linux. Reversible.

**Description:** paste `description.bbcode`.

**Tags:** Cheats, Utilities, Gameplay

**Requirements:** none. (Python 3 is used by the installer; if it is missing, the launchers offer to start the official Python installer.)

**Permissions / credits:**
- Credits: Frostpunk and its developer panel: 11 bit studios. Installer: MIT licence.
- Upload permission / modification permission / conversion permission: allowed with credit (it is MIT).
- Asset use permission: N/A (contains no assets).
- Source code: https://github.com/no84by/frostpunk-dev-menu

**Main file:** `FrostpunkDevMenu-1.0.0-nexus.zip` (from `./build.sh`; dev_menu.py only: Nexus blocked the launchers)
- File name on Nexus: Frostpunk Dev Menu 1.0.0
- File description: dev_menu.py only. Quit the game, then run: python3 dev_menu.py (Windows: py -3 dev_menu.py). Double-click launchers: github.com/no84by/frostpunk-dev-menu/releases/latest

**Images** (made by `python3 nexus/make_images.py SCREENSHOT.png` from one in-game screenshot):
- Header (1300x372, text in the top half; Nexus draws the mod name over the bottom half): `images/header.png`
- Gallery (1920x1080), in this order: `images/0-cover.png` (thumbnail), `images/1-panel-closeup.png`, `images/2-panel-in-game.png`

**Requirements:** external resource "Python 3.6 or newer", https://www.python.org/downloads/
