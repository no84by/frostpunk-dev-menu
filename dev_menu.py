#!/usr/bin/env python3
"""Frostpunk Dev Menu: press F10 in a running city to open/close the game's own built-in
developer panel.

Frostpunk ships a full developer cheat panel, but nothing in the game opens it. This script adds
a few lines of Lua to the game's (empty) GameMain.lua script so that F10 calls the game's own
ShowDebugButtonsPanel / HideDebugButtonsPanel functions.

How the change is made: the game keeps its files in packed archives (common.idx + common.dat).
The changed script is appended to the end of common.dat and its one entry in common.idx is
pointed at it. Nothing in the game is overwritten. A small backup file (common.idx.devmenu.json)
next to the archive remembers the original entry, so `uninstall` puts everything back.

Usage:
  python3 dev_menu.py                     interactive menu
  python3 dev_menu.py install|uninstall|status [--game-dir FOLDER]

Works with the Windows (incl. Proton/Wine/Steam Deck) and macOS versions of Frostpunk 1.
Requires Python 3.6+. Quit Frostpunk first.
"""
import argparse, json, os, re, struct, subprocess, sys, zlib
from pathlib import Path

VERSION = "1.0.0"
GAMEMAIN_ID = 0x962DD588  # GameMain.lua, loaded last at game start; same id on every platform
ARCHIVE = "common"
MARKER = b"[FPMOD] dev-menu"
BACKUP_NAME = "common.idx.devmenu.json"
HDR, ENTRY = 11, 29  # idx: 11-byte header (u32 entry count at offset 3), 29-byte entries <IQQQB

# Input events arrive as (event type, key). Key codes are Windows virtual-key codes on every
# platform (F10 = 121); DIK_F10 is the DirectInput code the game's own constants use.
HOOK = r'''

-- [FPMOD] dev-menu: F10 toggles the built-in developer panel -----------------------------------
pcall(function()
  if not LuaGameDelegate then return end
  local prev = LuaGameDelegate.OnInputEvent
  local shown = false
  function LuaGameDelegate:OnInputEvent(...)
    local r = prev and prev(self, ...)
    local ev, key = ...
    if ev == INPUTEVENT_KEYBOARD_KEYDOWN and (key == 121 or key == DIK_F10) then
      pcall(function()
        shown = not shown
        if shown then ShowDebugButtonsPanel() else HideDebugButtonsPanel() end
      end)
    end
    return r
  end
end)
'''


class Fail(Exception):
    pass


# --- finding the game ----------------------------------------------------------------------------

def steam_roots():
    home = Path.home()
    roots = []
    if sys.platform == "win32":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as k:
                roots.append(Path(winreg.QueryValueEx(k, "SteamPath")[0]))
        except OSError:
            pass
        for env in ("ProgramFiles(x86)", "ProgramFiles"):
            if os.environ.get(env):
                roots.append(Path(os.environ[env]) / "Steam")
    elif sys.platform == "darwin":
        roots.append(home / "Library/Application Support/Steam")
        # Windows Steam inside a Wine wrapper (Sikarugir, Wineskin, CrossOver bottles)
        for pattern in ("Applications/Sikarugir/*.app/Contents/SharedSupport/prefix",
                        "Applications/Wineskin/*.app/Contents/SharedSupport/prefix",
                        "Library/Application Support/CrossOver/Bottles/*"):
            for prefix in home.glob(pattern):
                roots.append(prefix / "drive_c/Program Files (x86)/Steam")
    else:
        roots += [home / ".steam/steam", home / ".local/share/Steam",
                  home / ".var/app/com.valvesoftware.Steam/.local/share/Steam",
                  home / "snap/steam/common/.local/share/Steam"]
    libs = []
    for root in roots:
        libs.append(root)
        vdf = root / "steamapps/libraryfolders.vdf"
        if vdf.exists():
            for p in re.findall(r'"path"\s+"([^"]+)"', vdf.read_text(errors="replace")):
                libs.append(Path(p.replace("\\\\", "\\")))
    return libs


