"""Highscore management functions."""
import json
from os import path


def load_highscores(scores_dir='.'):
    """Load highscores from JSON file."""
    try:
        scores_path = path.join(scores_dir, 'highscores.json')
        with open(scores_path, 'r') as f:
            data = json.load(f)
            return data.get('scores', [])
    except Exception:
        return []


def add_highscore(name, score, scores_dir='.'):
    """Add a new highscore and save to JSON file."""
    scores = load_highscores(scores_dir)
    scores.append({'name': name, 'score': score})
    scores.sort(key=lambda x: x.get('score', 0), reverse=True)
    scores = scores[:10]  # Keep only top 10
    
    try:
        scores_path = path.join(scores_dir, 'highscores.json')
        with open(scores_path, 'w') as f:
            json.dump({'scores': scores}, f, indent=2)
    except Exception:
        pass


def is_highscore(score, scores_dir='.'):
    """Check if a score qualifies as a highscore (top 10)."""
    scores = load_highscores(scores_dir)
    if len(scores) < 10:
        return True
    return score > min(s.get('score', 0) for s in scores)
