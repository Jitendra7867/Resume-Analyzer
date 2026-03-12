from flask import Flask, render_template, request, jsonify, send_file, session
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import secrets
import traceback

from parser_module import ResumeParser
from analyzer import ResumeAnalyzer
from scorer import ResumeScorer
from ats_checker import ATSChecker
from grammar_checker import GrammarChecker
from report_generator import ReportGenerator
from version_control import ResumeVersionControl

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['REPORT_FOLDER'] = 'reports'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

for folder in [app.config['UPLOAD_FOLDER'], app.config['REPORT_FOLDER'], 'history']:
    os.makedirs(folder, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_user_id():
    if 'user_id' not in session:
        session['user_id'] = secrets.token_hex(8)
    return session['user_id']


@app.route('/')
def index():
    try:
        user_id = get_user_id()
        version_control = ResumeVersionControl(user_id)
        history = version_control.load_history()
        
        return render_template('index.html', 
                             has_history=len(history) > 0,
                             version_count=len(history))
    except Exception as e:
        print(f"Error in index: {str(e)}")
        return render_template('index.html', has_history=False, version_count=0)


@app.route('/analyze', methods=['POST'])
def analyze():
    filepath = None
    try:
        if 'resume' not in request.files:
            return render_template('index.html', error='No file uploaded')

        file = request.files['resume']
        if file.filename == '':
            return render_template('index.html', error='No file selected')

        if not allowed_file(file.filename):
            return render_template('index.html',
                                 error='Invalid file type. Use PDF, DOCX, or TXT')

        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)

        # Parse resume
        parser = ResumeParser()
        text = parser.extract_text(filepath)

        if not text or len(text.strip()) < 50:
            if filepath and os.path.exists(filepath):
                os.remove(filepath)
            return render_template('index.html',
                                 error='Could not extract enough text from resume')

        # Extract contact info
        contact_info = {
            'name': parser.extract_name(text) or 'Unknown',
            'email': parser.extract_email(text) or 'Not found',
            'phone': parser.extract_phone(text) or 'Not found',
            'links': parser.extract_links(text) or {},
            'education': parser.extract_education(text) or [],
            'experience_years': parser.extract_experience_years(text) or 0,
        }

        # Get job description (optional)
        job_description = request.form.get('job_description', '').strip()

        # Main analysis
        analyzer = ResumeAnalyzer(text)
        analysis = analyzer.get_full_analysis(
            job_description if job_description else None
        )

        # Scoring
        score_data = ResumeScorer.calculate_score(analysis)
        recommendations = ResumeScorer.generate_recommendations(
            analysis, score_data
        )

        # ATS Check
        ats_checker = ATSChecker(text)
        ats_data = ats_checker.calculate_ats_score()
        keyword_density = ats_checker.get_keyword_density()

        # Grammar Check
        grammar_checker = GrammarChecker(text)
        grammar_data = grammar_checker.get_full_analysis()

        # Save to version history
        user_id = get_user_id()
        version_control = ResumeVersionControl(user_id)
        version_number = version_control.save_version(
            score_data, analysis, unique_filename
        )

        # Generate PDF Report
        report_filename = f"report_{timestamp}.pdf"
        report_path = os.path.join(app.config['REPORT_FOLDER'], report_filename)
        
        try:
            report_gen = ReportGenerator(report_path)
            report_gen.generate(
                contact_info, score_data, analysis, 
                recommendations, ats_data, grammar_data
            )
        except Exception as report_error:
            print(f"PDF generation error: {str(report_error)}")
            report_filename = None

        # Clean up uploaded file
        if filepath and os.path.exists(filepath):
            os.remove(filepath)

        return render_template('results.html',
                             contact=contact_info,
                             analysis=analysis,
                             score=score_data,
                             recommendations=recommendations,
                             ats=ats_data,
                             keyword_density=keyword_density,
                             grammar=grammar_data,
                             job_description=bool(job_description),
                             report_filename=report_filename,
                             version_number=version_number)

    except Exception as e:
        print(f"Error in analyze: {str(e)}")
        print(traceback.format_exc())
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
        return render_template('index.html', 
                             error=f'Error analyzing resume: {str(e)}')


@app.route('/download-report/<filename>')
def download_report(filename):
    try:
        report_path = os.path.join(app.config['REPORT_FOLDER'], filename)
        if os.path.exists(report_path):
            return send_file(report_path, as_attachment=True)
        return "Report not found", 404
    except Exception as e:
        print(f"Error downloading report: {str(e)}")
        return "Error downloading report", 500


@app.route('/history')
def history():
    try:
        user_id = get_user_id()
        version_control = ResumeVersionControl(user_id)
        history_data = version_control.load_history()
        progress_data = version_control.get_progress_data()

        return render_template('history.html',
                             history=history_data,
                             progress=progress_data)
    except Exception as e:
        print(f"Error in history: {str(e)}")
        return render_template('history.html', history=[], progress=None)


@app.route('/compare')
def compare():
    try:
        user_id = get_user_id()
        version_control = ResumeVersionControl(user_id)
        
        version_index = request.args.get('version', -2, type=int)
        comparison = version_control.get_comparison(version_index)

        if not comparison:
            return render_template('compare.html', 
                                 error='Not enough versions to compare')

        return render_template('compare.html', comparison=comparison)
    except Exception as e:
        print(f"Error in compare: {str(e)}")
        return render_template('compare.html', error=str(e))


@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'version': '2.0',
        'features': [
            'resume_analysis',
            'ats_checking',
            'pdf_reports',
            'version_history'
        ]
    })


if __name__ == '__main__':
    print("=" * 50)
    print("Resume Analyzer Pro - Starting...")
    print("=" * 50)
    print(f"Upload folder: {os.path.abspath(app.config['UPLOAD_FOLDER'])}")
    print(f"Report folder: {os.path.abspath(app.config['REPORT_FOLDER'])}")
    print("=" * 50)
    app.run(debug=True, port=5000, host='0.0.0.0')