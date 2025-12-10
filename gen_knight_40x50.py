#!/usr/bin/env python3
"""Generate knight sprites at 40x50 (matching enemy size)"""

from PIL import Image, ImageDraw
import os

def draw_knight(image, x, y, direction='right', pose='idle', frame=0):
    """Draw a knight character at the given position"""
    draw = ImageDraw.Draw(image, 'RGBA')
    
    # Flip coordinates for left-facing
    if direction == 'left':
        x = image.width - x
    
    # Colors
    armor_color = (200, 205, 215)  # silver
    armor_dark = (150, 155, 165)
    cloth_color = (190, 40, 40)    # red
    cloth_dark = (140, 30, 30)
    boot_color = (120, 70, 40)     # brown
    skin_color = (220, 180, 150)   # flesh
    sword_color = (215, 215, 225)  # steel
    sword_dark = (160, 160, 170)
    
    # Scale factor for larger sprites
    scale = 2.0
    
    # Base positioning (centered at x, y)
    cx, cy = x + 20, y + 20
    
    if pose == 'idle' or pose == 'walk':
        # Head (small, simple)
        draw.ellipse([cx-8*scale, cy-28*scale, cx+8*scale, cy-18*scale], fill=skin_color)
        
        # Helmet
        draw.polygon([(cx-9*scale, cy-28*scale), (cx-10*scale, cy-22*scale), (cx+10*scale, cy-22*scale), (cx+9*scale, cy-28*scale)], fill=armor_color)
        draw.ellipse([cx-10*scale, cy-26*scale, cx+10*scale, cy-20*scale], outline=armor_dark, width=1)
        
        # Face guard
        draw.rectangle([cx-6*scale, cy-20*scale, cx+6*scale, cy-16*scale], fill=armor_dark)
        
        # Shoulders/armor
        draw.rectangle([cx-14*scale, cy-18*scale, cx-10*scale, cy-8*scale], fill=armor_color)
        draw.rectangle([cx+10*scale, cy-18*scale, cx+14*scale, cy-8*scale], fill=armor_color)
        draw.rectangle([cx-12*scale, cy-15*scale, cx+12*scale, cy-8*scale], fill=armor_color, outline=armor_dark)
        
        # Chest plate
        draw.rectangle([cx-12*scale, cy-8*scale, cx+12*scale, cy+8*scale], fill=armor_color, outline=armor_dark)
        
        # Red undershirt
        draw.rectangle([cx-10*scale, cy-6*scale, cx+10*scale, cy+6*scale], fill=cloth_color)
        
        # Waist belt
        draw.rectangle([cx-12*scale, cy+6*scale, cx+12*scale, cy+8*scale], fill=armor_dark)
        
        # Red skirt
        draw.polygon([(cx-12*scale, cy+8*scale), (cx-14*scale, cy+20*scale), (cx+14*scale, cy+20*scale), (cx+12*scale, cy+8*scale)], fill=cloth_color)
        
        # Legs
        if pose == 'idle':
            # Both legs straight
            draw.rectangle([cx-6*scale, cy+20*scale, cx-3*scale, cy+33*scale], fill=armor_color, outline=armor_dark)
            draw.rectangle([cx+3*scale, cy+20*scale, cx+6*scale, cy+33*scale], fill=armor_color, outline=armor_dark)
        else:
            # Walk pose - one leg forward
            draw.rectangle([cx-8*scale, cy+18*scale, cx-5*scale, cy+33*scale], fill=armor_color, outline=armor_dark)
            draw.rectangle([cx+4*scale, cy+20*scale, cx+7*scale, cy+33*scale], fill=armor_color, outline=armor_dark)
        
        # Boots
        draw.rectangle([cx-6*scale, cy+33*scale, cx-3*scale, cy+36*scale], fill=boot_color)
        draw.rectangle([cx+3*scale, cy+33*scale, cx+6*scale, cy+36*scale], fill=boot_color)
        
        # Arms and sword
        if direction == 'right':
            # Left arm
            draw.rectangle([cx-14*scale, cy-6*scale, cx-12*scale, cy+10*scale], fill=armor_color, outline=armor_dark)
            draw.ellipse([cx-15*scale, cy+8*scale, cx-10*scale, cy+14*scale], fill=skin_color)
            
            # Right arm with sword
            draw.rectangle([cx+12*scale, cy-4*scale, cx+14*scale, cy+8*scale], fill=armor_color, outline=armor_dark)
            
            # Sword held high (idle)
            if pose == 'idle':
                draw.rectangle([cx+14*scale, cy-18*scale, cx+16*scale, cy+4*scale], fill=sword_color, outline=sword_dark)
                # Crossguard
                draw.rectangle([cx+12*scale, cy-2*scale, cx+18*scale, cy+2*scale], fill=armor_color)
                # Pommel
                draw.ellipse([cx+14*scale, cy+2*scale, cx+18*scale, cy+6*scale], fill=armor_dark)
            
            # Hand
            draw.ellipse([cx+14*scale, cy+6*scale, cx+16*scale, cy+10*scale], fill=skin_color)
        else:
            # Left side (mirrored)
            # Right arm
            draw.rectangle([cx+12*scale, cy-6*scale, cx+14*scale, cy+10*scale], fill=armor_color, outline=armor_dark)
            draw.ellipse([cx+10*scale, cy+8*scale, cx+15*scale, cy+14*scale], fill=skin_color)
            
            # Left arm with sword
            draw.rectangle([cx-14*scale, cy-4*scale, cx-12*scale, cy+8*scale], fill=armor_color, outline=armor_dark)
            
            # Sword held high (idle)
            if pose == 'idle':
                draw.rectangle([cx-16*scale, cy-18*scale, cx-14*scale, cy+4*scale], fill=sword_color, outline=sword_dark)
                # Crossguard
                draw.rectangle([cx-18*scale, cy-2*scale, cx-12*scale, cy+2*scale], fill=armor_color)
                # Pommel
                draw.ellipse([cx-18*scale, cy+2*scale, cx-14*scale, cy+6*scale], fill=armor_dark)
            
            # Hand
            draw.ellipse([cx-16*scale, cy+6*scale, cx-14*scale, cy+10*scale], fill=skin_color)
    
    elif pose == 'jump':
        # Jump pose - pulled up, legs bent
        # Head
        draw.ellipse([cx-8*scale, cy-22*scale, cx+8*scale, cy-12*scale], fill=skin_color)
        
        # Helmet
        draw.polygon([(cx-9*scale, cy-22*scale), (cx-10*scale, cy-16*scale), (cx+10*scale, cy-16*scale), (cx+9*scale, cy-22*scale)], fill=armor_color)
        
        # Shoulders/armor
        draw.rectangle([cx-14*scale, cy-12*scale, cx-10*scale, cy-2*scale], fill=armor_color)
        draw.rectangle([cx+10*scale, cy-12*scale, cx+14*scale, cy-2*scale], fill=armor_color)
        draw.rectangle([cx-12*scale, cy-9*scale, cx+12*scale, cy-2*scale], fill=armor_color, outline=armor_dark)
        
        # Chest
        draw.rectangle([cx-12*scale, cy-2*scale, cx+12*scale, cy+6*scale], fill=armor_color, outline=armor_dark)
        draw.rectangle([cx-10*scale, cy+0*scale, cx+10*scale, cy+4*scale], fill=cloth_color)
        
        # Bent legs
        draw.rectangle([cx-8*scale, cy+6*scale, cx-4*scale, cy+16*scale], fill=armor_color, outline=armor_dark)
        draw.rectangle([cx+4*scale, cy+6*scale, cx+8*scale, cy+16*scale], fill=armor_color, outline=armor_dark)
        
        # Boots
        draw.rectangle([cx-8*scale, cy+16*scale, cx-4*scale, cy+18*scale], fill=boot_color)
        draw.rectangle([cx+4*scale, cy+16*scale, cx+8*scale, cy+18*scale], fill=boot_color)
        
        # Arms
        if direction == 'right':
            draw.rectangle([cx-14*scale, cy-4*scale, cx-12*scale, cy+6*scale], fill=armor_color, outline=armor_dark)
            draw.rectangle([cx+12*scale, cy-6*scale, cx+14*scale, cy+4*scale], fill=armor_color, outline=armor_dark)
        else:
            draw.rectangle([cx+12*scale, cy-4*scale, cx+14*scale, cy+6*scale], fill=armor_color, outline=armor_dark)
            draw.rectangle([cx-14*scale, cy-6*scale, cx-12*scale, cy+4*scale], fill=armor_color, outline=armor_dark)
    
    elif pose == 'hit':
        # Hit pose - recoil, arms back
        # Head
        draw.ellipse([cx-7*scale, cy-24*scale, cx+7*scale, cy-16*scale], fill=skin_color)
        
        # Helmet tilted slightly
        draw.polygon([(cx-8*scale, cy-24*scale), (cx-10*scale, cy-20*scale), (cx+10*scale, cy-20*scale), (cx+8*scale, cy-24*scale)], fill=armor_color)
        
        # Shoulders
        draw.rectangle([cx-14*scale, cy-16*scale, cx-10*scale, cy-6*scale], fill=armor_color)
        draw.rectangle([cx+10*scale, cy-16*scale, cx+14*scale, cy-6*scale], fill=armor_color)
        draw.rectangle([cx-12*scale, cy-12*scale, cx+12*scale, cy-6*scale], fill=armor_color, outline=armor_dark)
        
        # Chest - slight lean
        draw.rectangle([cx-11*scale, cy-6*scale, cx+11*scale, cy+8*scale], fill=armor_color, outline=armor_dark)
        draw.rectangle([cx-10*scale, cy-4*scale, cx+10*scale, cy+6*scale], fill=cloth_color)
        
        # Legs leaning back
        draw.rectangle([cx-5*scale, cy+8*scale, cx-2*scale, cy+32*scale], fill=armor_color, outline=armor_dark)
        draw.rectangle([cx+2*scale, cy+10*scale, cx+5*scale, cy+32*scale], fill=armor_color, outline=armor_dark)
        
        # Boots
        draw.rectangle([cx-5*scale, cy+32*scale, cx-2*scale, cy+35*scale], fill=boot_color)
        draw.rectangle([cx+2*scale, cy+32*scale, cx+5*scale, cy+35*scale], fill=boot_color)
        
        # Arms back
        if direction == 'right':
            draw.rectangle([cx-16*scale, cy-8*scale, cx-14*scale, cy+6*scale], fill=armor_color, outline=armor_dark)
            draw.rectangle([cx+14*scale, cy-2*scale, cx+16*scale, cy+8*scale], fill=armor_color, outline=armor_dark)
        else:
            draw.rectangle([cx+14*scale, cy-8*scale, cx+16*scale, cy+6*scale], fill=armor_color, outline=armor_dark)
            draw.rectangle([cx-16*scale, cy-2*scale, cx-14*scale, cy+8*scale], fill=armor_color, outline=armor_dark)


