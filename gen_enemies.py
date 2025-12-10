#!/usr/bin/env python3
"""Generate detailed skeleton and goblin sprites with animations at 20x30"""

from PIL import Image, ImageDraw
import os

def draw_skeleton(image, x, y, pose='idle', frame=0):
    """Draw a skeleton character"""
    draw = ImageDraw.Draw(image, 'RGBA')
    
    cx, cy = x + 10, y + 15
    
    # Colors
    bone_color = (220, 220, 200)
    bone_dark = (180, 180, 160)
    bone_shadow = (140, 140, 120)
    socket_color = (0, 0, 0)
    socket_glow = (50, 50, 50)
    cloth_color = (80, 60, 40)  # brown tattered cloth
    cloth_dark = (50, 30, 20)
    
    if pose == 'idle':
        # SKULL
        draw.ellipse([cx-5, cy-12, cx+5, cy-6], fill=bone_color, outline=bone_dark)
        # Jaw
        draw.rectangle([cx-4, cy-7, cx+4, cy-5], fill=bone_color, outline=bone_dark)
        # Eye sockets
        draw.ellipse([cx-3, cy-10, cx-1, cy-8], fill=socket_color, outline=socket_glow)
        draw.ellipse([cx+1, cy-10, cx+3, cy-8], fill=socket_color, outline=socket_glow)
        # Glow in eyes
        draw.ellipse([cx-2, cy-9, cx-1, cy-9], fill=(100, 200, 100))
        draw.ellipse([cx+1, cy-9, cx+2, cy-9], fill=(100, 200, 100))
        # Nose hole
        draw.ellipse([cx-1, cy-7, cx+1, cy-6], fill=socket_color)
        
        # SPINE - vertebrae
        for i in range(3):
            draw.rectangle([cx-2, cy-4+i*4, cx+2, cy-2+i*4], fill=bone_color, outline=bone_dark)
        
        # RIBCAGE
        draw.polygon([(cx-5, cy), (cx-6, cy+8), (cx+6, cy+8), (cx+5, cy)], fill=bone_dark)
        # Rib details
        draw.line([(cx-4, cy+1), (cx-6, cy+6)], fill=bone_shadow, width=1)
        draw.line([(cx+4, cy+1), (cx+6, cy+6)], fill=bone_shadow, width=1)
        draw.line([(cx-3, cy), (cx-5, cy+7)], fill=bone_shadow, width=1)
        draw.line([(cx+3, cy), (cx+5, cy+7)], fill=bone_shadow, width=1)
        
        # PELVIS
        draw.polygon([(cx-4, cy+8), (cx-5, cy+12), (cx+5, cy+12), (cx+4, cy+8)], fill=bone_color, outline=bone_dark)
        
        # LEGS - bone structure
        # Left leg
        draw.rectangle([cx-4, cy+12, cx-2, cy+27], fill=bone_color, outline=bone_dark)
        # Right leg
        draw.rectangle([cx+2, cy+12, cx+4, cy+27], fill=bone_color, outline=bone_dark)
        # Feet
        draw.rectangle([cx-4, cy+27, cx-2, cy+29], fill=bone_dark)
        draw.rectangle([cx+2, cy+27, cx+4, cy+29], fill=bone_dark)
        
        # ARMS
        # Left arm
        draw.rectangle([cx-6, cy-2, cx-5, cy+10], fill=bone_color, outline=bone_dark)
        draw.ellipse([cx-7, cy+8, cx-4, cy+12], fill=bone_dark)  # hand
        # Right arm
        draw.rectangle([cx+5, cy-2, cx+6, cy+10], fill=bone_color, outline=bone_dark)
        draw.ellipse([cx+4, cy+8, cx+7, cy+12], fill=bone_dark)  # hand
        
        # Tattered cloth wraps around
        draw.polygon([(cx-5, cy+7), (cx-6, cy+13), (cx-3, cy+13)], fill=cloth_color)
        draw.polygon([(cx+5, cy+7), (cx+6, cy+13), (cx+3, cy+13)], fill=cloth_color)
    
    elif pose == 'walk':
        # Similar to idle but with one leg forward
        # SKULL
        draw.ellipse([cx-5, cy-12, cx+5, cy-6], fill=bone_color, outline=bone_dark)
        draw.rectangle([cx-4, cy-7, cx+4, cy-5], fill=bone_color, outline=bone_dark)
        draw.ellipse([cx-3, cy-10, cx-1, cy-8], fill=socket_color, outline=socket_glow)
        draw.ellipse([cx+1, cy-10, cx+3, cy-8], fill=socket_color, outline=socket_glow)
        draw.ellipse([cx-2, cy-9, cx-1, cy-9], fill=(100, 200, 100))
        draw.ellipse([cx+1, cy-9, cx+2, cy-9], fill=(100, 200, 100))
        draw.ellipse([cx-1, cy-7, cx+1, cy-6], fill=socket_color)
        
        # SPINE
        for i in range(3):
            draw.rectangle([cx-2, cy-4+i*4, cx+2, cy-2+i*4], fill=bone_color, outline=bone_dark)
        
        # RIBCAGE
        draw.polygon([(cx-5, cy), (cx-6, cy+8), (cx+6, cy+8), (cx+5, cy)], fill=bone_dark)
        draw.line([(cx-4, cy+1), (cx-6, cy+6)], fill=bone_shadow, width=1)
        draw.line([(cx+4, cy+1), (cx+6, cy+6)], fill=bone_shadow, width=1)
        
        # PELVIS
        draw.polygon([(cx-4, cy+8), (cx-5, cy+12), (cx+5, cy+12), (cx+4, cy+8)], fill=bone_color, outline=bone_dark)
        
        # LEGS - one forward
        draw.rectangle([cx-5, cy+12, cx-3, cy+27], fill=bone_color, outline=bone_dark)
        draw.rectangle([cx+3, cy+12, cx+5, cy+27], fill=bone_color, outline=bone_dark)
        draw.rectangle([cx-5, cy+27, cx-3, cy+29], fill=bone_dark)
        draw.rectangle([cx+3, cy+27, cx+5, cy+29], fill=bone_dark)
        
        # ARMS - swinging
        draw.rectangle([cx-7, cy, cx-5, cy+12], fill=bone_color, outline=bone_dark)
        draw.rectangle([cx+5, cy-4, cx+7, cy+8], fill=bone_color, outline=bone_dark)
    
    elif pose == 'shoot':
        # Skeleton in shooting stance - arms raised
        # SKULL
        draw.ellipse([cx-5, cy-12, cx+5, cy-6], fill=bone_color, outline=bone_dark)
        draw.rectangle([cx-4, cy-7, cx+4, cy-5], fill=bone_color, outline=bone_dark)
        draw.ellipse([cx-3, cy-10, cx-1, cy-8], fill=socket_color, outline=socket_glow)
        draw.ellipse([cx+1, cy-10, cx+3, cy-8], fill=socket_color, outline=socket_glow)
        # Glowing brighter eyes when shooting
        draw.ellipse([cx-2, cy-9, cx-1, cy-9], fill=(150, 255, 150))
        draw.ellipse([cx+1, cy-9, cx+2, cy-9], fill=(150, 255, 150))
        draw.ellipse([cx-1, cy-7, cx+1, cy-6], fill=socket_color)
        
        # SPINE
        for i in range(3):
            draw.rectangle([cx-2, cy-4+i*4, cx+2, cy-2+i*4], fill=bone_color, outline=bone_dark)
        
        # RIBCAGE
        draw.polygon([(cx-5, cy), (cx-6, cy+8), (cx+6, cy+8), (cx+5, cy)], fill=bone_dark)
        draw.line([(cx-4, cy+1), (cx-6, cy+6)], fill=bone_shadow, width=1)
        draw.line([(cx+4, cy+1), (cx+6, cy+6)], fill=bone_shadow, width=1)
        
        # PELVIS
        draw.polygon([(cx-4, cy+8), (cx-5, cy+12), (cx+5, cy+12), (cx+4, cy+8)], fill=bone_color, outline=bone_dark)
        
        # LEGS - standing
        draw.rectangle([cx-4, cy+12, cx-2, cy+27], fill=bone_color, outline=bone_dark)
        draw.rectangle([cx+2, cy+12, cx+4, cy+27], fill=bone_color, outline=bone_dark)
        draw.rectangle([cx-4, cy+27, cx-2, cy+29], fill=bone_dark)
        draw.rectangle([cx+2, cy+27, cx+4, cy+29], fill=bone_dark)
        
        # ARMS - raised up in shooting stance
        draw.rectangle([cx-7, cy-8, cx-5, cy+4], fill=bone_color, outline=bone_dark)
        draw.ellipse([cx-8, cy-10, cx-4, cy-6], fill=bone_dark)  # hand aiming
        draw.rectangle([cx+5, cy-8, cx+7, cy+4], fill=bone_color, outline=bone_dark)
        draw.ellipse([cx+4, cy-10, cx+8, cy-6], fill=bone_dark)  # hand aiming
        
        # Energy orbs forming at hands
        draw.ellipse([cx-8, cy-10, cx-6, cy-8], fill=(100, 200, 100, 150))
        draw.ellipse([cx+6, cy-10, cx+8, cy-8], fill=(100, 200, 100, 150))


