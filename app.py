from flask import Flask, request, jsonify, render_template
from main import generate_summary_data
import logging
import os
import PyPDF2
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

EMAIL_TEMPLATE = """
Subject: Group Progress Update - {date}
Dear Team,
Summary:
{summary}
Coverage: {coverage}% ({covered_count}/{total_items})
Covered Items:
{covered_list}
Missing Items:
{missing_list}
Evidence:
{evidence}
Please address missing items before next update.
Best,
Progress Tracker Bot
"""

def extract_checklist(pdf_path):
    items = []
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            items = [line.strip() for line in text.split('\n') if line.strip() and len(line.strip()) > 10]
        if not items:
            items = ["ASR Conversion", "Summarization", "Specification Matching", "Email Generation", "Testing Phase"]
    except Exception as e:
        items = ["ASR Conversion", "Summarization", "Specification Matching", "Email Generation", "Testing Phase"]
    return items[:5]

def match_specification(summary, checklist):
    summary_lower = summary.lower()
    covered = []
    evidence = []
    for item in checklist:
        item_lower = item.lower()
        keywords = item_lower.split()[:3]
        if any(kw in summary_lower for kw in keywords):
            covered.append(item)
            quote = next((s for s in summary.split('.') if any(kw in s.lower() for kw in keywords)), "Evidence found in summary")
            evidence.append(f"{item}: \"{quote.strip()}\"")
        else:
            evidence.append(f"{item}: No match found")
    missing = [item for item in checklist if item not in covered]
    coverage = round((len(covered) / len(checklist)) * 100, 1) if checklist else 0
    return coverage, covered, missing, evidence

def generate_email(summary, coverage, covered, missing, evidence):
    return EMAIL_TEMPLATE.format(
        date=datetime.now().strftime("%Y-%m-%d"),
        summary=summary.replace('\n', '<br>'),
        coverage=coverage,
        covered_count=len(covered),
        total_items=len(covered) + len(missing),
        covered_list='\n'.join([f"- {x}" for x in covered]) if covered else "- None",
        missing_list='\n'.join([f"- {x}" for x in missing]) if missing else "- None",
        evidence='\n'.join(evidence)
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_summary', methods=['POST'])
def run_summary():
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'Missing audio file'}), 400
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        audio_path = os.path.join(UPLOAD_FOLDER, 'input_audio.wav')
        audio_file.save(audio_path)
        result = generate_summary_data(audio_path=audio_path, backup_docx=None)
        transcription = result["transcription"]
        summaries = result["summaries"]
        return jsonify({
            'transcription': transcription,
            'summary': summaries[0][1] if summaries else "無法生成摘要",
            'all_summaries': dict(summaries) if summaries else {}
        })
    except Exception as e:
        logging.exception("Run Summary error")
        return jsonify({'error': str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'audio' not in request.files or 'pdf' not in request.files:
            return jsonify({'error': 'Missing audio or PDF'}), 400
        audio_file = request.files['audio']
        pdf_file = request.files['pdf']
        if audio_file.filename == '' or pdf_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        audio_path = os.path.join(UPLOAD_FOLDER, 'input_audio.wav')
        pdf_path = os.path.join(UPLOAD_FOLDER, 'spec.pdf')
        backup_docx = os.path.join(UPLOAD_FOLDER, 'scrip.docx')
        audio_file.save(audio_path)
        pdf_file.save(pdf_path)
        result = generate_summary_data(audio_path=audio_path, backup_docx=backup_docx)
        transcription = result["transcription"]
        summaries = result["summaries"]
        summary = summaries[0][1] if summaries else "無法生成摘要"
        checklist = extract_checklist(pdf_path)
        coverage, covered, missing, evidence = match_specification(summary, checklist)
        email_draft = generate_email(summary, coverage, covered, missing, evidence)
        return jsonify({
            'transcription': transcription[:300] + '...' if len(transcription) > 300 else transcription,
            'summary': summary,
            'coverage': coverage,
            'covered': covered or [],
            'missing': missing or [],
            'evidence': evidence or [],
            'email_draft': email_draft,
            'all_summaries': dict(summaries) if summaries else {}
        })
    except Exception as e:
        logging.exception("Upload error")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
