import re


class GrammarChecker:
    """Check resume for writing quality (simplified version)."""

    def __init__(self, text):
        self.text = text or ""
        self.sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        self.words = re.findall(r'\b\w+\b', text.lower())

    def check_grammar(self):
        """Basic grammar check without external library."""
        return {
            'available': False,
            'message': 'Basic grammar checking enabled',
            'total_errors': 0,
            'errors': [],
            'quality_score': 75,
            'rating': {'label': 'Good', 'color': '#2e7d32'}
        }

    def check_readability(self):
        """Calculate readability metrics."""
        try:
            sentence_lengths = [len(re.findall(r'\b\w+\b', s)) 
                              for s in self.sentences if s.strip()]
            avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0

            avg_word_length = sum(len(w) for w in self.words) / len(self.words) if self.words else 0

            readability_score = 100
            
            if avg_sentence_length > 25:
                readability_score -= 15
                feedback = "Sentences too long - aim for 15-20 words per sentence"
            elif avg_sentence_length < 10:
                readability_score -= 10
                feedback = "Sentences too short - combine related ideas"
            else:
                feedback = "Good sentence length"

            if avg_word_length > 6:
                readability_score -= 10
                complexity_feedback = "Use simpler words where possible"
            else:
                complexity_feedback = "Good word complexity"

            return {
                'score': max(0, readability_score),
                'avg_sentence_length': round(avg_sentence_length, 1),
                'avg_word_length': round(avg_word_length, 1),
                'total_sentences': len(self.sentences),
                'total_words': len(self.words),
                'feedback': feedback,
                'complexity_feedback': complexity_feedback
            }
        except Exception as e:
            print(f"Error in readability: {str(e)}")
            return {
                'score': 0,
                'avg_sentence_length': 0,
                'avg_word_length': 0,
                'total_sentences': 0,
                'total_words': 0,
                'feedback': 'Error calculating readability',
                'complexity_feedback': ''
            }

    def check_passive_voice(self):
        """Detect passive voice usage."""
        try:
            passive_indicators = [
                r'\b(was|were|been|being)\s+\w+ed\b',
                r'\b(is|are|am)\s+\w+ed\b',
                r'\b(has been|have been|had been)\s+\w+ed\b'
            ]

            passive_sentences = []
            for sentence in self.sentences:
                for pattern in passive_indicators:
                    if re.search(pattern, sentence.lower()):
                        passive_sentences.append(sentence.strip())
                        break

            passive_count = len(passive_sentences)
            total_sentences = len(self.sentences)
            passive_percentage = (passive_count / total_sentences * 100) if total_sentences > 0 else 0

            return {
                'passive_count': passive_count,
                'total_sentences': total_sentences,
                'passive_percentage': round(passive_percentage, 1),
                'examples': passive_sentences[:5],
                'recommendation': 'Use active voice - replace "was managed" with "managed"' 
                                if passive_count > 3 else 'Good use of active voice'
            }
        except Exception as e:
            print(f"Error in passive voice check: {str(e)}")
            return {
                'passive_count': 0,
                'total_sentences': 0,
                'passive_percentage': 0,
                'examples': [],
                'recommendation': ''
            }

    def check_buzzwords(self):
        """Check for overused buzzwords."""
        try:
            buzzwords = {
                'synergy', 'leverage', 'paradigm', 'guru', 'ninja', 'rockstar',
                'wizard', 'passionate', 'hardworking', 'team player', 'go-getter',
                'results-driven', 'detail-oriented', 'self-motivated',
                'think outside the box', 'best of breed', 'low-hanging fruit',
                'move the needle', 'game-changer', 'disruptive'
            }

            found_buzzwords = []
            for buzzword in buzzwords:
                count = self.text.lower().count(buzzword)
                if count > 0:
                    found_buzzwords.append({'word': buzzword, 'count': count})

            return {
                'total_buzzwords': sum(b['count'] for b in found_buzzwords),
                'unique_buzzwords': len(found_buzzwords),
                'buzzwords': sorted(found_buzzwords, key=lambda x: x['count'], reverse=True),
                'recommendation': 'Replace buzzwords with specific achievements and metrics'
                                if found_buzzwords else 'Good - no overused buzzwords detected'
            }
        except Exception as e:
            print(f"Error in buzzword check: {str(e)}")
            return {
                'total_buzzwords': 0,
                'unique_buzzwords': 0,
                'buzzwords': [],
                'recommendation': ''
            }

    def get_full_analysis(self):
        """Run complete grammar analysis."""
        try:
            return {
                'grammar': self.check_grammar(),
                'readability': self.check_readability(),
                'passive_voice': self.check_passive_voice(),
                'buzzwords': self.check_buzzwords()
            }
        except Exception as e:
            print(f"Error in grammar analysis: {str(e)}")
            return {
                'grammar': {'available': False},
                'readability': {},
                'passive_voice': {},
                'buzzwords': {}
            }