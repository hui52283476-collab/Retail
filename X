import sys
import os
from docx import Document
import requests
import json

# OpenRouter API configuration
API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY = "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"
MODEL = "google/gemma-2-9b-it:free"

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

def summarize_text(text, max_tokens=200):
    if not text or not text.strip():
        return "No input text provided for summarization."
    
    # TRUNCATE TEXT - Free tier can't handle 2045 chars!
    if len(text) > 1000:
        text = text[:1000] + "\n\n[Text truncated for API limits]"
    
    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert summarizer. Create a concise summary (50-150 words) "
                "of the provided text. Focus on main ideas only."
            )
        },
        {
            "role": "user",
            "content": f"Summarize:\n\n{text}"
        }
    ]
    
    payload = {
        "model": MODEL,
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
        response = requests.post(API_URL, headers=headers, json=payload)
        
        
        result = response.json()
        
        if 'choices' in result and len(result['choices']) > 0:
            summary = result['choices'][0]['message']['content'].strip()
            print(f"✨ Raw summary length: {len(summary)} chars")
            return summary
        else:
            print(f"❌ No choices in response: {json.dumps(result, indent=2)}")
            return f"Unexpected response: {json.dumps(result, indent=2)}"
    
    except requests.exceptions.RequestException as e:
        print(f"🌐 Network error: {str(e)}")
        return f"Network error: {str(e)}"
    except json.JSONDecodeError as e:
        print(f"🔧 JSON error: {str(e)}")
        return f"JSON error: {str(e)}"
    except Exception as e:
        print(f"💥 Unexpected error: {str(e)}")
        return f"Error: {str(e)}"

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
    
    
    summary = summarize_text(text)
    print("📄 SUMMARY")
    print(summary)
