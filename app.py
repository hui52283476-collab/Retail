from flask import Flask, request, jsonify, render_template_string
import os
from ASR import transcribe_audio  # 你嘅 ASR
import PyPDF2
from transformers import pipeline

app = Flask(__name__)

# LLM 總結
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_text(text):
    if len(text) < 50:
        return text
    result = summarizer(text, max_length=100, min_length=30, do_sample=False)
    return result[0]['summary_text']

# PDF 匹配
def match_spec(transcription, pdf_file):
    try:
        with open(pdf_file, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            spec_text = ''
            for page in reader.pages:
                spec_text += page.extract_text()
        items = [item.strip() for item in spec_text.split('\n') if item.strip()]
        covered = 0
        evidence = {}
        for item in items:
            if any(word in transcription.lower() for word in item.lower().split()):
                covered += 1
                evidence[item] = 'Matched: ' + transcription[:100] + '...'
        coverage = (covered / len(items)) * 100 if items else 0
        return coverage, evidence
    except Exception as e:
        return 0, {'Error': str(e)}

# 電郵草稿
def generate_email(coverage, evidence):
    covered = list(evidence.keys())[:3]
    missing = 100 - coverage
    draft = f"Subject: Progress Update - Coverage: {coverage:.1f}%\n\nDear Team,\n\nCovered: {', '.join(covered)}\nMissing: {missing:.1f}%\n\nBest,\nAssistant"
    return draft

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            if 'audio' in request.files:
                audio = request.files['audio']
                audio_path = 'temp_audio.wav'
                audio.save(audio_path)
                transcription = transcribe_audio(audio_path)
                os.remove(audio_path)
            else:
                transcription = request.form['transcript']
            
            summary = summarize_text(transcription)
            
            pdf = request.files['pdf']
            pdf_path = 'temp_spec.pdf'
            pdf.save(pdf_path)
            coverage, evidence = match_spec(transcription, pdf_path)
            os.remove(pdf_path)
            
            email_draft = generate_email(coverage, evidence)
            
            return jsonify({
                'transcription': transcription,
                'summary': summary,
                'coverage': coverage,
                'evidence': evidence,
                'email': email_draft
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head><title>Progress Tracker</title></head>
    <body>
        <h1>Upload Audio & PDF</h1>
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="audio" accept="audio/*"><br><br>
            <input type="file" name="pdf" accept=".pdf"><br><br>
            <input type="submit" value="Process">
        </form>
        <div id="results"></div>
        <script>
            document.querySelector('form').onsubmit = function(e) {
                e.preventDefault();
                const formData = new FormData(this);
                fetch('/', {method: 'POST', body: formData})
                .then(r => r.json())
                .then(data => {
                    document.getElementById('results').innerHTML = `
                        <h2>Summary:</h2><p>${data.summary}</p>
                        <h2>Coverage:</h2><p>${data.coverage}%</p>
                        <h2>Evidence:</h2><ul>${Object.entries(data.evidence).map(([k,v]) => `<li>${k}: ${v}</li>`).join('')}</ul>
                        <h2>Email:</h2><pre>${data.email}</pre>
                    `;
                });
            };
        </script>
    </body>
    </html>
    '''
    return html

if __name__ == '__main__':
    app.run(debug=True)