def draw_goblin(image, x, y, pose='idle', frame=0):
    """Draw a goblin character"""
    draw = ImageDraw.Draw(image, 'RGBA')
    
    cx, cy = x + 10, y + 15
    
    # Colors
    skin_color = (100, 140, 80)  # greenish
    skin_dark = (70, 100, 50)
    skin_light = (130, 170, 110)
    eye_color = (200, 50, 50)  # red eyes
    eye_dark = (100, 20, 20)
    cloth_color = (60, 80, 40)  # dark green cloth
    cloth_bright = (100, 140, 80)
    boot_color = (50, 50, 50)  # dark boots
    
    if pose == 'idle':
        # HEAD - rounded goblin shape
        draw.ellipse([cx-5, cy-11, cx+5, cy-5], fill=skin_color, outline=skin_dark)
        # Pointed ears
        draw.polygon([(cx-5, cy-10), (cx-7, cy-14), (cx-4, cy-8)], fill=skin_color)
        draw.polygon([(cx+5, cy-10), (cx+7, cy-14), (cx+4, cy-8)], fill=skin_color)
        # Inner ear
        draw.polygon([(cx-5, cy-10), (cx-6, cy-13), (cx-4, cy-8)], fill=skin_light)
        draw.polygon([(cx+5, cy-10), (cx+6, cy-13), (cx+4, cy-8)], fill=skin_light)
        
        # FACE
        # Eyes
        draw.ellipse([cx-3, cy-9, cx-1, cy-7], fill=eye_color)
        draw.ellipse([cx+1, cy-9, cx+3, cy-7], fill=eye_color)
        draw.ellipse([cx-2, cy-8, cx-1, cy-8], fill=eye_dark)  # pupils
        draw.ellipse([cx+1, cy-8, cx+2, cy-8], fill=eye_dark)
        
        # Nose
        draw.polygon([(cx-1, cy-6), (cx+1, cy-6), (cx, cy-4)], fill=skin_dark)
        
        # Mouth - wicked grin
        draw.arc([cx-2, cy-4, cx+2, cy-2], 0, 180, fill=skin_dark, width=1)
        
        # BODY - hunched goblin
        draw.polygon([(cx-5, cy-5), (cx-6, cy+6), (cx+6, cy+6), (cx+5, cy-5)], fill=cloth_color)
        # Highlight
        draw.polygon([(cx-4, cy-4), (cx-5, cy+2), (cx-2, cy+6)], fill=cloth_bright)
        
        # ARMS - short and skinny
        draw.rectangle([cx-7, cy-2, cx-5, cy+8], fill=skin_color, outline=skin_dark)
        draw.ellipse([cx-8, cy+6, cx-4, cy+10], fill=skin_color)  # hands
        draw.rectangle([cx+5, cy-2, cx+7, cy+8], fill=skin_color, outline=skin_dark)
        draw.ellipse([cx+4, cy+6, cx+8, cy+10], fill=skin_color)
        
        # LEGS - bow-legged
        draw.rectangle([cx-5, cy+6, cx-3, cy+26], fill=skin_color, outline=skin_dark)
        draw.rectangle([cx+3, cy+6, cx+5, cy+26], fill=skin_color, outline=skin_dark)
        # Boots
        draw.rectangle([cx-5, cy+26, cx-3, cy+29], fill=boot_color)
        draw.rectangle([cx+3, cy+26, cx+5, cy+29], fill=boot_color)
        # Spikes on boots
        draw.polygon([(cx-5, cy+26), (cx-6, cy+24), (cx-4, cy+26)], fill=(80, 80, 80))
        draw.polygon([(cx+5, cy+26), (cx+6, cy+24), (cx+4, cy+26)], fill=(80, 80, 80))
    
    elif pose == 'walk':
        # Walking animation - one leg forward
        # HEAD
        draw.ellipse([cx-5, cy-11, cx+5, cy-5], fill=skin_color, outline=skin_dark)
        draw.polygon([(cx-5, cy-10), (cx-7, cy-14), (cx-4, cy-8)], fill=skin_color)
        draw.polygon([(cx+5, cy-10), (cx+7, cy-14), (cx+4, cy-8)], fill=skin_color)
        
        # FACE
        draw.ellipse([cx-3, cy-9, cx-1, cy-7], fill=eye_color)
        draw.ellipse([cx+1, cy-9, cx+3, cy-7], fill=eye_color)
        draw.polygon([(cx-1, cy-6), (cx+1, cy-6), (cx, cy-4)], fill=skin_dark)
        
        # BODY
        draw.polygon([(cx-5, cy-5), (cx-6, cy+6), (cx+6, cy+6), (cx+5, cy-5)], fill=cloth_color)
        draw.polygon([(cx-4, cy-4), (cx-5, cy+2), (cx-2, cy+6)], fill=cloth_bright)
        
        # ARMS - relaxed walking
        draw.rectangle([cx-7, cy-2, cx-5, cy+8], fill=skin_color, outline=skin_dark)
        draw.ellipse([cx-8, cy+6, cx-4, cy+10], fill=skin_color)
        draw.rectangle([cx+5, cy-2, cx+7, cy+8], fill=skin_color, outline=skin_dark)
        draw.ellipse([cx+4, cy+6, cx+8, cy+10], fill=skin_color)
        
        # LEGS - one forward in walking stride
        draw.rectangle([cx-5, cy+6, cx-3, cy+25], fill=skin_color, outline=skin_dark)  # back leg
        draw.rectangle([cx+2, cy+8, cx+4, cy+26], fill=skin_color, outline=skin_dark)  # front leg extended
        draw.rectangle([cx-5, cy+25, cx-3, cy+29], fill=boot_color)
        draw.rectangle([cx+2, cy+26, cx+4, cy+29], fill=boot_color)
        draw.polygon([(cx-5, cy+25), (cx-6, cy+23), (cx-4, cy+25)], fill=(80, 80, 80))
        draw.polygon([(cx+2, cy+26), (cx+1, cy+24), (cx+3, cy+26)], fill=(80, 80, 80))
    
    elif pose == 'attack':
        # Attack pose - leaning forward with weapon
        # HEAD - tilted down
        draw.ellipse([cx-4, cy-10, cx+4, cy-4], fill=skin_color, outline=skin_dark)
        draw.polygon([(cx-4, cy-9), (cx-6, cy-13), (cx-3, cy-7)], fill=skin_color)
        draw.polygon([(cx+4, cy-9), (cx+6, cy-13), (cx+3, cy-7)], fill=skin_color)
        
        # FACE
        draw.ellipse([cx-3, cy-8, cx-1, cy-6], fill=eye_color)
        draw.ellipse([cx+1, cy-8, cx+3, cy-6], fill=eye_color)
        draw.polygon([(cx-1, cy-5), (cx+1, cy-5), (cx, cy-3)], fill=skin_dark)
        
        # BODY - leaning forward
        draw.polygon([(cx-4, cy-4), (cx-5, cy+8), (cx+5, cy+8), (cx+4, cy-4)], fill=cloth_color)
        draw.polygon([(cx-3, cy-3), (cx-4, cy+4), (cx-1, cy+8)], fill=cloth_bright)
        
        # ARMS - one extended forward for stabbing
        draw.rectangle([cx-6, cy-1, cx-4, cy+10], fill=skin_color, outline=skin_dark)
        draw.ellipse([cx-7, cy+8, cx-3, cy+12], fill=skin_color)  # hand
        
        draw.rectangle([cx+4, cy+2, cx+6, cy+12], fill=skin_color, outline=skin_dark)
        draw.ellipse([cx+3, cy+10, cx+7, cy+14], fill=skin_color)
        
        # DAGGER - crude stabbing weapon
        draw.rectangle([cx+6, cy+4, cx+7, cy+12], fill=(100, 100, 100))  # handle
        draw.polygon([(cx+7, cy+4), (cx+9, cy+6), (cx+8, cy+12)], fill=(200, 200, 200))  # blade
        draw.polygon([(cx+8, cy+4), (cx+9, cy+6), (cx+8, cy+12)], fill=(150, 150, 150))  # blade shadow
        
        # LEGS
        draw.rectangle([cx-4, cy+8, cx-2, cy+26], fill=skin_color, outline=skin_dark)
        draw.rectangle([cx+2, cy+8, cx+4, cy+26], fill=skin_color, outline=skin_dark)
        draw.rectangle([cx-4, cy+26, cx-2, cy+29], fill=boot_color)
        draw.rectangle([cx+2, cy+26, cx+4, cy+29], fill=boot_color)
    
    elif pose == 'stab':
        # Stabbing animation - extended attack
        # HEAD - lunging forward
        draw.ellipse([cx-3, cy-10, cx+3, cy-4], fill=skin_color, outline=skin_dark)
        draw.polygon([(cx-3, cy-9), (cx-5, cy-13), (cx-2, cy-7)], fill=skin_color)
        draw.polygon([(cx+3, cy-9), (cx+5, cy-13), (cx+2, cy-7)], fill=skin_color)
        
        # FACE - aggressive
        draw.ellipse([cx-2, cy-8, cx, cy-6], fill=eye_color)
        draw.ellipse([cx+1, cy-8, cx+3, cy-6], fill=eye_color)
        
        # BODY - lunging forward
        draw.polygon([(cx-3, cy-4), (cx-4, cy+8), (cx+4, cy+8), (cx+3, cy-4)], fill=cloth_color)
        
        # ARMS - fully extended stab
        draw.rectangle([cx-6, cy+1, cx-4, cy+11], fill=skin_color, outline=skin_dark)
        draw.rectangle([cx+4, cy+0, cx+6, cy+12], fill=skin_color, outline=skin_dark)
        draw.ellipse([cx+3, cy+10, cx+7, cy+14], fill=skin_color)  # forward hand
        
        # DAGGER - deep stab
        draw.rectangle([cx+6, cy+2, cx+7, cy+14], fill=(100, 100, 100))  # handle
        draw.polygon([(cx+7, cy+2), (cx+10, cy+4), (cx+8, cy+14)], fill=(200, 200, 200))  # blade extended
        draw.polygon([(cx+8, cy+2), (cx+10, cy+4), (cx+8, cy+14)], fill=(150, 150, 150))
        
        # LEGS - lunging
        draw.rectangle([cx-3, cy+8, cx-1, cy+26], fill=skin_color, outline=skin_dark)
        draw.rectangle([cx+1, cy+10, cx+3, cy+26], fill=skin_color, outline=skin_dark)
        draw.rectangle([cx-3, cy+26, cx-1, cy+29], fill=boot_color)
        draw.rectangle([cx+1, cy+26, cx+3, cy+29], fill=boot_color)


