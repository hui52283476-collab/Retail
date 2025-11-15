This is a complete end-to-end AI meeting summarization pipeline that turns audio recordings or written meeting notes into a professional summary + follow-up email, all in one click.


How to Use It (Simple Steps)

Upload either:
A .wav audio file (Cantonese/English meeting recording)
Or a .docx file (meeting minutes/notes)

1. Click "Start"
2. Wait ~30 seconds
3. Get output.txt — a full report with:
Full transcript
10 AI summaries (from different LLMs)
The best summary (auto-selected)
Spec coverage score (how many of your 12 project KPIs are met)
A ready-to-send follow-up email

What Happens Behind the Scenes (Step-by-Step)
1. Receives your file (app.py Flask web server)
2. If .wav → transcribes Cantonese speech to text using Google Speech-to-Text (ASR.py) 
→ Handles long audio by auto-splitting into 20-sec chunks
3. If no audio or transcription fails → falls back to .docx and extracts text (summarizer.py)
4. Sends the transcript to 10 free top-tier LLMs via OpenRouter API: 
Gemma-2, Llama-3.3-70B, Mistral, Qwen, Moonshot Kimi, etc.
5. Collects all 10 summaries, picks the longest valid one as the "Best Summary"
6. Checks the best summary against your 12 project specs (e.g., "ASR transcription", "LLM summary", "email generation") → calculates coverage score
7. Generates a professional follow-up email with subject, progress, gaps, and next steps
8. Saves everything to output.txt — clean, structured, ready to send

What the Code Does (Step-by-Step)

1. Reads a .docx file
- The function read_docx(file_path):
  - Opens the Word document.
  - Extracts all non-empty paragraphs.
  - Joins them into a single text string.
  - Returns the full text for summarization.

2. Sends the text to OpenRouter AI
- The function summarize_text(text):
  - Prepares a prompt asking the AI to summarize the meeting minutes.
  - Sends the request to OpenRouter’s API using the specified model 
  - Receives and returns the summary.

3. Runs from the command line
- You run the script like this:
  python summarizer.py path/to/your/meeting_minutes.docx
  
- It checks:
  - That you provided a file path.
  - That the file is a .docx.
  - That the file exists and contains text.

4. Prints the result
- It shows:
  - The number of characters extracted.
  - The generated summary from the AI.


Use Case: Summarizing Meeting Minutes*

If you have a .docx file with meeting notes, this script:
- Reads the content.
- Sends it to an AI summarizer.
- Returns a concise summary focusing on key points and decisions.


What you need to install before running our code?
[requirements.txt](https://github.com/user-attachments/files/23250104/requirements.txt)
