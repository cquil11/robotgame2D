#!/usr/bin/env python3
"""Generate detailed knight sprites at 20x30 with proper left/right mirroring"""

from PIL import Image, ImageDraw
import os

def draw_detailed_knight(image, x, y, direction='right', pose='idle', frame=0):
    """Draw a detailed knight character with shading and highlights"""
    draw = ImageDraw.Draw(image, 'RGBA')
    
    # Colors
    armor_bright = (220, 225, 235)  # bright silver
    armor_mid = (180, 185, 200)     # mid silver
    armor_dark = (140, 145, 165)    # dark silver shadow
    armor_edge = (100, 105, 120)    # edge shadow
    
    cloth_bright = (220, 60, 60)    # bright red
    cloth_mid = (190, 40, 40)       # mid red
    cloth_dark = (140, 20, 20)      # dark red shadow
    
    boot_bright = (150, 90, 50)
    boot_dark = (100, 50, 20)
    
    skin = (230, 190, 160)
    skin_shadow = (200, 160, 130)
    
    sword_bright = (240, 240, 250)
    sword_mid = (200, 200, 210)
    sword_dark = (140, 140, 155)
    
    cx, cy = x + 10, y + 15
    
    if pose == 'idle':
        # HEAD
        draw.ellipse([cx-4, cy-12, cx+4, cy-8], fill=skin)
        draw.ellipse([cx-3, cy-11, cx+3, cy-9], fill=(245, 210, 180))  # highlight
        draw.ellipse([cx-4, cy-10, cx-1, cy-8], fill=skin_shadow)  # shadow
        
        # HELMET - detailed
        # Top dome
        draw.arc([cx-5, cy-13, cx+5, cy-7], 0, 180, fill=armor_mid, width=1)
        draw.polygon([(cx-5, cy-9), (cx-6, cy-7), (cx+6, cy-7), (cx+5, cy-9)], fill=armor_mid)
        # Highlight on dome
        draw.arc([cx-4, cy-12, cx+4, cy-8], 0, 180, fill=armor_bright, width=1)
        # Dark shadow edge
        draw.arc([cx-5, cy-13, cx+5, cy-7], 180, 360, fill=armor_edge, width=1)
        
        # Face guard with horizontal lines
        draw.rectangle([cx-4, cy-8, cx+4, cy-5], fill=armor_dark, outline=armor_edge)
        draw.line([(cx-4, cy-7), (cx+4, cy-7)], fill=armor_edge, width=1)
        # Eye holes
        draw.ellipse([cx-3, cy-7, cx-1, cy-6], fill=(0, 0, 0))
        draw.ellipse([cx+1, cy-7, cx+3, cy-6], fill=(0, 0, 0))
        draw.ellipse([cx-2, cy-6, cx-1, cy-5], fill=(20, 20, 20))  # pupils
        draw.ellipse([cx+1, cy-6, cx+2, cy-5], fill=(20, 20, 20))
        
        # SHOULDERS - pauldrons
        # Right shoulder (viewer's left)
        draw.ellipse([cx-7, cy-5, cx-4, cy+2], fill=armor_mid, outline=armor_dark)
        draw.ellipse([cx-6, cy-4, cx-5, cy+1], fill=armor_bright)  # highlight
        # Left shoulder (viewer's right)
        draw.ellipse([cx+4, cy-5, cx+7, cy+2], fill=armor_mid, outline=armor_dark)
        draw.ellipse([cx+5, cy-4, cx+6, cy+1], fill=armor_bright)
        
        # CHEST PLATE - layered
        # Upper chest
        draw.rectangle([cx-6, cy-3, cx+6, cy+3], fill=armor_mid, outline=armor_edge)
        draw.rectangle([cx-5, cy-2, cx+5, cy+2], fill=armor_bright)  # highlight
        # Center line detail
        draw.line([(cx, cy-3), (cx, cy+3)], fill=armor_dark, width=1)
        # Ribs/details
        draw.line([(cx-4, cy), (cx+4, cy)], fill=armor_dark, width=1)
        
        # Red undershirt
        draw.rectangle([cx-5, cy+1, cx+5, cy+5], fill=cloth_mid)
        draw.rectangle([cx-4, cy+1, cx+4, cy+4], fill=cloth_bright)  # bright side
        draw.rectangle([cx-5, cy+3, cx-1, cy+5], fill=cloth_dark)  # shadow
        
        # WAIST BELT
        draw.rectangle([cx-6, cy+5, cx+6, cy+6], fill=armor_dark, outline=armor_edge)
        draw.line([(cx-5, cy+5), (cx+5, cy+5)], fill=armor_bright, width=1)  # highlight
        
        # RED SKIRT
        draw.polygon([(cx-6, cy+6), (cx-7, cy+13), (cx+7, cy+13), (cx+6, cy+6)], fill=cloth_mid)
        # Highlight on skirt
        draw.polygon([(cx-5, cy+7), (cx-6, cy+11), (cx-1, cy+13)], fill=cloth_bright)
        # Shadow on skirt
        draw.polygon([(cx+2, cy+7), (cx+6, cy+11), (cx+7, cy+13)], fill=cloth_dark)
        
        # LEGS - armored
        # Left leg
        draw.rectangle([cx-4, cy+13, cx-2, cy+28], fill=armor_mid, outline=armor_edge)
        draw.rectangle([cx-3, cy+14, cx-2, cy+27], fill=armor_bright)  # highlight
        # Right leg
        draw.rectangle([cx+2, cy+13, cx+4, cy+28], fill=armor_mid, outline=armor_edge)
        draw.rectangle([cx+2, cy+14, cx+3, cy+27], fill=armor_bright)
        
        # BOOTS
        draw.rectangle([cx-4, cy+28, cx-2, cy+30], fill=boot_dark, outline=(60, 30, 0))
        draw.rectangle([cx+2, cy+28, cx+4, cy+30], fill=boot_dark, outline=(60, 30, 0))
        draw.line([(cx-4, cy+29), (cx-2, cy+29)], fill=boot_bright, width=1)
        draw.line([(cx+2, cy+29), (cx+4, cy+29)], fill=boot_bright, width=1)
        
        # ARMS with gauntlets and SWORD based on direction
        if direction == 'right':
            # Right arm (viewer's left) - relaxed
            draw.rectangle([cx-7, cy-3, cx-6, cy+8], fill=armor_mid, outline=armor_edge)
            draw.rectangle([cx-6, cy-1, cx-5, cy+7], fill=armor_bright)
            # Gauntlet
            draw.rectangle([cx-7, cy+8, cx-5, cy+11], fill=armor_dark, outline=armor_edge)
            draw.ellipse([cx-7, cy+8, cx-5, cy+12], fill=armor_mid)  # knuckles
            
            # Left arm (viewer's right) - holding sword
            draw.rectangle([cx+6, cy-3, cx+7, cy+6], fill=armor_mid, outline=armor_edge)
            draw.rectangle([cx+6, cy-1, cx+7, cy+5], fill=armor_bright)
            # Gauntlet
            draw.rectangle([cx+5, cy+6, cx+7, cy+9], fill=armor_dark, outline=armor_edge)
            draw.ellipse([cx+5, cy+6, cx+7, cy+10], fill=armor_mid)
            
            # SWORD - detailed and raised
            # Blade
            draw.rectangle([cx+7, cy-14, cx+8, cy+5], fill=sword_mid, outline=sword_dark, width=1)
            draw.polygon([(cx+7, cy-14), (cx+9, cy-12), (cx+8, cy+5)], fill=sword_bright)  # highlight
            draw.polygon([(cx+8, cy-14), (cx+9, cy-12), (cx+8, cy+5)], fill=sword_dark)  # shadow
            
            # Crossguard
            draw.rectangle([cx+5, cy+2, cx+9, cy+4], fill=armor_dark, outline=armor_edge)
            draw.ellipse([cx+5, cy+2, cx+9, cy+4], fill=armor_mid)
            
            # Pommel
            draw.ellipse([cx+6, cy+4, cx+8, cy+7], fill=armor_dark, outline=armor_edge)
            draw.ellipse([cx+6, cy+4, cx+8, cy+6], fill=armor_bright)  # highlight
        else:
            # LEFT facing - mirror everything
            # Right arm (viewer's left when facing left) - holding sword
            draw.rectangle([cx-7, cy-3, cx-6, cy+6], fill=armor_mid, outline=armor_edge)
            draw.rectangle([cx-7, cy-1, cx-6, cy+5], fill=armor_bright)
            # Gauntlet
            draw.rectangle([cx-7, cy+6, cx-5, cy+9], fill=armor_dark, outline=armor_edge)
            draw.ellipse([cx-7, cy+6, cx-5, cy+10], fill=armor_mid)
            
            # Left arm (viewer's right when facing left) - relaxed
            draw.rectangle([cx+6, cy-3, cx+7, cy+8], fill=armor_mid, outline=armor_edge)
            draw.rectangle([cx+6, cy-1, cx+7, cy+7], fill=armor_bright)
            # Gauntlet
            draw.rectangle([cx+5, cy+8, cx+7, cy+11], fill=armor_dark, outline=armor_edge)
            draw.ellipse([cx+5, cy+8, cx+7, cy+12], fill=armor_mid)  # knuckles
            
            # SWORD - mirrored
            # Blade
            draw.rectangle([cx-8, cy-14, cx-7, cy+5], fill=sword_mid, outline=sword_dark, width=1)
            draw.polygon([(cx-7, cy-14), (cx-9, cy-12), (cx-8, cy+5)], fill=sword_bright)  # highlight
            draw.polygon([(cx-8, cy-14), (cx-9, cy-12), (cx-8, cy+5)], fill=sword_dark)  # shadow
            
            # Crossguard
            draw.rectangle([cx-9, cy+2, cx-5, cy+4], fill=armor_dark, outline=armor_edge)
            draw.ellipse([cx-9, cy+2, cx-5, cy+4], fill=armor_mid)
            
            # Pommel
            draw.ellipse([cx-8, cy+4, cx-6, cy+7], fill=armor_dark, outline=armor_edge)
            draw.ellipse([cx-8, cy+4, cx-6, cy+6], fill=armor_bright)  # highlight
    
    elif pose == 'jump':
        # Compressed jumping pose
        # HEAD
        draw.ellipse([cx-4, cy-10, cx+4, cy-6], fill=skin)
        draw.ellipse([cx-3, cy-9, cx+3, cy-7], fill=(245, 210, 180))
        
        # HELMET - compressed
        draw.polygon([(cx-5, cy-11), (cx-6, cy-6), (cx+6, cy-6), (cx+5, cy-11)], fill=armor_mid)
        draw.arc([cx-4, cy-11, cx+4, cy-6], 0, 180, fill=armor_bright, width=1)
        
        # Face guard
        draw.rectangle([cx-4, cy-6, cx+4, cy-4], fill=armor_dark)
        draw.ellipse([cx-3, cy-6, cx-1, cy-5], fill=(0, 0, 0))
        draw.ellipse([cx+1, cy-6, cx+3, cy-5], fill=(0, 0, 0))
        
        # SHOULDERS
        draw.ellipse([cx-6, cy-4, cx-3, cy+2], fill=armor_mid, outline=armor_dark)
        draw.ellipse([cx+3, cy-4, cx+6, cy+2], fill=armor_mid, outline=armor_dark)
        
        # CHEST
        draw.rectangle([cx-5, cy-2, cx+5, cy+4], fill=armor_mid, outline=armor_edge)
        draw.rectangle([cx-4, cy-1, cx+4, cy+3], fill=armor_bright)
        
        # Red shirt
        draw.rectangle([cx-4, cy+3, cx+4, cy+6], fill=cloth_mid)
        
        # WAIST
        draw.rectangle([cx-5, cy+6, cx+5, cy+7], fill=armor_dark)
        
        # Bent LEGS
        draw.rectangle([cx-4, cy+7, cx-2, cy+16], fill=armor_mid, outline=armor_edge)
        draw.rectangle([cx+2, cy+7, cx+4, cy+16], fill=armor_mid, outline=armor_edge)
        
        # BOOTS - bent
        draw.rectangle([cx-4, cy+16, cx-2, cy+18], fill=boot_dark)
        draw.rectangle([cx+2, cy+16, cx+4, cy+18], fill=boot_dark)
        
        # ARMS - bent inward
        draw.rectangle([cx-6, cy+0, cx-5, cy+8], fill=armor_mid, outline=armor_edge)
        draw.rectangle([cx+5, cy+0, cx+6, cy+8], fill=armor_mid, outline=armor_edge)
    
    elif pose == 'hit':
        # Recoil pose
        # HEAD - tilted back
        draw.ellipse([cx-3, cy-11, cx+3, cy-8], fill=skin)
        
        # HELMET - tilted
        draw.polygon([(cx-4, cy-12), (cx-5, cy-8), (cx+5, cy-7), (cx+4, cy-11)], fill=armor_mid)
        draw.arc([cx-4, cy-12, cx+4, cy-8], 0, 180, fill=armor_bright, width=1)
        
        # Face guard
        draw.rectangle([cx-4, cy-8, cx+4, cy-5], fill=armor_dark)
        
        # SHOULDERS - leaning back
        draw.ellipse([cx-6, cy-5, cx-3, cy+2], fill=armor_mid, outline=armor_dark)
        draw.ellipse([cx+3, cy-5, cx+6, cy+2], fill=armor_mid, outline=armor_dark)
        
        # CHEST - leaning
        draw.rectangle([cx-5, cy-3, cx+5, cy+5], fill=armor_mid, outline=armor_edge)
        draw.rectangle([cx-4, cy-1, cx+4, cy+4], fill=armor_bright)
        
        # Red shirt
        draw.rectangle([cx-4, cy+3, cx+4, cy+7], fill=cloth_mid)
        
        # LEGS - leaning back
        draw.rectangle([cx-3, cy+7, cx-1, cy+26], fill=armor_mid, outline=armor_edge)
        draw.rectangle([cx+1, cy+9, cx+3, cy+26], fill=armor_mid, outline=armor_edge)
        
        # BOOTS
        draw.rectangle([cx-3, cy+26, cx-1, cy+28], fill=boot_dark)
        draw.rectangle([cx+1, cy+26, cx+3, cy+28], fill=boot_dark)
        
        # ARMS - thrown back
        draw.rectangle([cx-7, cy-2, cx-6, cy+8], fill=armor_mid, outline=armor_edge)
        draw.rectangle([cx+6, cy-2, cx+7, cy+8], fill=armor_mid, outline=armor_edge)