# Generate skeletons
os.makedirs('images', exist_ok=True)
os.makedirs('images/enemies', exist_ok=True)

print('Generating skeleton sprites...')
# Left skeleton (skel_left)
img = Image.new('RGBA', (20, 30), (0, 0, 0, 0))
draw_skeleton(img, 0, 0, pose='idle')
img.save('images/enemies/skel_left.png')
print('Generated skel_left.png')

# Right skeleton (Skel_right)
img = Image.new('RGBA', (20, 30), (0, 0, 0, 0))
draw_skeleton(img, 0, 0, pose='idle')
img.save('images/enemies/Skel_right.png')
print('Generated Skel_right.png')

# Skeleton walk animation
for frame in range(2):
    img = Image.new('RGBA', (20, 30), (0, 0, 0, 0))
    draw_skeleton(img, 0, 0, pose='walk', frame=frame)
    img.save(f'images/enemies/skeleton_walk_{frame}.png')
    print(f'Generated skeleton_walk_{frame}.png')

# Skeleton shoot animation
for frame in range(2):
    img = Image.new('RGBA', (20, 30), (0, 0, 0, 0))
    draw_skeleton(img, 0, 0, pose='shoot', frame=frame)
    img.save(f'images/enemies/skeleton_shoot_{frame}.png')
    print(f'Generated skeleton_shoot_{frame}.png')

