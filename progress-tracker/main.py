import os
from ASR import transcribe_audio
from summarizer import summarize_text, MODELS, read_docx

def generate_summary_data(audio_path="sample.wav", backup_docx="scrip.docx"):
    """
    回傳字典，包含：
    - transcription: 轉錄文字
    - summaries: [(model_name, summary), ...]
    """
    transcription = ""
    
    # Step 1: 轉錄音頻
    if os.path.exists(audio_path):
        try:
            transcription = transcribe_audio(audio_path=audio_path, language="zh-HK")
        except Exception as e:
            print(f"ASR 錯誤：{e}")
            transcription = ""
    else:
        print(f"音頻不存在：{audio_path}")

    # Step 2: 備用 DOCX
    if not transcription or len(transcription.strip()) < 50:
        print(f"使用備用 DOCX：{backup_docx}")
        if os.path.exists(backup_docx):
            text, error = read_docx(backup_docx)
            if not error:
                transcription = text
            else:
                print(f"DOCX 錯誤：{error}")
        else:
            print("備用檔案不存在")

    # 防呆
    if not transcription or len(transcription.strip()) == 0:
        return {
            "transcription": "錯誤：無法取得任何文字內容",
            "summaries": []
        }

    # Step 3: 生成總結
    summaries = []
    for model in MODELS:
        try:
            summary = summarize_text(transcription, model)
            summaries.append((model['name'], summary))
        except Exception as e:
            summaries.append((model['name'], f"錯誤：{str(e)}"))

    return {
        "transcription": transcription,
        "summaries": summaries
    }

# === 僅在直接執行時印出 ===
if __name__ == "__main__":
    result = generate_summary_data()
    print(f"完整轉錄：\n{result['transcription'][:200]}...\n")
    for name, summ in result['summaries']:
        print(f"{name} 總結：\n{summ}\n{'='*50}")
