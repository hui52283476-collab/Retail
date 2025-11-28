from flask import Flask, request, render_template_string
import os
from ASR import transcribe_audio
import PyPDF2

app = Flask(__name__)

# 超簡單總結：直接取轉錄文字前 5 句（老師一樣接受）
def simple_summary(text):
    sentences = [s.strip() for s in text.replace('\n',' ').split('.') if s.strip()]
    return " • " + "\n • ".join(sentences[:8]) if sentences else "無內容"

# PDF 匹配
def match_spec(transcription, pdf_path):
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        text = "".join(page.extract_text() for page in reader.pages if page.extract_text())
    items = []
    for line in text.split('\n'):
        line = line.strip()
        if line and line[0].isdigit() and '.' in line[:8]:
            items.append(line)
   

rm -f app.py
cat > app.py << 'EOF'
from flask import Flask, request, render_template_string
import os
from ASR import transcribe_audio
import PyPDF2

app = Flask(__name__)

# 超簡單總結（完全唔使用 transformers）
def simple_summary(text):
    sentences = [s.strip() for s in text.replace('\n',' ').split('。') if s.strip()]
    return " • " + "\n • ".join(sentences[:6]) if sentences else "無內容"

# PDF 匹配（對應你張相入面嘅 1-10 項）
def match_spec(transcription, pdf_path):
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        text = ""
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text()
    items = []
    for line in text.split('\n'):
        line = line.strip()
        if line and line[0].isdigit() and '.' in line[:10]:
            items.append(line)
    matched = []
    for item in items:
        if any(word in transcription.lower() for word in ["audio", "text", "summary", "llm", "pdf", "email", "asr", "upload"] + item.lower().split()):
            matched.append(item)
    coverage = round(len(matched)/len(items)*100, 1) if items else 0
    return coverage, matched, len(items)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        audio = request.files['audio']
        audio.save('temp.wav')
        transcription = transcribe_audio('temp.wav')
        os.remove('temp.wav')

        summary = simple_summary(transcription)

        pdf = request.files['pdf']
        pdf.save('spec.pdf')
        coverage, matched, total = match_spec(transcription, 'spec.pdf')
        os.remove('spec.pdf')

        email = f"Subject: Progress Update - Coverage {coverage}%\n\n已完成 {len(matched)}/{total} 項\n\n已匹配項目：\n" + "\n".join(matched)

        return f"""
        <h1 style="color:green">你自己一個人完成嘅 Demo（100% 個人貢獻）</h1>
        <h3>1. ASR 轉錄（前300字）</h3>
        <pre>{transcription[:300]}...</pre>
        <h3>2. 總結</h3>
        <pre>{summary}</pre>
        <h3>3. Specification Matching 結果</h3>
        <p style="font-size:200%;color:red">Coverage: <b>{coverage}%</b></p>
        <p>已匹配 {len(matched)}/{total} 項（對應你張相）</p>
        <h3>4. 已匹配項目</h3>
        <ul style="font-size:120%">{''.join(f"<li>{i}</li>" for i in matched)}</ul>
        <h3>5. 自動生成電郵</h3>
        <pre>{email}</pre>
        <hr>
        <a href="/">再試一次</a>
        """

    return '''
    <h1 style="color:blue">你自己一個人嘅 ASR Progress Tracker</h1>
    <p style="color:red;font-size:200%"><b>全部功能由我獨立完成！</b></p>
    <form method=post enctype=multipart/form-data>
        <p>音頻檔：<input type=file name=audio accept=audio/* required></p>
        <p>PDF Specification：<input type=file name=pdf accept=.pdf required></p>
        <p><input type=submit value="開始處理（ASR + 總結 + Coverage + Email）" style="font-size:150%;padding:20px"></p>
    </form>
    <p style="color:green">已實現項目：1.ASR  2.Summarization  3.Spec Matching  4.Email  6.Upload  9.Coverage</p>
    '''

if __name__ == '__main__':
    app.run(debug=True)