print('\nGenerating goblin sprites...')
# Left goblin (Goblin2)
img = Image.new('RGBA', (20, 30), (0, 0, 0, 0))
draw_goblin(img, 0, 0, pose='idle')
img.save('images/enemies/Goblin2.png')
print('Generated Goblin2.png')

# Right goblin (Goblin)
img = Image.new('RGBA', (20, 30), (0, 0, 0, 0))
draw_goblin(img, 0, 0, pose='idle')
img.save('images/enemies/Goblin.png')
print('Generated Goblin.png')

# Goblin walk animation
for frame in range(2):
    img = Image.new('RGBA', (20, 30), (0, 0, 0, 0))
    draw_goblin(img, 0, 0, pose='walk', frame=frame)
    img.save(f'images/enemies/goblin_walk_{frame}.png')
    print(f'Generated goblin_walk_{frame}.png')

# Goblin attack animation
for frame in range(2):
    img = Image.new('RGBA', (20, 30), (0, 0, 0, 0))
    draw_goblin(img, 0, 0, pose='attack', frame=frame)
    img.save(f'images/enemies/goblin_attack_{frame}.png')
    print(f'Generated goblin_attack_{frame}.png')

# Goblin stab animation
for frame in range(2):
    img = Image.new('RGBA', (20, 30), (0, 0, 0, 0))
    draw_goblin(img, 0, 0, pose='stab', frame=frame)
    img.save(f'images/enemies/goblin_stab_{frame}.png')
    print(f'Generated goblin_stab_{frame}.png')

print('[OK] All skeleton and goblin sprites generated at 20x30')
