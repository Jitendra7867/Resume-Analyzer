import pdfplumber
import docx
import re
import os


class ResumeParser:
    """Parse resume files and extract text content."""

    @staticmethod
    def extract_text(file_path):
        """Extract text based on file extension."""
        ext = os.path.splitext(file_path)[1].lower()

        if ext == '.pdf':
            return ResumeParser._extract_from_pdf(file_path)
        elif ext == '.docx':
            return ResumeParser._extract_from_docx(file_path)
        elif ext == '.txt':
            return ResumeParser._extract_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    @staticmethod
    def _extract_from_pdf(file_path):
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text

    @staticmethod
    def _extract_from_docx(file_path):
        doc = docx.Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text

    @staticmethod
    def _extract_from_txt(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def extract_email(text):
        """Extract email addresses."""
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(pattern, text)
        return emails[0] if emails else None

    @staticmethod
    def extract_phone(text):
        """Extract phone numbers."""
        pattern = r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\./0-9]{7,15}'
        phones = re.findall(pattern, text)
        return phones[0].strip() if phones else None

    @staticmethod
    def extract_name(text):
        """Extract name (first non-empty line heuristic)."""
        lines = text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and not re.search(r'@|http|www|\d{5,}', line):
                return line
        return "Unknown"

    @staticmethod
    def extract_links(text):
        """Extract URLs (LinkedIn, GitHub, Portfolio)."""
        pattern = r'https?://[^\s,\)]+'
        links = re.findall(pattern, text)
        categorized = {
            'linkedin': None,
            'github': None,
            'other': []
        }
        for link in links:
            if 'linkedin' in link.lower():
                categorized['linkedin'] = link
            elif 'github' in link.lower():
                categorized['github'] = link
            else:
                categorized['other'].append(link)
        return categorized

    @staticmethod
    def extract_education(text):
        """Extract education details."""
        education_keywords = [
            r"bachelor'?s?", r"master'?s?", r"ph\.?d\.?", r"b\.?tech",
            r"m\.?tech", r"b\.?sc", r"m\.?sc", r"b\.?e\.?", r"m\.?e\.?",
            r"mba", r"bba", r"b\.?com", r"m\.?com", r"diploma",
            r"b\.?c\.?a", r"m\.?c\.?a", r"bca", r"mca",
            r"computer science", r"engineering", r"university",
            r"college", r"institute", r"school"
        ]
        pattern = '|'.join(education_keywords)
        lines = text.split('\n')
        education = []
        for line in lines:
            if re.search(pattern, line, re.IGNORECASE):
                cleaned = line.strip()
                if cleaned and len(cleaned) > 5:
                    education.append(cleaned)
        return education

    @staticmethod
    def extract_experience_years(text):
        """Estimate years of experience."""
        patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience|exp)',
            r'experience\s*(?:of)?\s*(\d+)\+?\s*(?:years?|yrs?)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return 0