# Enhanced Attack System

## Overview
The attack system has been significantly enhanced with dynamic attack types, energy management, and charge mechanics that reward skilled play.

## Attack Types

### 1. Normal Attack
- **Trigger**: Standard sword swing
- **Damage**: Base damage + combo bonus
- **Range**: 30-50 pixels depending on combo
- **Recovery**: 10 frames
- **Multiplier**: 1.0x

### 2. Heavy Attack
- **Trigger**: Charging for 20+ frames while not attacking
- **Damage**: 2.0x base damage (includes energy and combo bonuses)
- **Range**: 45-65 pixels (15 pixels larger than normal)
- **Height**: 25-35 pixels (8 pixels taller)
- **Recovery**: 16 frames (longer recovery)
- **Score Bonus**: 1.5x multiplier
- **Visual**: Red attack indicator text

### 3. Critical Attack
- **Trigger**: Landing 4+ consecutive hits within 1.5 seconds
- **Damage**: 1.5x base damage (includes energy and combo bonuses)
- **Range**: 30-50 pixels (same as normal)
- **Height**: 35-45 pixels (10 pixels taller - reaches more targets)
- **Recovery**: 14 frames
- **Score Bonus**: 2.0x multiplier (2.5x on boss fights)
- **Visual**: Gold/yellow attack indicator text

## Attack Energy System

### Energy Mechanics
- **Max Energy**: 100 points
- **Regen Rate**: 3 points per frame when not attacking
- **Hit Bonus**: +20 energy on successful hit (capped at max)
- **Drain**: Full drain on attack (energy bonus applied to damage)

### Energy Damage Bonus
- Energy provides up to 50% damage bonus at full capacity
- Formula: `final_damage = (base + combo_bonus) × type_multiplier × (1.0 + energy_bonus)`
- Energy is fully drained after each attack to prevent stacking

### Energy Bar Display
- Located at bottom-left of screen
- Cyan color bar showing current energy level
- Updates in real-time as player attacks and regenerates

## Combo System

### Combo Mechanics
- Extends combo duration to 1 second (up from original)
- Consecutive hits increase combo multiplier
- Max combo level: 5 hits
- Consecutive hit tracking: Up to 10 hits (triggers critical at 4+)

### Combo Bonuses
- **Damage**: +0.5 per combo level (multiplicative)
- **Score**: +20% multiplier per combo level
- **Range**: +5 pixels per combo level
- **Height**: +3 pixels per combo level

## Scoring System

### Score Calculation
Base score × Elite multiplier × Combo multiplier × Attack Type multiplier × Streak multiplier

### Attack Type Multipliers
- **Normal**: 1.0x
- **Heavy**: 1.5x (1.5x on bosses)
- **Critical**: 2.0x (2.5x on bosses)

### Example Scores
- Basic goblin hit: 50 points × 1.0 (normal)
- Elite goblin heavy hit with 3x combo: 50 × 3.0 × 1.6 × 1.5 = 360 points
- Critical hit on skeleton with 5x combo and 5x streak: 75 × 1.0 × 2.0 × 2.0 × 1.5 = 450 points

## UI Indicators

### Attack Type Display
- Shows current attack type when attacking
- Text appears at top-center of screen
- Colors: White (normal), Red (heavy), Gold (critical)

### Attack Energy Bar
- Located at bottom-left
- Cyan progress bar
- Label: "ATTACK ENERGY"
- Real-time updates

### Combo Indicator
- Appears when combo > 1 and player attacking
- Shows combo count: "Nx COMBO!"
- Yellow/gold colored text

## Strategy Tips

1. **Build Energy**: Let energy regenerate during calm moments before tough fights
2. **Heavy Attack Timing**: Use heavy attacks on elite enemies or bosses when at full energy
3. **Critical Chains**: Land quick consecutive hits to trigger critical attacks for maximum damage
4. **Energy Efficiency**: Each hit grants +20 energy, so continuous combat keeps energy flowing
5. **Streak Maintenance**: Keep kills flowing for streak bonuses that stack with attack type multipliers

## Technical Details

### New Player Attributes
- `attack_energy`: Current energy (0-100)
- `max_attack_energy`: Maximum energy capacity (100)
- `attack_energy_regen`: Energy regen per frame (3.0)
- `attack_type`: Current attack type ('normal', 'heavy', 'critical')
- `charge_timer`: Frames spent charging for heavy attack
- `consecutive_hits`: Count of hits in current sequence (0-10)

### Modified Methods
- `hit()`: Now determines attack type based on charge and consecutive hits
- `increment_combo()`: Now tracks consecutive hits and regenerates energy
- `get_attack_damage()`: Uses energy and attack type for damage calculation
- `get_attack_rect()`: Adjusts hitbox based on attack type
- `update()`: Handles energy regen, charge reset, and consecutive hit timeout

## Highscore System

### Top 5 Scores
The game saves and displays the top 5 highscores with player names:
- Scores saved to `highscores.json`
- Automatically sorted by score
- Only top 5 retained
- Player prompted for name entry on new highscore
- Scores visible from main menu "High Scores" option
