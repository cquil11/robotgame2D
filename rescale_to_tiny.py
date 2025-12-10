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
HR_W, HR_H = 40, 60

def add_shade_rect(d, box, base, highlight=None, shadow=None):
    d.rectangle(box, fill=base, outline=OUTLINE)
    x0, y0, x1, y1 = box
    if highlight:
        d.line([(x0, y0), (x1, y0)], fill=highlight, width=1)
        d.line([(x0, y0), (x0, y1)], fill=highlight, width=1)
    if shadow:
        d.line([(x0, y1), (x1, y1)], fill=shadow, width=1)
        d.line([(x1, y0), (x1, y1)], fill=shadow, width=1)

def draw_knight_base(facing_right=True, swing=False):
    img = Image.new('RGBA', (HR_W, HR_H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    offset_x = 10 if facing_right else HR_W - 10 - 8
    offset_y = 10

    # Legs
    add_shade_rect(d, [offset_x, offset_y + 10, offset_x + 8, offset_y + 15], CLOTH, highlight=CLOTH_DARK)
    add_shade_rect(d, [offset_x, offset_y + 15, offset_x + 8, offset_y + 17], LEATHER, shadow=(90, 50, 30, 255))

    # Torso
    add_shade_rect(d, [offset_x, offset_y + 3, offset_x + 8, offset_y + 10], ARMOR, highlight=ARMOR_LIGHT, shadow=ARMOR_DARK)
    add_shade_rect(d, [offset_x + 1, offset_y + 4, offset_x + 7, offset_y + 9], ARMOR_DARK, highlight=ARMOR_LIGHT)

    # Belt
    add_shade_rect(d, [offset_x, offset_y + 9, offset_x + 8, offset_y + 10], LEATHER, shadow=(80, 50, 25, 255))

    # Shoulders
    add_shade_rect(d, [offset_x - 1, offset_y + 2, offset_x + 9, offset_y + 4], ARMOR_DARK)
    add_shade_rect(d, [offset_x - 1, offset_y + 4, offset_x + 9, offset_y + 5], CLOTH, shadow=CLOTH_DARK)

    # Arms
    arm_y = offset_y + 4
    arm_len = 7 if swing else 5
    arm_x = offset_x + (8 if facing_right else -arm_len)
    add_shade_rect(d, [arm_x, arm_y, arm_x + arm_len, arm_y + 2], CLOTH, shadow=CLOTH_DARK)
    add_shade_rect(d, [arm_x, arm_y + 2, arm_x + arm_len, arm_y + 3], ARMOR, highlight=ARMOR_LIGHT)

    # Head
    head_w, head_h = 8, 6
    head_x = offset_x - 1
    head_y = offset_y - 5
    add_shade_rect(d, [head_x, head_y, head_x + head_w, head_y + head_h], ARMOR, highlight=ARMOR_LIGHT, shadow=ARMOR_DARK)
    d.rectangle([head_x, head_y + 2, head_x + head_w, head_y + 3], fill=VISOR)
    d.rectangle([head_x + 2, head_y + 3, head_x + 6, head_y + 4], fill=SKIN)
    d.rectangle([head_x + 3, head_y - 1, head_x + 5, head_y + 1], fill=CLOTH)

    # Cape
    cape_x = offset_x + (7 if facing_right else -1)
    d.rectangle([cape_x, offset_y + 4, cape_x + 1, offset_y + 15], fill=(150, 20, 20, 140))

    # Sword
    sword_len = 10
    sword_w = 1
    if facing_right:
        sx1, sy1 = arm_x + arm_len, arm_y
        sx2, sy2 = sx1 + sword_len, sy1
    else:
        sx1, sy1 = arm_x, arm_y
        sx2, sy2 = sx1 - sword_len, sy1
    d.rectangle([min(sx1, sx2), sy1, max(sx1, sx2), sy2 + sword_w], fill=STEEL, outline=OUTLINE)
    d.line([sx1, sy1, sx2, sy2], fill=EDGE, width=1)
    guard_w = 2
    if facing_right:
        d.rectangle([sx1, sy1 + 1, sx1 + guard_w, sy1 + 2], fill=STEEL_DARK, outline=OUTLINE)
    else:
        d.rectangle([sx1 - guard_w, sy1 + 1, sx1, sy1 + 2], fill=STEEL_DARK, outline=OUTLINE)

    if swing:
        glow_x = sx2
        d.ellipse([glow_x - 1, sy2 - 1, glow_x + 2, sy2 + 2], fill=GLOW)

    return img

def downscale(img, target_w, target_h):
    return img.resize((target_w, target_h), Image.LANCZOS)

# Base sprites (20x30)
for facing_right in (True, False):
    img = draw_knight_base(facing_right, False)
    final = downscale(img, 20, 30)
    name = 'player_right.png' if facing_right else 'player_left.png'
    final.save(f'images/{name}')
    
    img = draw_knight_base(facing_right, False)
    img = img.transform((HR_W, HR_H), Image.AFFINE, (1, 0, 0, 0, 1, -2))
    final = downscale(img, 20, 30)
    name = 'player_jump_right.png' if facing_right else 'player_jump_left.png'
    final.save(f'images/{name}')
    
    img = draw_knight_base(facing_right, True)
    final = downscale(img, 20, 30)
    name = 'player_hit_right.png' if facing_right else 'player_hit_left.png'
    final.save(f'images/{name}')

# Normal attack (25x35)
for frame in range(3):
    knight = draw_knight_base(True, swing=frame > 0)
    d = ImageDraw.Draw(knight)
    slash_len = 8 + frame * 4
    alpha = 230 - frame * 60
    d.line([20, 12, 20 + slash_len, 10], fill=(255, 240, 160, alpha), width=1)
    d.line([20, 12, 20 + slash_len, 14], fill=(255, 240, 160, alpha), width=1)
    glow = Image.new('RGBA', knight.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.line([20, 12, 20 + slash_len, 12], fill=(255, 240, 160, alpha//2), width=2)
    glow = glow.filter(ImageFilter.GaussianBlur(1))
    knight = Image.alpha_composite(knight, glow)
    final = downscale(knight, 25, 35)
    final.save(f'images/player_attack_normal_right_{frame}.png')
    final.transpose(Image.FLIP_LEFT_RIGHT).save(f'images/player_attack_normal_left_{frame}.png')

# Critical attack (28x38)
for frame in range(3):
    knight = draw_knight_base(True, swing=True)
    d = ImageDraw.Draw(knight)
    radius = 5 + frame * 3
    alpha = 230 - frame * 60
    center = (25, 15)
    for i in range(2):
        d.ellipse([center[0]-radius+i, center[1]-radius+i, center[0]+radius-i, center[1]+radius-i], outline=(120, 180, 255, alpha), width=1)
    for i in range(3):
        spark_x = center[0] + radius + i * 2
        spark_y = center[1] + (i - 1) * 2
        d.ellipse([spark_x-1, spark_y-1, spark_x+1, spark_y+1], fill=(190, 230, 255, alpha))
    glow = Image.new('RGBA', knight.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([center[0]-radius-1, center[1]-radius-1, center[0]+radius+1, center[1]+radius+1], outline=(120, 180, 255, alpha//2), width=2)
    glow = glow.filter(ImageFilter.GaussianBlur(1))
    knight = Image.alpha_composite(knight, glow)
    final = downscale(knight, 28, 38)
    final.save(f'images/player_attack_critical_right_{frame}.png')
    final.transpose(Image.FLIP_LEFT_RIGHT).save(f'images/player_attack_critical_left_{frame}.png')

# Heavy attack (30x40)
for frame in range(4):
    knight = draw_knight_base(True, swing=True)
    d = ImageDraw.Draw(knight)
    arc_progress = frame / 3.0
    start = -80 + arc_progress * 150
    end = start + 80
    for thick in range(2):
        d.arc([20 - 12 + thick, 10 - 12 + thick, 20 + 12 + thick, 10 + 12 + thick], start, end, fill=(255, 170, 100, 240 - frame * 45), width=1)
    if frame == 3:
        for i in range(3):
            d.ellipse([25 - i, 15 - i, 28 + i, 18 + i], outline=(255, 200, 110, 220 - i*30), width=1)
    glow = Image.new('RGBA', knight.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.arc([20 - 12, 10 - 12, 20 + 12, 10 + 12], start, end, fill=(255, 120, 60, 120), width=2)
    glow = glow.filter(ImageFilter.GaussianBlur(1))
    knight = Image.alpha_composite(knight, glow)
    final = downscale(knight, 30, 40)
    final.save(f'images/player_attack_heavy_right_{frame}.png')
    final.transpose(Image.FLIP_LEFT_RIGHT).save(f'images/player_attack_heavy_left_{frame}.png')

print('[OK] Player sprites rescaled to 20x30 to match goblin/skeleton')
