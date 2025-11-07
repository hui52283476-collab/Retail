import os
import requests
from docx import Document

# === ASR Import ===
try:
    from ASR import transcribe_audio
except ImportError:
    def transcribe_audio(path, lang="zh-HK"): 
        return "[ASR.py not found]"

# === OpenRouter Config ===
API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY = "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"

MODELS = [
    {"name": "1.Gemma-2", "id": "google/gemma-2-9b-it:free"},
    {"name": "2.Mistral", "id": "mistralai/mistral-7b-instruct:free"},
    {"name": "3.Microsoft", "id": "qwen/qwen3-coder:free"},
    {"name": "4.Meta", "id": "meta-llama/llama-3.3-70b-instruct:free"},
    {"name": "5.Mgpt-oss-20b", "id": "openai/gpt-oss-20b:free"},
    {"name": "6.Venice", "id": "cognitivecomputations/dolphin-mistral-24b-venice-edition:free"},
    {"name": "7.Mistral Nemo", "id": "mistralai/mistral-nemo:free"},
    {"name": "8.Shisa AI", "id": "shisa-ai/shisa-v2-llama3.3-70b:free"},
    {"name": "9.NVIDIA", "id": "nvidia/nemotron-nano-9b-v2:free"}, 
    {"name": "10.MoonshotAI", "id": "moonshotai/kimi-dev-72b:free"},
]

SPEC_CHECKLIST = [
    "Instant audio recording", "Upload audio", "Upload transcript", "Drag-and-drop",
    "ASR transcription", "LLM point-form summary", "Match summary to specification",
    "Display coverage score", "Auto-generated follow-up email", "Progress indicator",
    "Error messages", "Temporary storage"
]

def read_docx(file_path):
    if not os.path.exists(file_path): return None, "File not found"
    try:
        doc = Document(file_path)
        text = '\n'.join(p.text for p in doc.paragraphs if p.text.strip())
        return text or None, None
    except Exception as e:
        return None, f"DOCX Error: {e}"

def summarize_text(text, model_info):
    if len(text) > 1500: text = text[:1500] + "\n[Truncated]"
    
    messages = [
        {"role": "system", "content": "Summarize in 80-150 words, point form, cover: ASR, LLM, pipeline, KPI, progress, challenges."},
        {"role": "user", "content": f"Text:\n\n{text}"}
    ]
    
    payload = {"model": model_info["id"], "messages": messages, "max_tokens": 250, "temperature": 0.4}
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    
    try:
        r = requests.post(API_URL, json=payload, headers=headers, timeout=25)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
        return f"[API {r.status_code}]"
    except Exception as e:
        return f"[Error: {str(e)[:50]}]"

def match_specification(summary):
    summary_lower = summary.lower()
    covered = []
    for item in SPEC_CHECKLIST:
        keywords = item.lower().split()[:2]  # 更寬鬆
        if any(kw in summary_lower for kw in keywords):
            covered.append(item)
    score = len(covered)
    return covered, [i for i in SPEC_CHECKLIST if i not in covered], score, len(SPEC_CHECKLIST)

def generate_follow_up_email(transcript, summary, covered, missing, total):
    # 選最長成功總結
    if not summary or "[API" in summary: 
        return "[No valid summary for email]"

    prompt = f"""
Write a professional follow-up email (120-180 words):

Subject: Progress Update – Group Pipeline (v1.1)

Structure:
1. Greeting: Dear Team,
2. Key progress (from summary below)
3. Coverage: {len(covered)}/{total} specs covered
4. Top 3 covered: {', '.join(covered[:3])}
5. Top 3 missing: {', '.join(missing[:3])}
6. Next steps & challenges
7. Closing: Best regards, [Your Name]

Summary:
{summary}

Transcript snippet:
{transcript[:200]}...
"""

    # 用 Microsoft 模型（最穩定）
    payload = {
        "model": "qwen/qwen3-coder:free",
        "messages": [
            {"role": "system", "content": "You are a clear, professional project manager."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 400,
        "temperature": 0.5
    }
    
    try:
        r = requests.post(API_URL, json=payload, headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }, timeout=25)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
        return f"[Email API {r.status_code}]"
    except Exception as e:
        return f"[Email Failed: {str(e)[:50]}]"

# === MAIN ===
def main():
    audio_path = "sample.wav"
    backup_docx = "scrip.docx"
    output_file = "output.txt"
    
    print("Starting Pipeline...\n")
    
    # Step 1: Get transcription
    transcription = ""
    if os.path.exists(audio_path):
        print(f"Transcribing {audio_path}...")
        transcription = transcribe_audio(audio_path)
    else:
        print("Audio not found, trying DOCX...")
    
    if not transcription or len(transcription) < 50:
        if os.path.exists(backup_docx):
            text, err = read_docx(backup_docx)
            if text: transcription = text
            else: print(f"DOCX Error: {err}"); return
        else:
            print("No input! Need sample.wav or scrip.docx")
            return
    
    print(f"Transcript loaded ({len(transcription)} chars)\n")
    
    # Step 2: Summarize with working models
    print("Summarizing with stable LLMs...\n")
    summaries = []
    for model in MODELS:
        print(f"{model['name']}...")
        summary = summarize_text(transcription, model)
        summaries.append((model['name'], summary))
        print(f"{model['name']} Done\n")
    
    # Use longest valid summary
    valid_summaries = [(n, s) for n, s in summaries if "API" not in s and len(s) > 50]
    if not valid_summaries:
        print("All summaries failed!")
        return
    best_name, best_summary = max(valid_summaries, key=lambda x: len(x[1]))
    
    # Step 3: Match spec
    covered, missing, score, total = match_specification(best_summary)
    
    # Step 4: Generate email
    print("Generating email...")
    email = generate_follow_up_email(transcription, best_summary, covered, missing, total)
    
    # Step 5: Save
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("GROUP PROGRESS TRACKING REPORT\n")
        f.write("="*60 + "\n\n")
        f.write(f"TRANSCRIPT:\n{transcription}\n\n")
        f.write("LLM SUMMARIES:\n")
        for n, s in summaries: f.write(f"\n{n}:\n{s}\n")
        f.write(f"\nBEST SUMMARY ({best_name}):\n{best_summary}\n")
        f.write(f"\nSPEC COVERAGE: {score}/{total}\n")
        f.write(f"Covered: {', '.join(covered[:3])}{'...' if len(covered)>3 else ''}\n")
        f.write(f"Missing: {', '.join(missing[:3])}{'...' if len(missing)>3 else ''}\n\n")
        f.write("FOLLOW-UP EMAIL:\n")
        f.write("="*60 + "\n")
        f.write(email + "\n")
    
    print(f"Report saved: {output_file}")
    print(f"Coverage: {score}/{total}")

if __name__ == "__main__":
    main()
