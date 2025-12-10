from PIL import Image, ImageDraw, ImageFilter
import os

os.makedirs('images', exist_ok=True)

ARMOR = (200, 205, 215, 255)
ARMOR_DARK = (120, 125, 135, 255)
ARMOR_LIGHT = (235, 240, 248, 255)
CLOTH = (190, 40, 40, 255)
CLOTH_DARK = (140, 25, 25, 255)
LEATHER = (120, 70, 40, 255)
OUTLINE = (35, 35, 45, 255)
VISOR = (70, 75, 90, 255)
SKIN = (230, 200, 170, 255)
GLOW = (255, 220, 140, 200)
STEEL = (215, 215, 225, 255)
STEEL_DARK = (130, 135, 145, 255)
EDGE = (255, 255, 255, 255)

SCALE = 2
BASE_W, BASE_H = 40, 50
HR_W, HR_H = BASE_W * SCALE, BASE_H * SCALE

def add_shade_rect(d, box, base, highlight=None, shadow=None):
    d.rectangle(box, fill=base, outline=OUTLINE)
    x0, y0, x1, y1 = box
    if highlight:
        d.line([(x0, y0), (x1, y0)], fill=highlight, width=max(1, SCALE))
        d.line([(x0, y0), (x0, y1)], fill=highlight, width=max(1, SCALE))
    if shadow:
        d.line([(x0, y1), (x1, y1)], fill=shadow, width=max(1, SCALE))
        d.line([(x1, y0), (x1, y1)], fill=shadow, width=max(1, SCALE))

