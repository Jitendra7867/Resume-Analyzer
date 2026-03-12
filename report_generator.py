from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle, 
                                Paragraph, Spacer, PageBreak, Image)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import os


class ReportGenerator:
    """Generate professional PDF reports."""

    def __init__(self, filename="resume_report.pdf"):
        self.filename = filename
        self.doc = SimpleDocTemplate(
            filename,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1*inch,
            bottomMargin=0.75*inch
        )
        self.styles = getSampleStyleSheet()
        self.story = []
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Create custom paragraph styles."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#3a7bd5'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Section header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold',
            borderPadding=5,
            backColor=colors.HexColor('#ecf0f1'),
            leftIndent=10
        ))

        # Score style
        self.styles.add(ParagraphStyle(
            name='ScoreText',
            parent=self.styles['Normal'],
            fontSize=48,
            textColor=colors.HexColor('#00c853'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

    def add_header(self, contact_info):
        """Add report header."""
        # Title
        title = Paragraph("Resume Analysis Report", self.styles['CustomTitle'])
        self.story.append(title)

        # Date and candidate info
        date_text = f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
        date_para = Paragraph(date_text, self.styles['Normal'])
        self.story.append(date_para)

        if contact_info.get('name'):
            name_para = Paragraph(
                f"<b>Candidate:</b> {contact_info['name']}", 
                self.styles['Normal']
            )
            self.story.append(name_para)

        self.story.append(Spacer(1, 0.3*inch))

    def add_score_section(self, score_data):
        """Add overall score section."""
        self.story.append(Paragraph("Overall Score", self.styles['SectionHeader']))

        # Big score display
        score_color = score_data['grade']['color']
        score_style = ParagraphStyle(
            'TempScore',
            parent=self.styles['ScoreText'],
            textColor=colors.HexColor(score_color.replace('#', ''))
        )
        score_text = f"{score_data['total_score']}/100"
        self.story.append(Paragraph(score_text, score_style))

        grade_text = f"{score_data['grade']['letter']} - {score_data['grade']['label']}"
        grade_para = Paragraph(
            f"<b>{grade_text}</b>",
            ParagraphStyle('grade', parent=self.styles['Normal'], 
                         fontSize=14, alignment=TA_CENTER)
        )
        self.story.append(grade_para)
        self.story.append(Spacer(1, 0.2*inch))

        # Category breakdown table
        data = [['Category', 'Score', 'Rating']]
        for cat, val in score_data['category_scores'].items():
            rating = '⭐⭐⭐⭐⭐' if val >= 90 else '⭐⭐⭐⭐' if val >= 75 else '⭐⭐⭐' if val >= 60 else '⭐⭐'
            data.append([
                cat.replace('_', ' ').title(),
                f"{val}%",
                rating
            ])

        table = Table(data, colWidths=[3*inch, 1*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3a7bd5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))

        self.story.append(table)
        self.story.append(Spacer(1, 0.3*inch))

    def add_skills_section(self, analysis):
        """Add skills section."""
        self.story.append(Paragraph("Skills Detected", self.styles['SectionHeader']))

        skills = analysis['skills']
        
        # Technical skills
        tech_text = f"<b>Technical Skills ({len(skills['technical'])}):</b><br/>"
        if skills['technical']:
            tech_text += ', '.join(skills['technical'][:20])
            if len(skills['technical']) > 20:
                tech_text += f"... and {len(skills['technical']) - 20} more"
        else:
            tech_text += "<i>No technical skills detected</i>"

        self.story.append(Paragraph(tech_text, self.styles['Normal']))
        self.story.append(Spacer(1, 0.15*inch))

        # Soft skills
        soft_text = f"<b>Soft Skills ({len(skills['soft'])}):</b><br/>"
        if skills['soft']:
            soft_text += ', '.join(skills['soft'][:15])
        else:
            soft_text += "<i>No soft skills detected</i>"

        self.story.append(Paragraph(soft_text, self.styles['Normal']))
        self.story.append(Spacer(1, 0.2*inch))

    def add_ats_section(self, ats_data):
        """Add ATS compatibility section."""
        if not ats_data:
            return

        self.story.append(Paragraph("ATS Compatibility", self.styles['SectionHeader']))

        # ATS Score
        ats_text = f"<b>ATS Score:</b> {ats_data['score']}/100 - {ats_data['rating']}"
        self.story.append(Paragraph(ats_text, self.styles['Normal']))
        self.story.append(Spacer(1, 0.1*inch))

        # Issues
        if ats_data['issues']:
            issues_text = "<b>Issues Found:</b><br/>"
            for issue in ats_data['issues']:
                issues_text += f"• {issue}<br/>"
            self.story.append(Paragraph(issues_text, self.styles['Normal']))

        self.story.append(Spacer(1, 0.2*inch))

    def add_recommendations(self, recommendations):
        """Add recommendations section."""
        if not recommendations:
            return

        self.story.append(Paragraph("Recommendations", self.styles['SectionHeader']))

        for i, rec in enumerate(recommendations[:10], 1):
            priority_color = {
                'HIGH': '#ff5252',
                'MEDIUM': '#ffab40',
                'LOW': '#69f0ae'
            }.get(rec['priority'], '#666')

            rec_text = f"<b>{i}. {rec['category']}</b> "
            rec_text += f"<font color='{priority_color}'>[{rec['priority']}]</font><br/>"
            rec_text += f"{rec['message']}<br/>"

            if rec.get('tips'):
                for tip in rec['tips'][:3]:
                    rec_text += f"  💡 {tip}<br/>"

            self.story.append(Paragraph(rec_text, self.styles['Normal']))
            self.story.append(Spacer(1, 0.15*inch))

    def add_grammar_section(self, grammar_data):
        """Add grammar analysis section."""
        if not grammar_data or not grammar_data.get('available'):
            return

        self.story.append(Paragraph("Writing Quality", self.styles['SectionHeader']))

        grammar = grammar_data.get('grammar', {})
        if grammar.get('total_errors') is not None:
            error_text = f"<b>Grammar Check:</b> {grammar['total_errors']} issues found<br/>"
            error_text += f"<b>Quality Score:</b> {grammar.get('quality_score', 0)}/100"
            self.story.append(Paragraph(error_text, self.styles['Normal']))

        readability = grammar_data.get('readability', {})
        if readability:
            read_text = f"<b>Readability:</b> {readability.get('score', 0)}/100<br/>"
            read_text += f"Average sentence length: {readability.get('avg_sentence_length', 0)} words"
            self.story.append(Paragraph(read_text, self.styles['Normal']))

        self.story.append(Spacer(1, 0.2*inch))

    def generate(self, contact_info, score_data, analysis, 
                 recommendations, ats_data=None, grammar_data=None):
        """Generate complete PDF report."""
        self.add_header(contact_info)
        self.add_score_section(score_data)
        self.add_skills_section(analysis)
        
        if ats_data:
            self.add_ats_section(ats_data)
        
        if grammar_data:
            self.add_grammar_section(grammar_data)
        
        self.add_recommendations(recommendations)

        # Build PDF
        self.doc.build(self.story)
        return self.filename