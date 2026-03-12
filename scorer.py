class ResumeScorer:
    """Calculate resume scores based on analysis."""

    WEIGHTS = {
        'skills': 25,
        'sections': 20,
        'action_verbs': 15,
        'achievements': 15,
        'formatting': 15,
        'job_match': 10,
    }

    @staticmethod
    def calculate_score(analysis):
        """Calculate overall resume score (0-100)."""
        try:
            scores = {}

            # ─── Skills Score (25%) ───
            skill_count = analysis.get('skills', {}).get('total_count', 0)
            if skill_count >= 15:
                scores['skills'] = 100
            elif skill_count >= 10:
                scores['skills'] = 85
            elif skill_count >= 5:
                scores['skills'] = 65
            elif skill_count >= 3:
                scores['skills'] = 45
            else:
                scores['skills'] = 20

            # ─── Sections Score (20%) ───
            sections = analysis.get('sections', {})
            essential = ['experience', 'education', 'skills']
            bonus = ['summary', 'projects', 'achievements']

            essential_found = sum(1 for s in essential if sections.get(s, False))
            bonus_found = sum(1 for s in bonus if sections.get(s, False))

            section_score = 0
            if essential:
                section_score = (essential_found / len(essential)) * 70
            if bonus:
                section_score += (bonus_found / len(bonus)) * 30
            scores['sections'] = min(section_score, 100)

            # ─── Action Verbs Score (15%) ───
            verb_count = len(analysis.get('action_verbs', []))
            if verb_count >= 10:
                scores['action_verbs'] = 100
            elif verb_count >= 7:
                scores['action_verbs'] = 80
            elif verb_count >= 4:
                scores['action_verbs'] = 60
            elif verb_count >= 2:
                scores['action_verbs'] = 40
            else:
                scores['action_verbs'] = 15

            # ─── Achievements Score (15%) ───
            achievement_count = analysis.get('quantified_achievements', {}).get('count', 0)
            if achievement_count >= 5:
                scores['achievements'] = 100
            elif achievement_count >= 3:
                scores['achievements'] = 75
            elif achievement_count >= 1:
                scores['achievements'] = 50
            else:
                scores['achievements'] = 10

            # ─── Formatting Score (15%) ───
            issue_count = len(analysis.get('formatting', {}).get('issues', []))
            word_count = analysis.get('formatting', {}).get('word_count', 0)

            format_score = 100
            format_score -= issue_count * 15
            if word_count < 100:
                format_score -= 30
            elif word_count < 200:
                format_score -= 15
            scores['formatting'] = max(format_score, 0)

            # ─── Job Match Score (10%) ───
            job_match = analysis.get('job_match')
            if job_match:
                scores['job_match'] = (job_match.get('overall_match', 0) * 0.4 +
                                      job_match.get('skill_match', 0) * 0.6)
            else:
                scores['job_match'] = 50

            # ─── Calculate Weighted Total ───
            total = 0
            for category, score in scores.items():
                weight = ResumeScorer.WEIGHTS.get(category, 0)
                total += (score * weight) / 100

            grade = ResumeScorer._get_grade(total)

            return {
                'total_score': round(total, 1),
                'category_scores': {k: round(v, 1) for k, v in scores.items()},
                'grade': grade,
                'max_score': 100,
            }
        except Exception as e:
            print(f"Error in scoring: {str(e)}")
            return {
                'total_score': 0,
                'category_scores': {},
                'grade': {'letter': 'F', 'label': 'Error', 'color': '#c62828'},
                'max_score': 100,
            }

    @staticmethod
    def _get_grade(score):
        if score >= 90:
            return {'letter': 'A+', 'label': 'Excellent', 'color': '#00c853'}
        elif score >= 80:
            return {'letter': 'A', 'label': 'Very Good', 'color': '#2e7d32'}
        elif score >= 70:
            return {'letter': 'B+', 'label': 'Good', 'color': '#558b2f'}
        elif score >= 60:
            return {'letter': 'B', 'label': 'Above Average', 'color': '#f9a825'}
        elif score >= 50:
            return {'letter': 'C', 'label': 'Average', 'color': '#ff8f00'}
        elif score >= 40:
            return {'letter': 'D', 'label': 'Below Average', 'color': '#e65100'}
        else:
            return {'letter': 'F', 'label': 'Needs Improvement', 'color': '#c62828'}

    @staticmethod
    def generate_recommendations(analysis, score_data):
        """Generate actionable recommendations."""
        try:
            recommendations = []
            scores = score_data.get('category_scores', {})

            if scores.get('skills', 0) < 60:
                recommendations.append({
                    'category': '🔧 Skills',
                    'priority': 'HIGH',
                    'message': 'Add more relevant technical skills to your resume.',
                    'tips': [
                        'List specific programming languages and frameworks',
                        'Include tools and platforms you\'ve used',
                        'Add certifications if you have any',
                    ]
                })

            if scores.get('sections', 0) < 70:
                missing = [s for s, found in analysis.get('sections', {}).items() if not found]
                if missing:
                    recommendations.append({
                        'category': '📋 Sections',
                        'priority': 'HIGH',
                        'message': f'Missing sections: {", ".join(missing[:3])}',
                        'tips': [
                            'Add a Professional Summary at the top',
                            'Include a dedicated Skills section',
                            'Add relevant Projects section',
                        ]
                    })

            if scores.get('action_verbs', 0) < 60:
                recommendations.append({
                    'category': '💪 Action Verbs',
                    'priority': 'MEDIUM',
                    'message': 'Use more strong action verbs to describe achievements.',
                    'tips': [
                        'Start bullet points with verbs like: Developed, Implemented, Led',
                        'Avoid passive language',
                        'Be specific about your contributions',
                    ]
                })

            if scores.get('achievements', 0) < 50:
                recommendations.append({
                    'category': '📊 Quantified Results',
                    'priority': 'HIGH',
                    'message': 'Add measurable achievements with numbers.',
                    'tips': [
                        'Include percentages: "Improved performance by 40%"',
                        'Add scale: "Managed team of 8 developers"',
                        'Show impact: "Reduced load time from 5s to 1.2s"',
                    ]
                })

            if scores.get('formatting', 0) < 70:
                issues = analysis.get('formatting', {}).get('issues', [])
                suggestions = analysis.get('formatting', {}).get('suggestions', [])
                if issues:
                    recommendations.append({
                        'category': '📝 Formatting',
                        'priority': 'MEDIUM',
                        'message': issues[0] if issues else 'Formatting needs improvement',
                        'tips': suggestions[:3] if suggestions else []
                    })

            priority_map = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
            recommendations.sort(key=lambda x: priority_map.get(x.get('priority', 'LOW'), 2))

            return recommendations
        except Exception as e:
            print(f"Error generating recommendations: {str(e)}")
            return []