def draw_attack_frame(image, x, y, direction='right', attack_type='normal', frame=0):
    """Draw attack animation frames"""
    draw = ImageDraw.Draw(image, 'RGBA')
    
    # Colors
    armor_color = (200, 205, 215)
    armor_dark = (150, 155, 165)
    cloth_color = (190, 40, 40)
    cloth_dark = (140, 30, 30)
    boot_color = (120, 70, 40)
    skin_color = (220, 180, 150)
    sword_color = (215, 215, 225)
    sword_dark = (160, 160, 170)
    
    scale = 2.0
    cx, cy = x + 20, y + 20
    
    if direction == 'left':
        cx = image.width - cx
    
    if attack_type == 'normal':
        # Normal attack - quick slash
        # Frame 0: Starting pose
        if frame == 0:
            # Standing ready
            draw.ellipse([cx-8*scale, cy-28*scale, cx+8*scale, cy-18*scale], fill=skin_color)
            draw.polygon([(cx-9*scale, cy-28*scale), (cx-10*scale, cy-22*scale), (cx+10*scale, cy-22*scale), (cx+9*scale, cy-28*scale)], fill=armor_color)
            draw.rectangle([cx-12*scale, cy-18*scale, cx+12*scale, cy+8*scale], fill=armor_color, outline=armor_dark)
            draw.rectangle([cx-10*scale, cy-6*scale, cx+10*scale, cy+6*scale], fill=cloth_color)
            draw.rectangle([cx-6*scale, cy+20*scale, cx+6*scale, cy+33*scale], fill=armor_color, outline=armor_dark)
            draw.rectangle([cx-6*scale, cy+33*scale, cx+6*scale, cy+36*scale], fill=boot_color)
            
            if direction == 'right':
                draw.rectangle([cx+12*scale, cy-4*scale, cx+14*scale, cy+8*scale], fill=armor_color, outline=armor_dark)
                draw.rectangle([cx+14*scale, cy-14*scale, cx+16*scale, cy+8*scale], fill=sword_color, outline=sword_dark)
            else:
                draw.rectangle([cx-14*scale, cy-4*scale, cx-12*scale, cy+8*scale], fill=armor_color, outline=armor_dark)
                draw.rectangle([cx-16*scale, cy-14*scale, cx-14*scale, cy+8*scale], fill=sword_color, outline=sword_dark)
        
        # Frame 1: Mid-slash
        elif frame == 1:
            draw.ellipse([cx-8*scale, cy-28*scale, cx+8*scale, cy-18*scale], fill=skin_color)
            draw.polygon([(cx-9*scale, cy-28*scale), (cx-10*scale, cy-22*scale), (cx+10*scale, cy-22*scale), (cx+9*scale, cy-28*scale)], fill=armor_color)
            draw.rectangle([cx-12*scale, cy-18*scale, cx+12*scale, cy+8*scale], fill=armor_color, outline=armor_dark)
            draw.rectangle([cx-10*scale, cy-6*scale, cx+10*scale, cy+6*scale], fill=cloth_color)
            draw.rectangle([cx-6*scale, cy+20*scale, cx+6*scale, cy+33*scale], fill=armor_color, outline=armor_dark)
            draw.rectangle([cx-6*scale, cy+33*scale, cx+6*scale, cy+36*scale], fill=boot_color)
            
            if direction == 'right':
                draw.rectangle([cx+12*scale, cy-6*scale, cx+14*scale, cy+10*scale], fill=armor_color, outline=armor_dark)
                draw.rectangle([cx+14*scale, cy-8*scale, cx+24*scale, cy+0*scale], fill=sword_color, outline=sword_dark, width=1)
            else:
                draw.rectangle([cx-14*scale, cy-6*scale, cx-12*scale, cy+10*scale], fill=armor_color, outline=armor_dark)
                draw.rectangle([cx-24*scale, cy-8*scale, cx-14*scale, cy+0*scale], fill=sword_color, outline=sword_dark, width=1)
        
        # Frame 2: End slash
        elif frame == 2:
            draw.ellipse([cx-8*scale, cy-28*scale, cx+8*scale, cy-18*scale], fill=skin_color)
            draw.polygon([(cx-9*scale, cy-28*scale), (cx-10*scale, cy-22*scale), (cx+10*scale, cy-22*scale), (cx+9*scale, cy-28*scale)], fill=armor_color)
            draw.rectangle([cx-12*scale, cy-18*scale, cx+12*scale, cy+8*scale], fill=armor_color, outline=armor_dark)
            draw.rectangle([cx-10*scale, cy-6*scale, cx+10*scale, cy+6*scale], fill=cloth_color)
            draw.rectangle([cx-6*scale, cy+20*scale, cx+6*scale, cy+33*scale], fill=armor_color, outline=armor_dark)
            draw.rectangle([cx-6*scale, cy+33*scale, cx+6*scale, cy+36*scale], fill=boot_color)
            
            if direction == 'right':
                draw.rectangle([cx+8*scale, cy+0*scale, cx+10*scale, cy+12*scale], fill=armor_color, outline=armor_dark)
                draw.rectangle([cx+10*scale, cy-6*scale, cx+22*scale, cy+12*scale], fill=sword_color, outline=sword_dark, width=1)
            else:
                draw.rectangle([cx-10*scale, cy+0*scale, cx-8*scale, cy+12*scale], fill=armor_color, outline=armor_dark)
                draw.rectangle([cx-22*scale, cy-6*scale, cx-10*scale, cy+12*scale], fill=sword_color, outline=sword_dark, width=1)
    
    elif attack_type == 'critical':
        # Critical attack - spin slash with blue aura
        angle = frame * 120  # Rotate effect
        
        draw.ellipse([cx-8*scale, cy-28*scale, cx+8*scale, cy-18*scale], fill=skin_color)
        draw.polygon([(cx-9*scale, cy-28*scale), (cx-10*scale, cy-22*scale), (cx+10*scale, cy-22*scale), (cx+9*scale, cy-28*scale)], fill=armor_color)
        draw.rectangle([cx-12*scale, cy-18*scale, cx+12*scale, cy+8*scale], fill=armor_color, outline=armor_dark)
        draw.rectangle([cx-10*scale, cy-6*scale, cx+10*scale, cy+6*scale], fill=cloth_color)
        draw.rectangle([cx-6*scale, cy+20*scale, cx+6*scale, cy+33*scale], fill=armor_color, outline=armor_dark)
        draw.rectangle([cx-6*scale, cy+33*scale, cx+6*scale, cy+36*scale], fill=boot_color)
        
        # Blue aura effect
        aura_color = (100, 150, 255, 100)
        draw.ellipse([cx-16*scale, cy-8*scale, cx+16*scale, cy+12*scale], fill=aura_color)
        
        if direction == 'right':
            draw.rectangle([cx+12*scale, cy-8*scale, cx+14*scale, cy+8*scale], fill=armor_color, outline=armor_dark)
            draw.rectangle([cx+14*scale, cy-12*scale, cx+24*scale, cy+4*scale], fill=sword_color, outline=sword_dark, width=1)
        else:
            draw.rectangle([cx-14*scale, cy-8*scale, cx-12*scale, cy+8*scale], fill=armor_color, outline=armor_dark)
            draw.rectangle([cx-24*scale, cy-12*scale, cx-14*scale, cy+4*scale], fill=sword_color, outline=sword_dark, width=1)
    
    elif attack_type == 'heavy':
        # Heavy attack - overhead swing
        if frame < 2:
            # Preparation
            draw.ellipse([cx-8*scale, cy-28*scale, cx+8*scale, cy-18*scale], fill=skin_color)
            draw.polygon([(cx-9*scale, cy-28*scale), (cx-10*scale, cy-22*scale), (cx+10*scale, cy-22*scale), (cx+9*scale, cy-28*scale)], fill=armor_color)
            draw.rectangle([cx-12*scale, cy-18*scale, cx+12*scale, cy+8*scale], fill=armor_color, outline=armor_dark)
            draw.rectangle([cx-10*scale, cy-6*scale, cx+10*scale, cy+6*scale], fill=cloth_color)
            draw.rectangle([cx-6*scale, cy+20*scale, cx+6*scale, cy+33*scale], fill=armor_color, outline=armor_dark)
            draw.rectangle([cx-6*scale, cy+33*scale, cx+6*scale, cy+36*scale], fill=boot_color)
            
            if direction == 'right':
                draw.rectangle([cx+12*scale, cy-8*scale, cx+14*scale, cy+6*scale], fill=armor_color, outline=armor_dark)
                draw.rectangle([cx+14*scale, cy-20*scale, cx+16*scale, cy+6*scale], fill=sword_color, outline=sword_dark, width=2)
            else:
                draw.rectangle([cx-14*scale, cy-8*scale, cx-12*scale, cy+6*scale], fill=armor_color, outline=armor_dark)
                draw.rectangle([cx-16*scale, cy-20*scale, cx-14*scale, cy+6*scale], fill=sword_color, outline=sword_dark, width=2)
        else:
            # Swing
            draw.ellipse([cx-8*scale, cy-28*scale, cx+8*scale, cy-18*scale], fill=skin_color)
            draw.polygon([(cx-9*scale, cy-28*scale), (cx-10*scale, cy-22*scale), (cx+10*scale, cy-22*scale), (cx+9*scale, cy-28*scale)], fill=armor_color)
            draw.rectangle([cx-12*scale, cy-18*scale, cx+12*scale, cy+8*scale], fill=armor_color, outline=armor_dark)
            draw.rectangle([cx-10*scale, cy-6*scale, cx+10*scale, cy+6*scale], fill=cloth_color)
            draw.rectangle([cx-6*scale, cy+20*scale, cx+6*scale, cy+33*scale], fill=armor_color, outline=armor_dark)
            draw.rectangle([cx-6*scale, cy+33*scale, cx+6*scale, cy+36*scale], fill=boot_color)
            
            # Orange impact color
            if direction == 'right':
                draw.rectangle([cx+8*scale, cy-4*scale, cx+10*scale, cy+10*scale], fill=armor_color, outline=armor_dark)
                draw.rectangle([cx+10*scale, cy-16*scale, cx+28*scale, cy+6*scale], fill=sword_color, outline=(255, 140, 0), width=2)
            else:
                draw.rectangle([cx-10*scale, cy-4*scale, cx-8*scale, cy+10*scale], fill=armor_color, outline=armor_dark)
                draw.rectangle([cx-28*scale, cy-16*scale, cx-10*scale, cy+6*scale], fill=sword_color, outline=(255, 140, 0), width=2)


