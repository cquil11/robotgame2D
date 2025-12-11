# Crimson Knight

A medieval 2D action platformer built with Pygame featuring dynamic combat, progressive difficulty, and an upgrade system.

## Features

- **Dynamic Combat System**: Multiple attack types (normal, heavy, critical) with combo mechanics
- **Progressive Difficulty**: Enemy stats and AI improve with each level
- **Upgrade System**: Choose from random upgrades after each level
- **Multiple Enemy Types**: Goblins, Skeletons, and Boss Monsters
- **Power-ups**: Shield, damage boost, speed boost, freeze enemies
- **Level System**: 10 unique platform layouts with boss levels every 5 levels
- **Save/Load System**: Save your progress and continue later
- **Highscore Tracking**: Top 10 scores saved locally

## Controls

- **Arrow Keys / WASD**: Move left/right
- **Space / W**: Jump
- **Left Click**: Sword Attack (hold to charge heavy attack)
- **Right Click**: Activate Shield (blocks projectiles, 3s duration, 6s cooldown)
- **R / E**: Cast Fireball (costs mana)
- **ESC**: Pause game
- **Q**: Quit to menu (from pause)

## Requirements

- Python 3.7+
- Pygame

## Installation

```bash
# Clone the repository
git clone https://github.com/cquil11/robotgame2D.git
cd robotgame2D  # Note: Folder name unchanged for compatibility

# Install dependencies
pip install pygame

# Run the game
python Main.py
```

## Project Structure

```
robotgame2D/
├── Main.py           # Main game loop and logic
├── sprites.py        # All sprite classes (Player, enemies, items)
├── settings.py       # Game configuration and constants
├── screens.py        # Menu and screen rendering
├── ui_dialogs.py     # UI dialog boxes
├── upgrades.py       # Upgrade system
├── game_utils.py     # Utility functions
├── highscores.py     # Highscore management
├── images/           # Game sprites and graphics
├── sounds/           # Sound effects and music
├── highscore.txt     # Single highscore (legacy)
└── highscores.json   # Top 10 highscores
```

## Gameplay

- Defeat all enemies on each level to progress
- Collect coins for points
- Collect hearts to restore health
- Complete levels quickly for time bonuses
- Perfect clear (no damage) awards bonus points
- Every 5th level is a boss battle
- Choose upgrades between levels to enhance your character

## License

MIT License - See repository for details