def resources_dir(folder):
    """The folder holding common.idx, given the game folder (or that folder itself)."""
    p = Path(folder).expanduser()
    for cand in (p, p / "Frostpunk.app/Contents/Resources", p / "Contents/Resources"):
        if (cand / "common.idx").is_file() and (cand / "common.dat").is_file():
            return cand.resolve()
    return None


def find_games():
    found = []
    for lib in steam_roots():
        res = resources_dir(lib / "steamapps/common/Frostpunk")
        if res and res not in found:
            found.append(res)
    return found


def game_running():
    try:
        if sys.platform == "win32":
            out = subprocess.run(["tasklist"], stdout=subprocess.PIPE, universal_newlines=True).stdout
            return "frostpunk.exe" in out.lower()
        # macOS build is "Frostpunk"; the Windows build under Proton/Wine shows up as Frostpunk.exe
        return any(subprocess.run(["pgrep", *a], stdout=subprocess.DEVNULL).returncode == 0
                   for a in (["-x", "Frostpunk"], ["-if", r"frostpunk\.exe"]))
    except OSError:
        return False


# --- the archive ---------------------------------------------------------------------------------

class Archive:
    def __init__(self, res):
        self.idx_p, self.dat_p = res / (ARCHIVE + ".idx"), res / (ARCHIVE + ".dat")
        self.backup_p = res / BACKUP_NAME
        self.idx = bytearray(self.idx_p.read_bytes())
        count = struct.unpack_from("<I", self.idx, 3)[0]
        if len(self.idx) != HDR + ENTRY * count:
            raise Fail("common.idx has an unexpected format; this game version is not supported.")
        for i in range(count):
            if struct.unpack_from("<I", self.idx, HDR + ENTRY * i)[0] == GAMEMAIN_ID:
                self.pos = HDR + ENTRY * i
                break
        else:
            raise Fail("GameMain.lua not found in common.idx; this game version is not supported.")

    def entry(self):
        return bytes(self.idx[self.pos:self.pos + ENTRY])

    def read(self):
        _, stored, size, offset, gzipped = struct.unpack("<IQQQB", self.entry())
        with open(self.dat_p, "rb") as dat:
            dat.seek(offset)
            raw = dat.read(stored)
        data = zlib.decompressobj(31).decompress(raw) if gzipped else raw  # streams have no trailer
        if len(data) != size:
            raise Fail("GameMain.lua could not be read; the game files may be damaged.")
        return data

    def installed(self):
        return MARKER in self.read()


def gz(data):
    c = zlib.compressobj(9, zlib.DEFLATED, 31)
    return (c.compress(data) + c.flush())[:-8]  # the game's gzip streams carry no CRC/size trailer


# --- actions -------------------------------------------------------------------------------------

def install(res):
    arc = Archive(res)
    if arc.installed():
        print("Dev Menu is already installed.")
        return
    original = arc.entry()
    src = arc.read().rstrip() + HOOK.replace("\n", "\r\n").encode()
    blob = gz(src)
    dat_size = arc.dat_p.stat().st_size
    backup = {"tool": "frostpunk-dev-menu", "version": VERSION, "entry": original.hex(),
              "dat_size": dat_size, "patched_dat_size": dat_size + len(blob)}
    # write the backup first, so an interrupted install can still be undone
    arc.backup_p.write_text(json.dumps(backup, indent=1))
    with open(arc.dat_p, "ab") as dat:
        dat.write(blob)
    arc.idx[arc.pos:arc.pos + ENTRY] = struct.pack("<IQQQB", GAMEMAIN_ID, len(blob), len(src), dat_size, 1)
    arc.idx_p.write_bytes(arc.idx)
    if Archive(res).read() != src:
        raise Fail("Verification failed after install. Run 'uninstall', or verify the game files in Steam.")
    print("Dev Menu installed. Start Frostpunk, load a city, and press F10.")


