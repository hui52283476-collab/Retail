from main import generate_summary_data  
from flask import Flask, request, render_template, jsonify
import os
import whisper
import PyPDF2
import docx
import requests
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 載入模型
print("正在載入 Whisper 模型...")
model = whisper.load_model("base")
print("模型載入完成！")

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
        backup_docx = os.path.join(UPLOAD_FOLDER, 'scrip.docx')  # 可選備用

        audio_file.save(audio_path)
        pdf_file.save(pdf_path)

        # === 呼叫你的 main.py 真正 ASR + LLM ===
        result = generate_summary_data(
            audio_path=audio_path,
            backup_docx=backup_docx
        )

        transcription = result["transcription"]
        summaries = result["summaries"]

        # 取第一個模型的摘要當主摘要（或你指定）
        summary = summaries[0][1] if summaries else "無法生成摘要"

        # PDF 比對
        checklist = extract_checklist(pdf_path)
        coverage, covered, missing, evidence = match_specification(summary, checklist)

        # 生成郵件
        email_draft = generate_email(summary, coverage, covered, missing, evidence)

        return jsonify({
            'transcription': transcription[:300] + '...' if len(transcription) > 300 else transcription,
            'summary': summary,
            'coverage': coverage,
            'covered': covered,
            'missing': missing,
            'evidence': evidence,
            'email_draft': email_draft,
            'all_summaries': dict(summaries)  # 額外回傳所有模型摘要
        })

    except Exception as e:
        logging.exception("Upload error")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("伺服器啟動：http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
