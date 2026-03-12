import re
from collections import Counter


class ResumeAnalyzer:
    """Analyze resume content for skills, keywords, and quality."""

    # ─── Skill Databases ───
    TECHNICAL_SKILLS = {
        # Programming Languages
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'c',
        'ruby', 'php', 'swift', 'kotlin', 'go', 'rust', 'scala', 'r',
        'matlab', 'perl', 'dart', 'lua', 'shell', 'bash', 'powershell',

        # Web Development
        'html', 'css', 'sass', 'less', 'react', 'reactjs', 'angular',
        'vue', 'vuejs', 'nextjs', 'nuxtjs', 'svelte', 'jquery',
        'bootstrap', 'tailwind', 'webpack', 'vite', 'nodejs', 'express',
        'django', 'flask', 'fastapi', 'spring', 'springboot', 'laravel',
        'asp.net', 'ruby on rails', 'graphql', 'rest', 'restful',

        # Databases
        'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'cassandra',
        'oracle', 'sqlite', 'dynamodb', 'firebase', 'elasticsearch',
        'neo4j', 'couchdb', 'mariadb',

        # Cloud & DevOps
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins',
        'terraform', 'ansible', 'ci/cd', 'github actions', 'gitlab',
        'circleci', 'nginx', 'apache', 'linux', 'unix',

        # Data Science & ML
        'machine learning', 'deep learning', 'tensorflow', 'pytorch',
        'keras', 'scikit-learn', 'pandas', 'numpy', 'matplotlib',
        'seaborn', 'nlp', 'computer vision', 'opencv', 'spark',
        'hadoop', 'tableau', 'power bi', 'data analysis',
        'data visualization', 'statistics', 'ai', 'artificial intelligence',

        # Mobile
        'android', 'ios', 'react native', 'flutter', 'xamarin',
        'swiftui',

        # Tools & Others
        'git', 'github', 'bitbucket', 'jira', 'confluence', 'slack',
        'figma', 'photoshop', 'illustrator', 'xd', 'sketch',
        'agile', 'scrum', 'kanban', 'api', 'microservices',
        'blockchain', 'cybersecurity', 'iot',
    }

    SOFT_SKILLS = {
        'leadership', 'communication', 'teamwork', 'problem solving',
        'problem-solving', 'critical thinking', 'time management',
        'adaptability', 'creativity', 'collaboration', 'mentoring',
        'project management', 'decision making', 'analytical',
        'presentation', 'negotiation', 'conflict resolution',
        'strategic thinking', 'detail oriented', 'detail-oriented',
        'self motivated', 'self-motivated', 'multitasking',
        'organizational', 'interpersonal', 'work ethic',
    }

    ACTION_VERBS = {
        'developed', 'implemented', 'designed', 'managed', 'led',
        'created', 'built', 'optimized', 'improved', 'increased',
        'decreased', 'reduced', 'achieved', 'delivered', 'launched',
        'automated', 'streamlined', 'analyzed', 'coordinated',
        'established', 'executed', 'generated', 'initiated',
        'maintained', 'mentored', 'orchestrated', 'pioneered',
        'resolved', 'spearheaded', 'transformed', 'engineered',
        'architected', 'collaborated', 'contributed', 'drove',
        'facilitated', 'integrated', 'migrated', 'refactored',
    }

    # ─── Section Keywords ───
    SECTION_HEADERS = {
        'experience': ['experience', 'work experience', 'employment',
                       'professional experience', 'work history'],
        'education': ['education', 'academic', 'qualification',
                      'certifications', 'academic background'],
        'skills': ['skills', 'technical skills', 'competencies',
                   'technologies', 'tools', 'expertise'],
        'projects': ['projects', 'personal projects', 'academic projects',
                     'portfolio'],
        'summary': ['summary', 'objective', 'profile', 'about',
                    'professional summary', 'career objective'],
        'achievements': ['achievements', 'awards', 'honors',
                         'accomplishments', 'recognition'],
    }

    def __init__(self, text):
        self.text = text or ""
        self.text_lower = self.text.lower()
        self.words = re.findall(r'\b\w+\b', self.text_lower)
        self.word_count = len(self.words)
        self.lines = [l.strip() for l in self.text.split('\n') if l.strip()]

    def find_skills(self):
        """Find technical and soft skills in resume."""
        found_technical = set()
        found_soft = set()

        for skill in self.TECHNICAL_SKILLS:
            pattern = r'\b' + re.escape(skill.replace(' ', r'\s+')) + r'\b'
            if re.search(pattern, self.text_lower):
                found_technical.add(skill.title())

        for skill in self.SOFT_SKILLS:
            pattern = r'\b' + re.escape(skill.replace(' ', r'\s+')) + r'\b'
            if re.search(pattern, self.text_lower):
                found_soft.add(skill.title())

        return {
            'technical': sorted(list(found_technical)),
            'soft': sorted(list(found_soft)),
            'total_count': len(found_technical) + len(found_soft)
        }

    def find_action_verbs(self):
        """Find strong action verbs used."""
        found = set()
        for verb in self.ACTION_VERBS:
            if re.search(r'\b' + re.escape(verb) + r'\b', self.text_lower):
                found.add(verb.title())
        return sorted(list(found))

    def check_sections(self):
        """Check which standard resume sections are present."""
        found_sections = {}
        for section, keywords in self.SECTION_HEADERS.items():
            found = False
            for keyword in keywords:
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, self.text_lower):
                    found = True
                    break
            found_sections[section] = found
        return found_sections

    def check_quantified_achievements(self):
        """Check for metrics and quantified results."""
        patterns = [
            r'\d+\s*%',
            r'\$\s*[\d,]+',
            r'[\d,]+\s*users?',
            r'[\d,]+\s*customers?',
            r'[\d,]+\s*clients?',
            r'increased\s.*\d+',
            r'decreased\s.*\d+',
            r'reduced\s.*\d+',
            r'improved\s.*\d+',
            r'saved\s.*\d+',
            r'\d+x\b',
        ]
        matches = []
        for pattern in patterns:
            found = re.findall(pattern, self.text_lower)
            matches.extend(found)
        return {
            'count': len(matches),
            'examples': matches[:10]
        }

    def analyze_formatting(self):
        """Analyze resume formatting quality."""
        issues = []
        suggestions = []

        if self.word_count < 150:
            issues.append("Resume is too short (< 150 words)")
            suggestions.append("Add more detail about your experience and skills")
        elif self.word_count > 1500:
            issues.append("Resume might be too long (> 1500 words)")
            suggestions.append("Consider condensing to 1-2 pages")

        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        if not re.search(email_pattern, self.text):
            issues.append("No email address found")
            suggestions.append("Add your email address")

        phone_pattern = r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\./0-9]{7,15}'
        if not re.search(phone_pattern, self.text):
            issues.append("No phone number found")
            suggestions.append("Add your phone number")

        buzzwords = ['synergy', 'guru', 'ninja', 'rockstar', 'wizard',
                     'passionate', 'hardworking', 'results-driven',
                     'team player', 'go-getter', 'think outside the box']
        found_buzzwords = []
        for bw in buzzwords:
            if bw in self.text_lower:
                found_buzzwords.append(bw)
        if found_buzzwords:
            issues.append(f"Overused buzzwords found: {', '.join(found_buzzwords[:3])}")
            suggestions.append("Replace buzzwords with specific achievements")

        first_person = ['i ', ' i ', 'my ', 'me ', 'myself']
        fp_count = sum(self.text_lower.count(fp) for fp in first_person)
        if fp_count > 5:
            issues.append(f"Too many first-person pronouns ({fp_count})")
            suggestions.append("Remove 'I', 'my', 'me' - use action verbs instead")

        return {
            'issues': issues,
            'suggestions': suggestions,
            'word_count': self.word_count,
            'line_count': len(self.lines)
        }

    def match_job_description(self, job_description):
        """Match resume against a job description."""
        if not job_description or not job_description.strip():
            return None

        jd_lower = job_description.lower()
        jd_words = set(re.findall(r'\b\w{3,}\b', jd_lower))

        stop_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all',
            'can', 'has', 'her', 'was', 'one', 'our', 'out', 'with',
            'will', 'have', 'from', 'this', 'that', 'they', 'been',
            'said', 'each', 'which', 'their', 'about', 'would',
            'make', 'like', 'into', 'could', 'time', 'very', 'when',
            'come', 'than', 'look', 'only', 'also', 'back', 'after',
            'work', 'year', 'some', 'them', 'know', 'should', 'able',
            'including', 'experience', 'working', 'using', 'strong',
            'must', 'such', 'well', 'within', 'role', 'join',
        }

        jd_keywords = jd_words - stop_words
        resume_words = set(re.findall(r'\b\w{3,}\b', self.text_lower))

        matched = jd_keywords & resume_words
        missing = jd_keywords - resume_words

        jd_skills = set()
        for skill in self.TECHNICAL_SKILLS:
            pattern = r'\b' + re.escape(skill.replace(' ', r'\s+')) + r'\b'
            if re.search(pattern, jd_lower):
                jd_skills.add(skill)

        resume_skills = set()
        for skill in self.TECHNICAL_SKILLS:
            pattern = r'\b' + re.escape(skill.replace(' ', r'\s+')) + r'\b'
            if re.search(pattern, self.text_lower):
                resume_skills.add(skill)

        matched_skills = jd_skills & resume_skills
        missing_skills = jd_skills - resume_skills

        match_percentage = 0
        if jd_keywords:
            match_percentage = round((len(matched) / len(jd_keywords)) * 100, 1)

        skill_match_pct = 0
        if jd_skills:
            skill_match_pct = round((len(matched_skills) / len(jd_skills)) * 100, 1)

        return {
            'overall_match': match_percentage,
            'skill_match': skill_match_pct,
            'matched_keywords': sorted(list(matched))[:30],
            'missing_keywords': sorted(list(missing))[:20],
            'matched_skills': sorted([s.title() for s in matched_skills]),
            'missing_skills': sorted([s.title() for s in missing_skills]),
            'jd_skill_count': len(jd_skills),
            'matched_skill_count': len(matched_skills),
        }

    def get_full_analysis(self, job_description=None):
        """Run complete resume analysis."""
        try:
            skills = self.find_skills()
            sections = self.check_sections()
            action_verbs = self.find_action_verbs()
            achievements = self.check_quantified_achievements()
            formatting = self.analyze_formatting()
            jd_match = self.match_job_description(job_description)

            return {
                'skills': skills,
                'sections': sections,
                'action_verbs': action_verbs,
                'quantified_achievements': achievements,
                'formatting': formatting,
                'job_match': jd_match,
            }
        except Exception as e:
            print(f"Error in analysis: {str(e)}")
            return {
                'skills': {'technical': [], 'soft': [], 'total_count': 0},
                'sections': {},
                'action_verbs': [],
                'quantified_achievements': {'count': 0, 'examples': []},
                'formatting': {'issues': [], 'suggestions': [], 'word_count': 0, 'line_count': 0},
                'job_match': None,
            }