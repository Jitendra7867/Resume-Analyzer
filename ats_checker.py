import re
from collections import Counter


class ATSChecker:
    """Check resume compatibility with Applicant Tracking Systems."""

    def __init__(self, text):
        self.text = text
        self.text_lower = text.lower()
        self.lines = [l.strip() for l in text.split('\n') if l.strip()]
        self.word_count = len(re.findall(r'\b\w+\b', text))

    def calculate_ats_score(self):
        """Calculate ATS compatibility score (0-100)."""
        score = 100
        issues = []
        recommendations = []

        # 1. Check for complex formatting (tables, columns)
        if self._has_tables():
            score -= 15
            issues.append("❌ Tables or complex layouts detected")
            recommendations.append("Use simple, linear format without tables")

        # 2. Check for special characters
        special_chars = len(re.findall(r'[★☆●○■□▪▫◆◇♦►▶]', self.text))
        if special_chars > 5:
            score -= 10
            issues.append(f"❌ Too many special characters ({special_chars} found)")
            recommendations.append("Replace special bullets with standard dashes or asterisks")

        # 3. Check for images/graphics indicators
        if re.search(r'\[image\]|\[graphic\]|\[photo\]|\.jpg|\.png|\.gif', self.text_lower):
            score -= 20
            issues.append("❌ Images or graphics detected")
            recommendations.append("Remove all images - ATS cannot read visual content")

        # 4. Check document structure
        if len(self.lines) < 15:
            score -= 15
            issues.append("❌ Poor document structure - too few line breaks")
            recommendations.append("Use clear section breaks and bullet points")

        # 5. Check for standard section headers
        required_sections = {
            'experience': ['experience', 'work experience', 'employment', 'professional experience'],
            'education': ['education', 'academic background', 'qualifications'],
            'skills': ['skills', 'technical skills', 'core competencies', 'expertise']
        }

        missing_sections = []
        for section, keywords in required_sections.items():
            found = any(kw in self.text_lower for kw in keywords)
            if not found:
                missing_sections.append(section)

        if missing_sections:
            score -= 10 * len(missing_sections)
            issues.append(f"❌ Missing standard sections: {', '.join(missing_sections)}")
            recommendations.append(f"Add {', '.join(missing_sections)} sections with clear headings")

        # 6. Check word count (ideal: 400-800 words)
        if self.word_count < 300:
            score -= 15
            issues.append(f"❌ Resume too short ({self.word_count} words)")
            recommendations.append("Add more detail - aim for 400-800 words")
        elif self.word_count > 1000:
            score -= 10
            issues.append(f"⚠️ Resume too long ({self.word_count} words)")
            recommendations.append("Condense to 1-2 pages (400-800 words)")

        # 7. Check for contact information
        has_email = bool(re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', self.text))
        has_phone = bool(re.search(r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\./0-9]{7,15}', self.text))

        if not has_email:
            score -= 10
            issues.append("❌ No email address found")
            recommendations.append("Add email address at the top of resume")

        if not has_phone:
            score -= 5
            issues.append("⚠️ No phone number found")
            recommendations.append("Add phone number for contact")

        # 8. Check for headers/footers (problematic for ATS)
        if re.search(r'page \d+ of \d+|confidential|curriculum vitae', self.text_lower):
            score -= 10
            issues.append("⚠️ Headers/footers may cause parsing issues")
            recommendations.append("Remove headers and footers - place all info in main body")

        # 9. Check file name best practices (can't check from text, but recommend)
        recommendations.append("Save file as 'FirstName_LastName_Resume.pdf' or .docx")
        recommendations.append("Use standard fonts: Arial, Calibri, or Times New Roman (10-12pt)")

        # 10. Check for acronyms without definitions
        acronyms = re.findall(r'\b[A-Z]{2,}\b', self.text)
        if len(acronyms) > 10:
            issues.append(f"⚠️ Many acronyms found ({len(acronyms)})")
            recommendations.append("Spell out acronyms on first use: 'Search Engine Optimization (SEO)'")

        # Calculate final score
        final_score = max(0, min(100, score))

        # Determine rating
        if final_score >= 85:
            rating = "Excellent"
            color = "#00c853"
        elif final_score >= 70:
            rating = "Good"
            color = "#2e7d32"
        elif final_score >= 55:
            rating = "Fair"
            color = "#f9a825"
        else:
            rating = "Needs Improvement"
            color = "#c62828"

        return {
            'score': round(final_score, 1),
            'rating': rating,
            'color': color,
            'issues': issues,
            'recommendations': recommendations,
            'checks': {
                'no_complex_formatting': not self._has_tables(),
                'minimal_special_chars': special_chars <= 5,
                'no_images': not re.search(r'\[image\]|\.jpg|\.png', self.text_lower),
                'good_structure': len(self.lines) >= 15,
                'standard_sections': len(missing_sections) == 0,
                'optimal_length': 300 <= self.word_count <= 1000,
                'has_contact_info': has_email and has_phone,
            }
        }

    def _has_tables(self):
        """Detect if text likely contains tables."""
        # Check for table-like patterns
        table_indicators = [
            r'┌|┬|┐|├|┼|┤|└|┴|┘',  # Box drawing characters
            r'\|.*\|.*\|',  # Pipe-separated columns
            r'\t.*\t.*\t',  # Multiple tabs
        ]
        return any(re.search(pattern, self.text) for pattern in table_indicators)

    def get_keyword_density(self):
        """Calculate keyword frequency for ATS optimization."""
        words = re.findall(r'\b[a-z]{3,}\b', self.text_lower)
        
        # Remove common stop words
        stop_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all',
            'can', 'has', 'her', 'was', 'one', 'our', 'out', 'with',
            'will', 'have', 'from', 'this', 'that', 'they', 'been'
        }
        
        filtered_words = [w for w in words if w not in stop_words]
        word_freq = Counter(filtered_words)
        
        # Get top 20 keywords
        top_keywords = word_freq.most_common(20)
        
        return {
            'total_words': len(words),
            'unique_words': len(set(filtered_words)),
            'top_keywords': [
                {'word': word, 'count': count, 
                 'density': round((count / len(words)) * 100, 2)}
                for word, count in top_keywords
            ]
        }

    def check_file_format_tips(self):
        """Provide file format recommendations."""
        return {
            'recommended_formats': ['.docx', '.pdf'],
            'avoid_formats': ['.jpg', '.png', '.pages', '.txt'],
            'tips': [
                "PDF: Best for preserving formatting, widely accepted",
                "DOCX: Best for ATS parsing, easier to extract text",
                "Avoid: Scanned PDFs, images, or unconventional formats",
                "File size: Keep under 2MB for email compatibility"
            ]
        }