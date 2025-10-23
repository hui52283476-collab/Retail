import os
from docx import Document

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
