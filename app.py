from flask import Flask, request, jsonify, render_template
import os
import PyPDF2
from datetime import datetime
import random

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
    """讀 PDF 提取檢查清單"""
    items = []
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            # 簡單提取每行作為 item
            items = [line.strip() for line in text.split('\n') if line.strip() and len(line.strip()) > 10]
        if not items:
            items = ["ASR Conversion", "Summarization", "Specification Matching", "Email Generation", "Testing Phase"]
    except Exception as e:
        items = ["ASR Conversion", "Summarization", "Specification Matching", "Email Generation", "Testing Phase"]
    return items[:5]  # 限 5 個 demo

def match_specification(summary, checklist):
    """簡單匹配（keyword overlap）"""
    summary_lower = summary.lower()
    covered = []
    evidence = []
    for item in checklist:
        item_lower = item.lower()
        # 簡單檢查關鍵字
        keywords = item_lower.split()[:3]
        if any(kw in summary_lower for kw in keywords):
            covered.append(item)
            # 找證據
            quote = next((s for s in summary.split('.') if any(kw in s.lower() for kw in keywords)), "Evidence found in summary")
            evidence.append(f"✓ {item}: \"{quote.strip()}\"")
        else:
            evidence.append(f"❌ {item}: No match found")
    missing = [item for item in checklist if item not in covered]
    coverage = round((len(covered) / len(checklist)) * 100, 1) if checklist else 0
    return coverage, covered, missing, evidence

def generate_email(summary, coverage, covered, missing, evidence):
    return EMAIL_TEMPLATE.format(
        date=datetime.now().strftime("%Y-%m-%d"),
        summary=summary.replace('\n', '<br>'),
        coverage=coverage,
        covered_count=len(covered),
        total_items=len(covered) + len(missing),  # 改呢度
        covered_list='\n'.join([f"- {x}" for x in covered]) if covered else "- None",
        missing_list='\n'.join([f"- {x}" for x in missing]) if missing else "- None",
        evidence='\n'.join(evidence)
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'audio' not in request.files or 'pdf' not in request.files:
            return jsonify({'error': 'Missing audio or PDF'}), 400

        audio_file = request.files['audio']
        pdf_file = request.files['pdf']

        if audio_file.filename == '' or pdf_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # 儲存檔案
        audio_path = os.path.join(UPLOAD_FOLDER, 'input_audio.wav')
        pdf_path = os.path.join(UPLOAD_FOLDER, 'spec.pdf')
        audio_file.save(audio_path)
        pdf_file.save(pdf_path)

        # 假 ASR 轉錄（之後接你 ASR.py）
        transcription = "We recorded the group progress update. Implemented ASR using Whisper for Cantonese and English. Generated point-form summary with LLM. Matched to Retail specification PDF items like ASR Conversion, Summarization, and Email Generation. Coverage is good, but Testing Phase needs work."

        # 假 LLM 總結（點形式）
        summary = "- Completed audio recording and upload features.\n- ASR transcription successful with Whisper.\n- LLM summarization in bullet points.\n- Matched 3/5 spec items.\n- Generated follow-up email draft."

        # PDF 匹配
        checklist = extract_checklist(pdf_path)
        coverage, covered, missing, evidence = match_specification(summary, checklist)

       # 生成電郵（修好變數）
          email_draft = generate_email(summary, coverage, covered, missing, evidence)

        return jsonify({
            'transcription': transcription[:200] + '...',
            'summary': summary,
            'coverage': coverage,
            'covered': covered,
            'missing': missing,
            'evidence': evidence,
            'email_draft': email_draft
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
        app.run(host='0.0.0.0', port=5001, debug=True)
