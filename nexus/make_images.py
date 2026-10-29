"""Builds the Nexus images from one in-game screenshot (panel open, 3440x1484 window capture).
Usage: python3 make_images.py SCREENSHOT.png   -> writes into nexus/images/"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = Path(__file__).parent / "images"
DIN = "/System/Library/Fonts/Supplemental/DIN Condensed Bold.ttf"
AVENIR = "/System/Library/Fonts/Avenir Next.ttc"
ORANGE = (255, 170, 60)

shot = Image.open(sys.argv[1]).convert("RGB")
top = next(y for y in range(200) if sum(shot.getpixel((1720, y))) > 60)  # skip black title strip
game = shot.crop((0, top, shot.width, top + 1440))                       # 3440x1440
view = game.crop((0, 0, 2560, 1440)).resize((1920, 1080), Image.LANCZOS)  # 16:9, panel + generator
panel = shot.crop((20, 140, 760, 1090))                                  # the Cheats panel


def shade(img, box, alpha):
    over = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(over).rectangle(box, fill=(8, 12, 20, alpha))
    return Image.alpha_composite(img.convert("RGBA"), over).convert("RGB")


def text(img, xy, s, font, fill=(255, 255, 255), anchor="la"):
    d = ImageDraw.Draw(img)
    d.text((xy[0] + 3, xy[1] + 3), s, font=font, fill=(0, 0, 0), anchor=anchor)
    d.text(xy, s, font=font, fill=fill, anchor=anchor)


# 1) cover / thumbnail: title on the right, over the city; the panel stays visible on the left
cover = shade(view, (800, 0, 1920, 330), 170)
text(cover, (1860, 40), "DEV MENU (F10)", ImageFont.truetype(DIN, 150), anchor="ra")
text(cover, (1860, 200), "FROSTPUNK'S OWN DEVELOPER PANEL, ONE KEY AWAY", ImageFont.truetype(DIN, 52), ORANGE, "ra")
text(cover, (1860, 262), "Made by 11 bit studios. This mod only switches it on.", ImageFont.truetype(AVENIR, 34), anchor="ra")
cover.save(OUT / "0-cover.png")

# 2) header 1300x372: Nexus draws the mod name, stats and buttons over the lower half -> text on top
band = game.crop((1300, 200, 3440, 812)).resize((1300, 372), Image.LANCZOS)
header = shade(band, (0, 0, 1300, 186), 150)
text(header, (650, 22), "FROSTPUNK DEV MENU (F10)", ImageFont.truetype(DIN, 84), anchor="ma")
text(header, (650, 112), "THE GAME'S OWN DEVELOPER PANEL, ONE KEY AWAY", ImageFont.truetype(DIN, 40), ORANGE, "ma")
header.save(OUT / "header.png")

# 3) close-up padded to 16:9 on a blurred, darkened copy of the scene
bg = view.filter(ImageFilter.GaussianBlur(18))
bg = shade(bg, (0, 0, 1920, 1080), 120)
p = panel.resize((int(panel.width * 1000 / panel.height), 1000), Image.LANCZOS)
bg.paste(p, ((1920 - p.width) // 2, 40))
bg.save(OUT / "1-panel-closeup.png")

# 4) plain in-game view
view.save(OUT / "2-panel-in-game.png")
for f in sorted(OUT.glob("*.png")):
    print(f.name, Image.open(f).size)
