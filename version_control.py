import json
import os
from datetime import datetime


class ResumeVersionControl:
    """Track resume analysis history and improvements."""

    def __init__(self, user_id='default'):
        self.user_id = user_id
        self.history_dir = 'history'
        self.history_file = os.path.join(self.history_dir, f'{user_id}.json')
        os.makedirs(self.history_dir, exist_ok=True)

    def save_version(self, score_data, analysis, filename):
        """Save a new version to history."""
        version = {
            'timestamp': datetime.now().isoformat(),
            'filename': filename,
            'score': score_data['total_score'],
            'grade': score_data['grade']['letter'],
            'category_scores': score_data['category_scores'],
            'skill_count': analysis['skills']['total_count'],
            'technical_skills': len(analysis['skills']['technical']),
            'soft_skills': len(analysis['skills']['soft']),
            'action_verbs': len(analysis['action_verbs']),
            'achievements': analysis['quantified_achievements']['count']
        }

        history = self.load_history()
        history.append(version)

        # Keep only last 20 versions
        if len(history) > 20:
            history = history[-20:]

        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)

        return len(history)

    def load_history(self):
        """Load version history."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def get_latest_version(self):
        """Get the most recent version."""
        history = self.load_history()
        return history[-1] if history else None

    def get_progress_data(self):
        """Get data for progress visualization."""
        history = self.load_history()
        
        if not history:
            return None

        return {
            'dates': [v['timestamp'][:10] for v in history],
            'scores': [v['score'] for v in history],
            'skill_counts': [v['skill_count'] for v in history],
            'versions_count': len(history),
            'first_score': history[0]['score'],
            'latest_score': history[-1]['score'],
            'improvement': round(history[-1]['score'] - history[0]['score'], 1),
            'average_score': round(sum(v['score'] for v in history) / len(history), 1)
        }

    def get_comparison(self, version_index=-1):
        """Compare a specific version with the latest."""
        history = self.load_history()
        
        if len(history) < 2:
            return None

        latest = history[-1]
        compared = history[version_index]

        return {
            'latest': latest,
            'compared': compared,
            'score_diff': latest['score'] - compared['score'],
            'skill_diff': latest['skill_count'] - compared['skill_count'],
            'improvements': self._find_improvements(compared, latest)
        }

    def _find_improvements(self, old, new):
        """Find what improved between versions."""
        improvements = []
        declines = []

        for category in old['category_scores']:
            old_score = old['category_scores'][category]
            new_score = new['category_scores'][category]
            diff = new_score - old_score

            if diff > 5:
                improvements.append(f"{category}: +{diff:.1f}%")
            elif diff < -5:
                declines.append(f"{category}: {diff:.1f}%")

        return {
            'improvements': improvements,
            'declines': declines,
            'overall_change': new['score'] - old['score']
        }

    def clear_history(self):
        """Clear all history for this user."""
        if os.path.exists(self.history_file):
            os.remove(self.history_file)