# summarizer.py - Run Summary 功能
import docx
import os

def read_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

def summarize_text(text, max_words=100):
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + "..."

if __name__ == "__main__":
    file_path = input("請輸入 .docx 檔案路徑（例如 scrip.docx）：").strip()
    if not os.path.exists(file_path):
        print("檔案不存在！")
    else:
        print("正在讀取文件...")
        text = read_docx(file_path)
        print(f"總字數：{len(text)}")
        summary = summarize_text(text)
        print("\n文件摘要：")
        print("="*50)
        print(summary)
        print("="*50)
