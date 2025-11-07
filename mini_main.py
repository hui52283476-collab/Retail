# mini_main.py
# Simple test summary (use ASR output text), no NLTK.

from ASR import transcribe_audio  # import ASR

def simple_summarization(text, num_sentences=2):
    '''
    Pure Python summary: take top N sentences + keywords.
    '''
    if len(text.strip()) < 50:
        return text + " (too short, no summary needed)"
    
    # Split sentences (Chinese with . or ? )
    sentences = [s.strip() for s in text.replace('?', '.').split('.') if s.strip()]
    
    # Simple keywords: high freq words
    words = [w for w in text.replace(',', ' ').split() if len(w) > 2]  # rough token
    key_words = set(words[:5])  # top 5 freq
    
    # Take top N sentences
    top_sentences = sentences[:num_sentences]
    summary = '.'.join(top_sentences) + '. Key: ' + ' '.join(key_words)
    return summary.strip()

def main():
    audio_path = "sample.wav"
    language = "zh-TW"
    print(f"Start transcribing {audio_path}...")
    transcription = transcribe_audio(audio_path=audio_path, language=language)
    
    print("Transcribed text:")
    print(transcription)
    
    print("\\nGenerating summary...")
    summary = simple_summarization(transcription, num_sentences=2)
    print("Summary:")
    print(summary)
    
    with open("transcription.txt", "w", encoding="utf-8") as f:
        f.write("Full transcription:\\n" + transcription + "\\n\\nSummary:\\n" + summary)
    print("Saved to transcription.txt")

if __name__ == "__main__":
    main()