# Generate all sprites at 40x50
os.makedirs('images', exist_ok=True)

# Base poses
for direction in ['left', 'right']:
    # Idle
    img = Image.new('RGBA', (40, 50), (0, 0, 0, 0))
    draw_knight(img, 0, 0, direction=direction, pose='idle')
    img.save(f'images/player_{direction}.png')
    print(f'Generated player_{direction}.png')
    
    # Jump
    img = Image.new('RGBA', (40, 50), (0, 0, 0, 0))
    draw_knight(img, 0, 0, direction=direction, pose='jump')
    img.save(f'images/player_jump_{direction}.png')
    print(f'Generated player_jump_{direction}.png')
    
    # Hit
    img = Image.new('RGBA', (40, 50), (0, 0, 0, 0))
    draw_knight(img, 0, 0, direction=direction, pose='hit')
    img.save(f'images/player_hit_{direction}.png')
    print(f'Generated player_hit_{direction}.png')
    
    # Normal attack frames
    for frame in range(3):
        img = Image.new('RGBA', (40, 50), (0, 0, 0, 0))
        draw_attack_frame(img, 0, 0, direction=direction, attack_type='normal', frame=frame)
        img.save(f'images/player_attack_normal_{direction}_{frame}.png')
        print(f'Generated player_attack_normal_{direction}_{frame}.png')
    
    # Critical attack frames
    for frame in range(3):
        img = Image.new('RGBA', (40, 50), (0, 0, 0, 0))
        draw_attack_frame(img, 0, 0, direction=direction, attack_type='critical', frame=frame)
        img.save(f'images/player_attack_critical_{direction}_{frame}.png')
        print(f'Generated player_attack_critical_{direction}_{frame}.png')
    
    # Heavy attack frames
    for frame in range(4):
        img = Image.new('RGBA', (40, 50), (0, 0, 0, 0))
        draw_attack_frame(img, 0, 0, direction=direction, attack_type='heavy', frame=frame)
        img.save(f'images/player_attack_heavy_{direction}_{frame}.png')
        print(f'Generated player_attack_heavy_{direction}_{frame}.png')

print('[OK] All knight sprites generated at 40x50 to match enemies')
