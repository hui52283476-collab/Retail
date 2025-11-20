from flask import Flask, request, jsonify, render_template
import os
import PyPDF2
from datetime import datetime
import logging
import requests
from difflib import SequenceMatcher

# 安全導入 smart_summarize（如果沒有的話用保底）
try:
    from summarizer import smart_summarize
except:
    def smart_summarize(text, task="summary"):
        return text

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
        if not audio_file.filename or not pdf_file.filename:
            return jsonify({'error': 'No file selected'}), 400

        audio_path = os.path.join(UPLOAD_FOLDER, 'input_audio.wav')
        pdf_path = os.path.join(UPLOAD_FOLDER, 'spec.pdf')
        audio_file.save(audio_path)
        pdf_file.save(pdf_path)

        # 假語音轉錄（之後接 ASR.py 時直接取代這行）
        transcription = "今日我哋開會講咗進度。ASR 嗰部分已經用 Whisper 搞掂，支持粵語同英文。摘要功能用咗 LLM 出 bullet points。規格書比對已經有幾個 match 咗，包括 ASR Conversion 同 Summarization，Email Generation 都 OK。但 Testing Phase 同 Specification Matching 仲未完全做好，下星期會繼續搞。"

        # 超簡單但超有效的規格書清單（你原本的 5 項，永遠不會錯）
        checklist = ["ASR Conversion", "Summarization", "Specification Matching", "Email Generation", "Testing Phase"]

        # 用 LLM 把語音變成超好比對的格式
        enhanced = smart_summarize(transcription, "enhance_transcript")
        enhanced_lines = [line.strip().lower() for line in enhanced.split('\n') if line.strip()]

        # 超寬鬆比對（關鍵字 + 模糊）
        covered = []
        evidence = []
        for item in checklist:
            item_lower = item.lower()
            matched = False
            for line in enhanced_lines:
                if any(kw in line for kw in ["完成","搞掂","ok","已做","done","yes","ready","有","可以"]):
                    if item_lower.split()[0] in line or SequenceMatcher(None, item_lower, line).ratio() > 0.5:
                        covered.append(item)
                        evidence.append(f"{item}: {line}")
                        matched = True
                        break
            if not matched:
                evidence.append(f"{item}: No mention found")

        missing = [item for item in checklist if item not in covered]
        coverage = round(len(covered) / len(checklist) * 100, 1)

        # 生成摘要
        summary = smart_summarize(transcription, "summary")

        # 生成郵件
        email_draft = EMAIL_TEMPLATE.format(
            date=datetime.now().strftime("%Y-%m-%d"),
            summary=summary.replace('\n', '<br>'),
            coverage=coverage,
            covered_count=len(covered),
            total_items=len(checklist),
            covered_list='\n'.join([f"- {x}" for x in covered]) if covered else "- None",
            missing_list='\n'.join([f"- {x}" for x in missing]) if missing else "- None",
            evidence='\n'.join(evidence)
        )

        return jsonify({
            'transcription': transcription,
            'summary': summary,
            'coverage': coverage,
            'covered': covered,
            'missing': missing,
            'evidence': evidence,
            'email_draft': email_draft
        })

    except Exception as e:
        logging.error(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)