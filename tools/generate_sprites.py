"""
Generate placeholder medieval monster and arrow sprites using Pillow.
Run:
     pip install pillow
     python tools/generate_sprites.py

This will create multiple files under `images/`:
  - monster_medieval.png (128x128)
  - monster_medieval_pixel.png (64x64 pixel-art)
  - arrow_skeleton.png (48x12)
  - arrow_skeleton_left.png (flipped)
  - arrow_skeleton_anim_0.png / _1.png / _2.png (simple frames)
  - arrow_skeleton_pixel.png (24x8 pixel-art) and left/flipped

These are placeholders you can iterate on.
"""
from PIL import Image, ImageDraw
import os

OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'images')
os.makedirs(OUT_DIR, exist_ok=True)


def save_image(img, name):
     path = os.path.join(OUT_DIR, name)
     img.save(path)
     print('Wrote', path)


# --- Vector-style medieval monster (128x128)
W, H = 128, 128
monster = Image.new('RGBA', (W, H), (0, 0, 0, 0))
draw = ImageDraw.Draw(monster)

# Body / head (rounded)
draw.ellipse((16, 20, W - 16, H - 24), fill=(90, 60, 40, 255), outline=(30, 20, 10, 255))

# Horns
draw.polygon([(28, 36), (40, 8), (52, 36)], fill=(200, 200, 200, 255))
draw.polygon([(W - 28, 36), (W - 40, 8), (W - 52, 36)], fill=(200, 200, 200, 255))

# Eyes
draw.ellipse((42, 54, 54, 66), fill=(255, 255, 255, 255))
draw.ellipse((W - 54, 54, W - 42, 66), fill=(255, 255, 255, 255))
draw.ellipse((46, 58, 50, 62), fill=(0, 0, 0, 255))
draw.ellipse((W - 50, 58, W - 46, 62), fill=(0, 0, 0, 255))

# Mouth / fangs
draw.rectangle((50, 84, W - 50, 92), fill=(140, 40, 40, 255))
draw.polygon([(58, 92), (62, 92), (60, 100)], fill=(255, 255, 255, 255))
draw.polygon([(W - 58, 92), (W - 62, 92), (W - 60, 100)], fill=(255, 255, 255, 255))

# Shoulder armor / plate
draw.rectangle((18, 70, 110, 104), fill=(60, 60, 80, 255))
draw.line((18, 70, 110, 70), fill=(30, 30, 40, 255), width=3)

# Decorative emblem
draw.ellipse((W // 2 - 12, 36, W // 2 + 12, 64), fill=(160, 80, 40, 255))
draw.line((W // 2, 44, W // 2, 56), fill=(30, 20, 10, 255), width=2)

save_image(monster, 'monster_medieval.png')


# --- Pixel-art monster (64x64) - drawn low-res then scaled
PW, PH = 32, 32
p = Image.new('RGBA', (PW, PH), (0, 0, 0, 0))
pd = ImageDraw.Draw(p)

# Simple blocky face
pd.rectangle((6, 6, PW - 6, PH - 10), fill=(90, 60, 40, 255))
pd.rectangle((8, 10, 12, 14), fill=(255, 255, 255, 255))
pd.rectangle((PW - 12, 10, PW - 8, 14), fill=(255, 255, 255, 255))
pd.rectangle((10, PH - 10, PW - 10, PH - 6), fill=(140, 40, 40, 255))

# Scale up using nearest for pixel-art
pixel_monster = p.resize((64, 64), Image.NEAREST)
save_image(pixel_monster, 'monster_medieval_pixel.png')


# --- Arrow (48x12) - right-facing
AW, AH = 48, 12
arrow = Image.new('RGBA', (AW, AH), (0, 0, 0, 0))
ad = ImageDraw.Draw(arrow)

# Shaft
ad.rectangle((6, AH // 2 - 2, AW - 12, AH // 2 + 2), fill=(120, 80, 40, 255))

# Head (triangle)
ad.polygon([(AW - 12, 1), (AW - 1, AH // 2), (AW - 12, AH - 1)], fill=(180, 40, 40, 255))

# Fletching
ad.polygon([(2, AH // 2), (6, AH // 2 - 4), (6, AH // 2 + 4)], fill=(40, 120, 200, 255))
ad.polygon([(0, AH // 2 - 2), (4, AH // 2 - 6), (4, AH // 2 + 2)], fill=(30, 100, 180, 255))

save_image(arrow, 'arrow_skeleton.png')

# Left-facing (flipped)
save_image(arrow.transpose(Image.FLIP_LEFT_RIGHT), 'arrow_skeleton_left.png')

# Simple animated frames (change fletching color slightly)
for i, color in enumerate([(40, 120, 200), (60, 140, 220), (30, 100, 180)]):
     f = Image.new('RGBA', (AW, AH), (0, 0, 0, 0))
     fd = ImageDraw.Draw(f)
     fd.rectangle((6, AH // 2 - 2, AW - 12, AH // 2 + 2), fill=(120, 80, 40, 255))
     fd.polygon([(AW - 12, 1), (AW - 1, AH // 2), (AW - 12, AH - 1)], fill=(180, 40, 40, 255))
     fd.polygon([(2, AH // 2), (6, AH // 2 - 4), (6, AH // 2 + 4)], fill=color + (255,))
     fd.polygon([(0, AH // 2 - 2), (4, AH // 2 - 6), (4, AH // 2 + 2)], fill=(30, 100, 180, 255))
     save_image(f, f'arrow_skeleton_anim_{i}.png')


# Pixel-art arrow (24x8)
PAW, PAH = 24, 8
ap = Image.new('RGBA', (PAW, PAH), (0, 0, 0, 0))
adp = ImageDraw.Draw(ap)
adp.rectangle((3, PAH // 2 - 1, PAW - 6, PAH // 2 + 1), fill=(120, 80, 40, 255))
adp.polygon([(PAW - 6, 1), (PAW - 1, PAH // 2), (PAW - 6, PAH - 1)], fill=(180, 40, 40, 255))
pixel_arrow = ap.resize((48, 16), Image.NEAREST)
save_image(pixel_arrow, 'arrow_skeleton_pixel.png')
save_image(pixel_arrow.transpose(Image.FLIP_LEFT_RIGHT), 'arrow_skeleton_pixel_left.png')

print('\nDone. Generated vector and pixel-art placeholders in images/.')