def uninstall(res):
    arc = Archive(res)
    if not arc.installed():
        if arc.backup_p.exists():
            arc.backup_p.unlink()  # left over after a Steam update or file verification
        print("Dev Menu is not installed; nothing to do.")
        return
    if not arc.backup_p.exists():
        raise Fail("Dev Menu is installed but its backup file is missing.\n"
                   "Use Steam > Frostpunk > Properties > Installed Files > Verify integrity instead.")
    backup = json.loads(arc.backup_p.read_text())
    arc.idx[arc.pos:arc.pos + ENTRY] = bytes.fromhex(backup["entry"])
    arc.idx_p.write_bytes(arc.idx)
    if arc.dat_p.stat().st_size == backup["patched_dat_size"]:  # our data is last: give the space back
        with open(arc.dat_p, "r+b") as dat:
            dat.truncate(backup["dat_size"])
    arc.backup_p.unlink()
    print("Dev Menu uninstalled. The game is back to its original state.")


def status(res):
    print("Dev Menu is", "INSTALLED" if Archive(res).installed() else "not installed")


ACTIONS = {"install": install, "uninstall": uninstall, "status": status}


# --- interactive menu ----------------------------------------------------------------------------

def ask(prompt):
    try:
        return input(prompt).strip()
    except EOFError:
        return ""


def choose_game():
    games = find_games()
    if len(games) == 1:
        return games[0]
    if games:
        print("Several Frostpunk installs found:")
        for i, g in enumerate(games, 1):
            print("  %d) %s" % (i, g))
        pick = ask("Which one? [1-%d] " % len(games))
        if pick.isdigit() and 1 <= int(pick) <= len(games):
            return games[int(pick) - 1]
        raise Fail("No install chosen.")
    print("Frostpunk was not found in the usual Steam folders.")
    folder = ask("Drag the Frostpunk game folder into this window (or paste its path), then press Enter:\n> ")
    res = resources_dir(folder.strip().strip("'\"").replace("\\ ", " "))
    if not res:
        raise Fail("common.idx was not found in that folder.")
    return res


def interactive():
    print("Frostpunk Dev Menu %s: F10 opens the game's built-in developer panel.\n" % VERSION)
    res = choose_game()
    print("Game files: %s" % res)
    is_on = Archive(res).installed()
    print("Status: Dev Menu is %s.\n" % ("INSTALLED" if is_on else "not installed"))
    choice = ask("[U]ninstall or [Q]uit? " if is_on else "[I]nstall or [Q]uit? ").lower()
    if choice[:1] == ("u" if is_on else "i"):
        if game_running():
            raise Fail("Frostpunk is running. Quit the game first, then try again.")
        (uninstall if is_on else install)(res)


def main():
    ap = argparse.ArgumentParser(description="Frostpunk Dev Menu: F10 opens the game's built-in developer panel.")
    ap.add_argument("action", nargs="?", choices=sorted(ACTIONS), help="leave out for an interactive menu")
    ap.add_argument("--game-dir", help="Frostpunk game folder (default: found automatically)")
    ap.add_argument("--version", action="version", version=VERSION)
    a = ap.parse_args()
    try:
        if not a.action:
            return interactive()
        if a.game_dir:
            res = resources_dir(a.game_dir)
            if not res:
                raise Fail("common.idx was not found under %s" % a.game_dir)
        else:
            games = find_games()
            if len(games) != 1:
                raise Fail("Frostpunk not found automatically. Use --game-dir FOLDER." if not games else
                           "Several installs found; pick one with --game-dir:\n  " + "\n  ".join(map(str, games)))
            res = games[0]
        if a.action != "status" and game_running():
            raise Fail("Frostpunk is running. Quit the game first, then try again.")
        print("Game files: %s" % res)
        ACTIONS[a.action](res)
    except Fail as e:
        print("\nERROR: %s" % e)
        return 1
    except PermissionError as e:
        print("\nERROR: no permission to change the game files (%s)." % e.filename)
        return 1


if __name__ == "__main__":
    sys.exit(main() or 0)
