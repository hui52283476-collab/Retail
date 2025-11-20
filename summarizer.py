import sys
import os
from docx import Document
import requests
import json

# OpenRouter API configuration
API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY = "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"

MODELS = [
    {"name": "1.Coder 32B", "id": "qwen/qwen-2.5-coder-32b-instruct:free"},
    {"name": "2.Venice", "id": "cognitivecomputations/dolphin-mistral-24b-venice-edition:free"},
    {"name": "3.Qwen", "id": "qwen/qwen2.5-vl-32b-inst  ruct:free"},
    {"name": "4.Shisa AI", "id": "shisa-ai/shisa-v2-llama3.3-70b:free"},
    {"name": "5.Qwen2.5 72B ", "id": "qwen/qwen-2.5-72b-instruct:free"},
    {"name": "6.NVIDIA", "id": "nvidia/nemotron-nano-9b-v2:free"},
    {"name": "7.Gemma 3n 4B", "id": "google/gemma-3n-e4b-it:free"},
    {"name": "8.Tencent", "id": "tencent/hunyuan-a13b-instruct:free"},
    {"name": "9.Agentica", "id": "agentica-org/deepcoder-14b-preview:free"},
    
    
]

def read_docx(file_path):
    try:
        if not os.path.exists(file_path):
            return None, f"File '{file_path}' does not exist."
        doc = Document(file_path)
        full_text = [paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()]
        text = '\n'.join(full_text)
        if not text:
            return None, "No text found in the DOCX file."
        return text, None
    except Exception as e:
        return None, f"Error reading DOCX file: {str(e)}"

def summarize_text(text, model_info, max_tokens=200):
    if not text or not text.strip():
        return f"No input text provided for summarization ({model_info['name']})."
    
    # TRUNCATE TEXT - Free tier can't handle 2045 chars!
    if len(text) > 1000:
        text = text[:1000] + "\n\n[Text truncated for API limits]"
    
    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert summarizer. Create a concise summary (50-150 words) "
                "of the provided text, focusing on the retail project, audio transcription, "
                "KPI matching, and pipeline development. Include specific challenges and proposed solutions."
            )
        },
        {
            "role": "user",
            "content": f"Summarize:\n\n{text}"
        }
    ]
    
    payload = {
        "model": model_info["id"],
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.3
    }
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://localhost",
        "X-Title": "Docx Summarizer"
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=20)
        print(f"📡 {model_info['name']} API Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ {model_info['name']} API Error: {response.text}")
            return f"API Error ({model_info['name']}): {response.text}"
        
        result = response.json()
        
        if 'choices' in result and len(result['choices']) > 0:
            summary = result['choices'][0]['message']['content'].strip()
            print(f"✨ {model_info['name']} Raw summary length: {len(summary)} chars")
            return summary
        else:
            print(f"❌ {model_info['name']} No choices in response: {json.dumps(result, indent=2)}")
            return f"Unexpected response ({model_info['name']}): {json.dumps(result, indent=2)}"
    
    except requests.exceptions.RequestException as e:
        print(f"🌐 {model_info['name']} Network error: {str(e)}")
        return f"Network error ({model_info['name']}): {str(e)}"
    except json.JSONDecodeError as e:
        print(f"🔧 {model_info['name']} JSON error: {str(e)}")
        return f"JSON error ({model_info['name']}): {str(e)}"
    except Exception as e:
        print(f"💥 {model_info['name']} Unexpected error: {str(e)}")
        return f"Error ({model_info['name']}): {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python summarizer.py <path_to_docx_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    if not file_path.endswith('.docx'):
        print("Error: Please provide a .docx file.")
        sys.exit(1)

    text, error = read_docx(file_path)
    if error:
        print(error)
        sys.exit(1)
    
    print(f"\n📄 Total characters extracted: {len(text)}")
    
    for model in MODELS:
        print(f"\n⏳ Generating summary with {model['name']}...")
        summary = summarize_text(text, model)
        print(f"\n📄 {model['name']} SUMMARY")
        print("="*50)
        print(summary)
        print(f"📏 Word count: {len(summary.split())}")
        print("="*50)