def draw_knight_base(facing_right=True, swing=False):
    img = Image.new('RGBA', (HR_W, HR_H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    offset_x = 12 * SCALE if facing_right else HR_W - 12 * SCALE - 16 * SCALE
    offset_y = 12 * SCALE

    # Legs
    add_shade_rect(d, [offset_x, offset_y + 20 * SCALE, offset_x + 16 * SCALE, offset_y + 30 * SCALE], CLOTH, highlight=CLOTH_DARK)
    add_shade_rect(d, [offset_x, offset_y + 30 * SCALE, offset_x + 16 * SCALE, offset_y + 32 * SCALE], LEATHER, shadow=(90, 50, 30, 255))

    # Torso
    add_shade_rect(d, [offset_x, offset_y + 5 * SCALE, offset_x + 16 * SCALE, offset_y + 20 * SCALE], ARMOR, highlight=ARMOR_LIGHT, shadow=ARMOR_DARK)
    add_shade_rect(d, [offset_x + 2 * SCALE, offset_y + 8 * SCALE, offset_x + 14 * SCALE, offset_y + 17 * SCALE], ARMOR_DARK, highlight=ARMOR_LIGHT)

    # Belt
    add_shade_rect(d, [offset_x, offset_y + 18 * SCALE, offset_x + 16 * SCALE, offset_y + 20 * SCALE], LEATHER, shadow=(80, 50, 25, 255))

    # Shoulders
    add_shade_rect(d, [offset_x - 2 * SCALE, offset_y + 3 * SCALE, offset_x + 18 * SCALE, offset_y + 7 * SCALE], ARMOR_DARK)
    add_shade_rect(d, [offset_x - 2 * SCALE, offset_y + 7 * SCALE, offset_x + 18 * SCALE, offset_y + 10 * SCALE], CLOTH, shadow=CLOTH_DARK)

    # Arms
    arm_y = offset_y + 7 * SCALE
    arm_len = 14 * SCALE if swing else 10 * SCALE
    arm_x = offset_x + (16 * SCALE if facing_right else -arm_len)
    add_shade_rect(d, [arm_x, arm_y, arm_x + arm_len, arm_y + 4 * SCALE], CLOTH, shadow=CLOTH_DARK)
    add_shade_rect(d, [arm_x, arm_y + 4 * SCALE, arm_x + arm_len, arm_y + 6 * SCALE], ARMOR, highlight=ARMOR_LIGHT)

    # Head
    head_w, head_h = 16 * SCALE, 12 * SCALE
    head_x = offset_x - 1 * SCALE
    head_y = offset_y - 8 * SCALE
    add_shade_rect(d, [head_x, head_y, head_x + head_w, head_y + head_h], ARMOR, highlight=ARMOR_LIGHT, shadow=ARMOR_DARK)
    d.rectangle([head_x, head_y + 4 * SCALE, head_x + head_w, head_y + 6 * SCALE], fill=VISOR)
    d.rectangle([head_x + 4 * SCALE, head_y + 6 * SCALE, head_x + 12 * SCALE, head_y + 8 * SCALE], fill=SKIN)
    d.rectangle([head_x + 7 * SCALE, head_y - 2 * SCALE, head_x + 9 * SCALE, head_y + 2 * SCALE], fill=CLOTH)

    # Cape
    cape_x = offset_x + (13 * SCALE if facing_right else -3 * SCALE)
    d.rectangle([cape_x, offset_y + 7 * SCALE, cape_x + 3 * SCALE, offset_y + 30 * SCALE], fill=(150, 20, 20, 140))

    # Sword
    sword_len = 20 * SCALE
    sword_w = 3 * SCALE
    if facing_right:
        sx1, sy1 = arm_x + arm_len, arm_y
        sx2, sy2 = sx1 + sword_len, sy1 - 1 * SCALE
    else:
        sx1, sy1 = arm_x, arm_y
        sx2, sy2 = sx1 - sword_len, sy1 - 1 * SCALE
    d.rectangle([min(sx1, sx2), sy1, max(sx1, sx2), sy2 + sword_w], fill=STEEL, outline=OUTLINE)
    d.line([sx1, sy1, sx2, sy2], fill=EDGE, width=max(1, SCALE))
    guard_w = 5 * SCALE
    if facing_right:
        d.rectangle([sx1 - 1 * SCALE, sy1 + 2 * SCALE, sx1 + guard_w, sy1 + 4 * SCALE], fill=STEEL_DARK, outline=OUTLINE)
    else:
        d.rectangle([sx1 - guard_w, sy1 + 2 * SCALE, sx1 + 1 * SCALE, sy1 + 4 * SCALE], fill=STEEL_DARK, outline=OUTLINE)

    if swing:
        glow_x = sx2
        d.ellipse([glow_x - 3 * SCALE, sy2 - 3 * SCALE, glow_x + 4 * SCALE, sy2 + 4 * SCALE], fill=GLOW)

    return img

def downscale(img, target_w, target_h):
    return img.resize((target_w, target_h), Image.LANCZOS)

# Base sprites
for facing_right in (True, False):
    img = draw_knight_base(facing_right, False)
    final = downscale(img, 40, 50)
    name = 'player_right.png' if facing_right else 'player_left.png'
    final.save(f'images/{name}')
    
    img = draw_knight_base(facing_right, False)
    img = img.transform((HR_W, HR_H), Image.AFFINE, (1, 0, 0, 0, 1, -3 * SCALE))
    final = downscale(img, 40, 50)
    name = 'player_jump_right.png' if facing_right else 'player_jump_left.png'
    final.save(f'images/{name}')
    
    img = draw_knight_base(facing_right, True)
    final = downscale(img, 40, 50)
    name = 'player_hit_right.png' if facing_right else 'player_hit_left.png'
    final.save(f'images/{name}')

# Normal attack
for frame in range(3):
    knight = draw_knight_base(True, swing=frame > 0)
    d = ImageDraw.Draw(knight)
    slash_len = (15 + frame * 8) * SCALE
    alpha = 230 - frame * 60
    d.line([30 * SCALE, 20 * SCALE, 30 * SCALE + slash_len, 17 * SCALE], fill=(255, 240, 160, alpha), width=2 * SCALE)
    d.line([30 * SCALE, 20 * SCALE, 30 * SCALE + slash_len, 23 * SCALE], fill=(255, 240, 160, alpha), width=2 * SCALE)
    glow = Image.new('RGBA', knight.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.line([30 * SCALE, 20 * SCALE, 30 * SCALE + slash_len, 20 * SCALE], fill=(255, 240, 160, alpha//2), width=4 * SCALE)
    glow = glow.filter(ImageFilter.GaussianBlur(2 * SCALE))
    knight = Image.alpha_composite(knight, glow)
    final = downscale(knight, 50, 55)
    final.save(f'images/player_attack_normal_right_{frame}.png')
    final.transpose(Image.FLIP_LEFT_RIGHT).save(f'images/player_attack_normal_left_{frame}.png')

# Critical attack
for frame in range(3):
    knight = draw_knight_base(True, swing=True)
    d = ImageDraw.Draw(knight)
    radius = (10 + frame * 7) * SCALE
    alpha = 230 - frame * 60
    center = (40 * SCALE, 22 * SCALE)
    for i in range(3):
        d.ellipse([center[0]-radius+i*SCALE, center[1]-radius+i*2*SCALE, center[0]+radius-i*SCALE, center[1]+radius+i*2*SCALE], outline=(120, 180, 255, alpha), width=SCALE)
    for i in range(5):
        spark_x = center[0] + radius + i * 3 * SCALE
        spark_y = center[1] + (i - 2) * 4 * SCALE
        d.ellipse([spark_x-SCALE, spark_y-SCALE, spark_x+SCALE, spark_y+SCALE], fill=(190, 230, 255, alpha))
    glow = Image.new('RGBA', knight.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([center[0]-radius-3*SCALE, center[1]-radius-3*SCALE, center[0]+radius+3*SCALE, center[1]+radius+3*SCALE], outline=(120, 180, 255, alpha//2), width=4*SCALE)
    glow = glow.filter(ImageFilter.GaussianBlur(3 * SCALE))
    knight = Image.alpha_composite(knight, glow)
    final = downscale(knight, 55, 60)
    final.save(f'images/player_attack_critical_right_{frame}.png')
    final.transpose(Image.FLIP_LEFT_RIGHT).save(f'images/player_attack_critical_left_{frame}.png')

# Heavy attack
for frame in range(4):
    knight = draw_knight_base(True, swing=True)
    d = ImageDraw.Draw(knight)
    arc_progress = frame / 3.0
    start = -80 + arc_progress * 150
    end = start + 80
    for thick in range(5):
        d.arc([30* SCALE - 25* SCALE + thick, 10* SCALE - 25* SCALE + thick, 30* SCALE + 25* SCALE + thick, 10* SCALE + 25* SCALE + thick], start, end, fill=(255, 170, 100, 240 - frame * 45), width=3 * SCALE)
    if frame == 3:
        for i in range(6):
            d.ellipse([50* SCALE - i* SCALE, 20* SCALE - i* SCALE, 55* SCALE + i* SCALE, 25* SCALE + i* SCALE], outline=(255, 200, 110, 220 - i*30), width=SCALE)
    glow = Image.new('RGBA', knight.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.arc([30* SCALE - 25* SCALE, 10* SCALE - 25* SCALE, 30* SCALE + 25* SCALE, 10* SCALE + 25* SCALE], start, end, fill=(255, 120, 60, 120), width=7 * SCALE)
    glow = glow.filter(ImageFilter.GaussianBlur(4 * SCALE))
    knight = Image.alpha_composite(knight, glow)
    final = downscale(knight, 60, 65)
    final.save(f'images/player_attack_heavy_right_{frame}.png')
    final.transpose(Image.FLIP_LEFT_RIGHT).save(f'images/player_attack_heavy_left_{frame}.png')

print('[OK] Rescaled all knight sprites to match goblin/skeleton size')
