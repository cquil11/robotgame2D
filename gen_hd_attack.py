from PIL import Image, ImageDraw, ImageFilter
import os

# High-detail knight attack sprites with shaded armor and AA downscale
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

SCALE = 2  # draw at 2x then downscale for AA
BASE_W, BASE_H = 95, 80
HR_W, HR_H = BASE_W * SCALE, BASE_H * SCALE
BODY_W, BODY_H = 24 * SCALE, 28 * SCALE


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
    offset_x = 18 * SCALE if facing_right else HR_W - 18 * SCALE - BODY_W
    offset_y = 18 * SCALE

    # Legs / pants with depth
    add_shade_rect(d, [offset_x, offset_y + BODY_H, offset_x + BODY_W, offset_y + BODY_H + 14 * SCALE], CLOTH, highlight=CLOTH_DARK)
    add_shade_rect(d, [offset_x, offset_y + BODY_H + 14 * SCALE, offset_x + BODY_W, offset_y + BODY_H + 18 * SCALE], LEATHER, shadow=(90, 50, 30, 255))

    # Torso armor with paneling
    add_shade_rect(d, [offset_x, offset_y + 8 * SCALE, offset_x + BODY_W, offset_y + BODY_H], ARMOR, highlight=ARMOR_LIGHT, shadow=ARMOR_DARK)
    add_shade_rect(d, [offset_x + 4 * SCALE, offset_y + 12 * SCALE, offset_x + BODY_W - 4 * SCALE, offset_y + BODY_H - 4 * SCALE], ARMOR_DARK, highlight=ARMOR_LIGHT)

    # Belt
    add_shade_rect(d, [offset_x, offset_y + BODY_H - 4 * SCALE, offset_x + BODY_W, offset_y + BODY_H], LEATHER, shadow=(80, 50, 25, 255))

    # Shoulder + sleeves
    add_shade_rect(d, [offset_x - 4 * SCALE, offset_y + 6 * SCALE, offset_x + BODY_W + 4 * SCALE, offset_y + 12 * SCALE], ARMOR_DARK)
    add_shade_rect(d, [offset_x - 4 * SCALE, offset_y + 12 * SCALE, offset_x + BODY_W + 4 * SCALE, offset_y + 16 * SCALE], CLOTH, shadow=CLOTH_DARK)

    # Arms
    arm_y = offset_y + 12 * SCALE
    arm_len = 22 * SCALE if swing else 16 * SCALE
    arm_x = offset_x + (BODY_W if facing_right else -arm_len)
    add_shade_rect(d, [arm_x, arm_y, arm_x + arm_len, arm_y + 6 * SCALE], CLOTH, shadow=CLOTH_DARK)
    add_shade_rect(d, [arm_x, arm_y + 6 * SCALE, arm_x + arm_len, arm_y + 10 * SCALE], ARMOR, highlight=ARMOR_LIGHT)

    # Head / helmet with rim light
    head_w, head_h = 26 * SCALE, 18 * SCALE
    head_x = offset_x - 2 * SCALE
    head_y = offset_y - 12 * SCALE
    add_shade_rect(d, [head_x, head_y, head_x + head_w, head_y + head_h], ARMOR, highlight=ARMOR_LIGHT, shadow=ARMOR_DARK)
    d.rectangle([head_x, head_y + 6 * SCALE, head_x + head_w, head_y + 9 * SCALE], fill=VISOR)
    d.rectangle([head_x + 6 * SCALE, head_y + 9 * SCALE, head_x + head_w - 6 * SCALE, head_y + 12 * SCALE], fill=SKIN)
    # Crest
    d.rectangle([head_x + head_w//2 - 2 * SCALE, head_y - 4 * SCALE, head_x + head_w//2 + 2 * SCALE, head_y + 4 * SCALE], fill=CLOTH)

    # Cape hint
    cape_x = offset_x + (BODY_W - 6 * SCALE if facing_right else -6 * SCALE)
    d.rectangle([cape_x, offset_y + 10 * SCALE, cape_x + 6 * SCALE, offset_y + BODY_H + 12 * SCALE], fill=(150, 20, 20, 140))

    # Sword with edge highlight
    sword_len = 32 * SCALE
    sword_w = 4 * SCALE
    if facing_right:
        sx1, sy1 = arm_x + arm_len, arm_y
        sx2, sy2 = sx1 + sword_len, sy1 - 2 * SCALE
    else:
        sx1, sy1 = arm_x, arm_y
        sx2, sy2 = sx1 - sword_len, sy1 - 2 * SCALE
    d.rectangle([sx1, sy1, sx2, sy2 + sword_w], fill=STEEL, outline=OUTLINE)
    d.line([sx1, sy1, sx2, sy2], fill=EDGE, width=max(1, SCALE))
    guard_w = 8 * SCALE
    if facing_right:
        d.rectangle([sx1 - 2 * SCALE, sy1 + 3 * SCALE, sx1 + guard_w, sy1 + 6 * SCALE], fill=STEEL_DARK, outline=OUTLINE)
    else:
        d.rectangle([sx1 - guard_w, sy1 + 3 * SCALE, sx1 + 2 * SCALE, sy1 + 6 * SCALE], fill=STEEL_DARK, outline=OUTLINE)

    # Weapon glow if swing
    if swing:
        glow_x = sx2
        d.ellipse([glow_x - 4 * SCALE, sy2 - 4 * SCALE, glow_x + 6 * SCALE, sy2 + 6 * SCALE], fill=GLOW)

    return img


def downscale(img, target_w, target_h):
    return img.resize((target_w, target_h), Image.LANCZOS)


def save_attack_frames():
    # Normal (3 frames)
    for frame in range(3):
        knight = draw_knight_base(True, swing=frame > 0)
        d = ImageDraw.Draw(knight)
        slash_len = (20 + frame * 12) * SCALE
        alpha = 230 - frame * 60
        d.line([52 * SCALE, 30 * SCALE, 52 * SCALE + slash_len, 25 * SCALE], fill=(255, 240, 160, alpha), width=3 * SCALE)
        d.line([52 * SCALE, 30 * SCALE, 52 * SCALE + slash_len, 35 * SCALE], fill=(255, 240, 160, alpha), width=3 * SCALE)
        glow = Image.new('RGBA', knight.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        gd.line([52 * SCALE, 30 * SCALE, 52 * SCALE + slash_len, 30 * SCALE], fill=(255, 240, 160, alpha//2), width=6 * SCALE)
        glow = glow.filter(ImageFilter.GaussianBlur(3 * SCALE))
        knight = Image.alpha_composite(knight, glow)
        final = downscale(knight, 80, 70)
        final.save(f'images/player_attack_normal_right_{frame}.png')
        final.transpose(Image.FLIP_LEFT_RIGHT).save(f'images/player_attack_normal_left_{frame}.png')

    # Critical (3 frames)
    for frame in range(3):
        knight = draw_knight_base(True, swing=True)
        d = ImageDraw.Draw(knight)
        radius = (14 + frame * 10) * SCALE
        alpha = 230 - frame * 60
        center = (60 * SCALE, 32 * SCALE)
        for i in range(3):
            d.ellipse([center[0]-radius+i*2*SCALE, center[1]-radius+i*4*SCALE, center[0]+radius-i*2*SCALE, center[1]+radius+i*4*SCALE], outline=(120, 180, 255, alpha), width=2 * SCALE)
        for i in range(6):
            spark_x = center[0] + radius + i * 4 * SCALE
            spark_y = center[1] + (i - 3) * 6 * SCALE
            d.ellipse([spark_x-2*SCALE, spark_y-2*SCALE, spark_x+2*SCALE, spark_y+2*SCALE], fill=(190, 230, 255, alpha))
        glow = Image.new('RGBA', knight.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        gd.ellipse([center[0]-radius-4*SCALE, center[1]-radius-4*SCALE, center[0]+radius+4*SCALE, center[1]+radius+4*SCALE], outline=(120, 180, 255, alpha//2), width=6*SCALE)
        glow = glow.filter(ImageFilter.GaussianBlur(4 * SCALE))
        knight = Image.alpha_composite(knight, glow)
        final = downscale(knight, 90, 75)
        final.save(f'images/player_attack_critical_right_{frame}.png')
        final.transpose(Image.FLIP_LEFT_RIGHT).save(f'images/player_attack_critical_left_{frame}.png')

    # Heavy (4 frames)
    for frame in range(4):
        knight = draw_knight_base(True, swing=True)
        d = ImageDraw.Draw(knight)
        arc_progress = frame / 3.0
        start = -80 + arc_progress * 150
        end = start + 80
        for thick in range(6):
            d.arc([45* SCALE - 38* SCALE + thick, 12* SCALE - 38* SCALE + thick, 45* SCALE + 38* SCALE + thick, 12* SCALE + 38* SCALE + thick], start, end, fill=(255, 170, 100, 240 - frame * 45), width=4 * SCALE)
        if frame == 3:
            for i in range(7):
                d.ellipse([78* SCALE - i*2* SCALE, 28* SCALE - i*2* SCALE, 85* SCALE + i*2* SCALE, 35* SCALE + i*2* SCALE], outline=(255, 200, 110, 220 - i*25), width=2 * SCALE)
        glow = Image.new('RGBA', knight.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        gd.arc([45* SCALE - 38* SCALE, 12* SCALE - 38* SCALE, 45* SCALE + 38* SCALE, 12* SCALE + 38* SCALE], start, end, fill=(255, 120, 60, 120), width=10 * SCALE)
        glow = glow.filter(ImageFilter.GaussianBlur(5 * SCALE))
        knight = Image.alpha_composite(knight, glow)
        final = downscale(knight, 95, 80)
        final.save(f'images/player_attack_heavy_right_{frame}.png')
        final.transpose(Image.FLIP_LEFT_RIGHT).save(f'images/player_attack_heavy_left_{frame}.png')


if __name__ == '__main__':
    save_attack_frames()
    print('[OK] High-detail knight attack sprites regenerated with shading, rim lights, and AA downscale')
