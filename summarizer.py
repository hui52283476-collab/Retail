import requests
import json
from config import API_URL, OPENROUTER_API_KEY, MODEL

def summarize_text(text, max_tokens=200):
    if not text or not text.strip():
        return "No input text provided for summarization."
    
    # Truncate text for API limits
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