def draw_detailed_attack(image, x, y, direction='right', attack_type='normal', frame=0):
    """Draw detailed attack frames"""
    draw = ImageDraw.Draw(image, 'RGBA')
    
    cx, cy = x + 10, y + 15
    
    # Colors
    armor_bright = (220, 225, 235)
    armor_mid = (180, 185, 200)
    armor_dark = (140, 145, 165)
    armor_edge = (100, 105, 120)
    cloth_bright = (220, 60, 60)
    cloth_mid = (190, 40, 40)
    cloth_dark = (140, 20, 20)
    boot_dark = (100, 50, 20)
    skin = (230, 190, 160)
    sword_bright = (240, 240, 250)
    sword_mid = (200, 200, 210)
    sword_dark = (140, 140, 155)
    
    if attack_type == 'normal':
        # Quick slash animation
        # BASE - similar to idle
        # HEAD
        draw.ellipse([cx-4, cy-12, cx+4, cy-8], fill=skin)
        
        # HELMET
        draw.polygon([(cx-5, cy-13), (cx-6, cy-7), (cx+6, cy-7), (cx+5, cy-13)], fill=armor_mid)
        draw.arc([cx-4, cy-12, cx+4, cy-8], 0, 180, fill=armor_bright, width=1)
        draw.rectangle([cx-4, cy-8, cx+4, cy-5], fill=armor_dark)
        
        # SHOULDERS
        draw.ellipse([cx-7, cy-5, cx-4, cy+2], fill=armor_mid, outline=armor_dark)
        draw.ellipse([cx+4, cy-5, cx+7, cy+2], fill=armor_mid, outline=armor_dark)
        
        # CHEST
        draw.rectangle([cx-6, cy-3, cx+6, cy+3], fill=armor_mid, outline=armor_edge)
        draw.rectangle([cx-5, cy-2, cx+5, cy+2], fill=armor_bright)
        
        # RED SHIRT
        draw.rectangle([cx-5, cy+1, cx+5, cy+5], fill=cloth_mid)
        
        # WAIST
        draw.rectangle([cx-6, cy+5, cx+6, cy+6], fill=armor_dark)
        
        # SKIRT
        draw.polygon([(cx-6, cy+6), (cx-7, cy+13), (cx+7, cy+13), (cx+6, cy+6)], fill=cloth_mid)
        
        # LEGS
        draw.rectangle([cx-4, cy+13, cx-2, cy+28], fill=armor_mid, outline=armor_edge)
        draw.rectangle([cx+2, cy+13, cx+4, cy+28], fill=armor_mid, outline=armor_edge)
        
        # BOOTS
        draw.rectangle([cx-4, cy+28, cx-2, cy+30], fill=boot_dark)
        draw.rectangle([cx+2, cy+28, cx+4, cy+30], fill=boot_dark)
        
        # SWORD SLASH - varies by frame and direction
        if direction == 'right':
            if frame == 0:
                # Ready position
                draw.rectangle([cx+7, cy-12, cx+8, cy+4], fill=sword_mid, outline=sword_dark)
                draw.polygon([(cx+7, cy-12), (cx+9, cy-10), (cx+8, cy+4)], fill=sword_bright)
            elif frame == 1:
                # Mid-slash
                draw.polygon([(cx+5, cy-8), (cx+12, cy-2), (cx+13, cy-4), (cx+6, cy-10)], fill=sword_mid)
                draw.polygon([(cx+5, cy-8), (cx+12, cy-2), (cx+12, cy-3)], fill=sword_bright)
            else:
                # End slash
                draw.polygon([(cx+6, cy+4), (cx+13, cy-4), (cx+14, cy-6), (cx+7, cy+6)], fill=sword_mid)
                draw.polygon([(cx+6, cy+4), (cx+13, cy-4), (cx+13, cy-5)], fill=sword_bright)
        else:
            # LEFT facing - mirror
            if frame == 0:
                # Ready position
                draw.rectangle([cx-8, cy-12, cx-7, cy+4], fill=sword_mid, outline=sword_dark)
                draw.polygon([(cx-7, cy-12), (cx-9, cy-10), (cx-8, cy+4)], fill=sword_bright)
            elif frame == 1:
                # Mid-slash
                draw.polygon([(cx-5, cy-8), (cx-12, cy-2), (cx-13, cy-4), (cx-6, cy-10)], fill=sword_mid)
                draw.polygon([(cx-5, cy-8), (cx-12, cy-2), (cx-12, cy-3)], fill=sword_bright)
            else:
                # End slash
                draw.polygon([(cx-6, cy+4), (cx-13, cy-4), (cx-14, cy-6), (cx-7, cy+6)], fill=sword_mid)
                draw.polygon([(cx-6, cy+4), (cx-13, cy-4), (cx-13, cy-5)], fill=sword_bright)
    
    elif attack_type == 'critical':
        # Spinning slash with aura
        # Similar base to normal
        draw.ellipse([cx-4, cy-12, cx+4, cy-8], fill=skin)
        draw.polygon([(cx-5, cy-13), (cx-6, cy-7), (cx+6, cy-7), (cx+5, cy-13)], fill=armor_mid)
        draw.rectangle([cx-4, cy-8, cx+4, cy-5], fill=armor_dark)
        draw.ellipse([cx-7, cy-5, cx-4, cy+2], fill=armor_mid, outline=armor_dark)
        draw.ellipse([cx+4, cy-5, cx+7, cy+2], fill=armor_mid, outline=armor_dark)
        draw.rectangle([cx-6, cy-3, cx+6, cy+3], fill=armor_mid, outline=armor_edge)
        draw.rectangle([cx-5, cy+1, cx+5, cy+5], fill=cloth_mid)
        draw.rectangle([cx-6, cy+5, cx+6, cy+6], fill=armor_dark)
        draw.polygon([(cx-6, cy+6), (cx-7, cy+13), (cx+7, cy+13), (cx+6, cy+6)], fill=cloth_mid)
        draw.rectangle([cx-4, cy+13, cx-2, cy+28], fill=armor_mid, outline=armor_edge)
        draw.rectangle([cx+2, cy+13, cx+4, cy+28], fill=armor_mid, outline=armor_edge)
        draw.rectangle([cx-4, cy+28, cx-2, cy+30], fill=boot_dark)
        draw.rectangle([cx+2, cy+28, cx+4, cy+30], fill=boot_dark)
        
        # Blue aura
        draw.ellipse([cx-8, cy-6, cx+8, cy+8], fill=(100, 150, 255, 80))
        
        # Spinning sword - direction based
        if direction == 'right':
            draw.polygon([(cx+7, cy-10), (cx+14, cy-3), (cx+13, cy-1), (cx+6, cy-8)], fill=sword_mid)
            draw.polygon([(cx+7, cy-10), (cx+14, cy-3), (cx+14, cy-4)], fill=sword_bright)
        else:
            draw.polygon([(cx-7, cy-10), (cx-14, cy-3), (cx-13, cy-1), (cx-6, cy-8)], fill=sword_mid)
            draw.polygon([(cx-7, cy-10), (cx-14, cy-3), (cx-14, cy-4)], fill=sword_bright)
    
    elif attack_type == 'heavy':
        # Overhead swing
        draw.ellipse([cx-4, cy-12, cx+4, cy-8], fill=skin)
        draw.polygon([(cx-5, cy-13), (cx-6, cy-7), (cx+6, cy-7), (cx+5, cy-13)], fill=armor_mid)
        draw.rectangle([cx-4, cy-8, cx+4, cy-5], fill=armor_dark)
        draw.ellipse([cx-7, cy-5, cx-4, cy+2], fill=armor_mid, outline=armor_dark)
        draw.ellipse([cx+4, cy-5, cx+7, cy+2], fill=armor_mid, outline=armor_dark)
        draw.rectangle([cx-6, cy-3, cx+6, cy+3], fill=armor_mid, outline=armor_edge)
        draw.rectangle([cx-5, cy+1, cx+5, cy+5], fill=cloth_mid)
        draw.rectangle([cx-6, cy+5, cx+6, cy+6], fill=armor_dark)
        draw.polygon([(cx-6, cy+6), (cx-7, cy+13), (cx+7, cy+13), (cx+6, cy+6)], fill=cloth_mid)
        draw.rectangle([cx-4, cy+13, cx-2, cy+28], fill=armor_mid, outline=armor_edge)
        draw.rectangle([cx+2, cy+13, cx+4, cy+28], fill=armor_mid, outline=armor_edge)
        draw.rectangle([cx-4, cy+28, cx-2, cy+30], fill=boot_dark)
        draw.rectangle([cx+2, cy+28, cx+4, cy+30], fill=boot_dark)
        
        # Large overhead sword - direction based
        if direction == 'right':
            if frame < 2:
                # Preparation
                draw.rectangle([cx+7, cy-18, cx+8, cy+2], fill=sword_mid, outline=sword_dark, width=1)
                draw.polygon([(cx+7, cy-18), (cx+9, cy-16), (cx+8, cy+2)], fill=sword_bright)
            else:
                # Swing down
                draw.polygon([(cx+5, cy-10), (cx+14, cy+6), (cx+15, cy+4), (cx+6, cy-12)], fill=sword_mid)
                draw.polygon([(cx+5, cy-10), (cx+14, cy+6), (cx+14, cy+5)], fill=sword_bright)
                # Orange impact glow
                draw.ellipse([cx+10, cy+0, cx+16, cy+8], fill=(255, 140, 0, 60))
        else:
            if frame < 2:
                # Preparation
                draw.rectangle([cx-8, cy-18, cx-7, cy+2], fill=sword_mid, outline=sword_dark, width=1)
                draw.polygon([(cx-7, cy-18), (cx-9, cy-16), (cx-8, cy+2)], fill=sword_bright)
            else:
                # Swing down
                draw.polygon([(cx-5, cy-10), (cx-14, cy+6), (cx-15, cy+4), (cx-6, cy-12)], fill=sword_mid)
                draw.polygon([(cx-5, cy-10), (cx-14, cy+6), (cx-14, cy+5)], fill=sword_bright)
                # Orange impact glow
                draw.ellipse([cx-16, cy+0, cx-10, cy+8], fill=(255, 140, 0, 60))


# Generate all detailed sprites
os.makedirs('images', exist_ok=True)

for direction in ['left', 'right']:
    # Base poses
    poses = [('idle', 'idle'), ('jump', 'jump'), ('hit', 'hit')]
    for pose_name, pose in poses:
        img = Image.new('RGBA', (20, 30), (0, 0, 0, 0))
        draw_detailed_knight(img, 0, 0, direction=direction, pose=pose)
        filename = f'images/player_{direction}.png' if pose_name == 'idle' else f'images/player_{pose_name}_{direction}.png'
        img.save(filename)
        print(f'Generated {filename}')
    
    # Attack animations
    for attack in ['normal', 'critical', 'heavy']:
        frames = 3 if attack != 'heavy' else 4
        for frame in range(frames):
            img = Image.new('RGBA', (20, 30), (0, 0, 0, 0))
            draw_detailed_attack(img, 0, 0, direction=direction, attack_type=attack, frame=frame)
            filename = f'images/player_attack_{attack}_{direction}_{frame}.png'
            img.save(filename)
            print(f'Generated {filename}')

print('[OK] All detailed knight sprites generated at 20x30 with proper mirroring')
