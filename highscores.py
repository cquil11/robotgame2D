"""Highscore management for the game."""
import json
from os import path
import os


def load_highscores(dir_path='.'):
    """Load highscores from file, return list of (name, score) tuples."""
    try:
        # Ensure directory exists
        if not path.exists(dir_path):
            dir_path = '.'
        highscores_path = path.join(dir_path, 'highscores.json')
        with open(highscores_path, 'r') as f:
            data = json.load(f)
            # Sort by score descending
            scores = sorted(data.get('scores', []), key=lambda x: x['score'], reverse=True)
            return scores[:5]  # Return top 5
    except Exception:
        return []


def save_highscores(scores, dir_path='.'):
    """Save highscores to both JSON and legacy highscore.txt file."""
    try:
        # Ensure directory exists
        if not path.exists(dir_path):
            dir_path = '.'
        
        # Save to highscores.json
        highscores_path = path.join(dir_path, 'highscores.json')
        with open(highscores_path, 'w', encoding='utf-8') as f:
            json.dump({'scores': scores}, f, indent=2)
        print(f"[OK] Saved {len(scores)} scores to highscores.json")
        
        # Also save the top score to highscore.txt for backward compatibility
        if scores and len(scores) > 0:
            hs_txt_path = path.join(dir_path, 'highscore.txt')
            with open(hs_txt_path, 'w', encoding='utf-8') as f:
                f.write(str(scores[0]['score']))  # Write only the top score
            print(f"[OK] Saved top score ({scores[0]['score']}) to highscore.txt")
    except Exception as e:
        print(f"[ERROR] Error saving highscores: {e}")


def is_highscore(score, dir_path='.'):
    """Check if score is in top 5."""
    scores = load_highscores(dir_path)
    if len(scores) < 5:
        return True
    return score > scores[-1]['score']


def add_highscore(name, score, dir_path='.'):
    """Add a new highscore and return updated list."""
    scores = load_highscores(dir_path)
    scores.append({'name': name, 'score': score})
    scores = sorted(scores, key=lambda x: x['score'], reverse=True)[:5]
    save_highscores(scores, dir_path)
    print(f"[OK] Added new highscore: {name} - {score}")
    return scores
