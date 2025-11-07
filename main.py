import os
from ASR import transcribe_audio
from summarizer import summarize_text, MODELS, read_docx

def main(audio_path="sample.wav", backup_docx="scrip.docx", output_file="output.txt"):
    print(f"開始處理音頻：{audio_path}")
    
    # Step 1: 轉錄音頻
    transcription = ""
    if os.path.exists(audio_path):
        print(f"發現音頻，開始轉錄...")
        try:
            transcription = transcribe_audio(audio_path=audio_path, language="zh-HK")
            print(f"原始轉錄結果（前200字）：\n{transcription[:200]}")
            print(f"轉錄總長度：{len(transcription)} 字")
        except Exception as e:
            print(f"轉錄錯誤：{e}")
            transcription = ""
    else:
        print(f"音頻檔案唔存在：{audio_path}")

    # Step 2: 如果轉錄失敗，用備份 DOCX
    if not transcription or len(transcription.strip()) < 50:
        print(f"轉錄太短或失敗，改用備份 DOCX：{backup_docx}")
        if not os.path.exists(backup_docx):
            print(f"備份檔案唔存在！")
            return
        text, error = read_docx(backup_docx)
        if error:
            print(f"讀取 DOCX 失敗：{error}")
            return
        transcription = text
        print(f"DOCX 讀取成功，長度：{len(transcription)} 字")

    # 防呆：確保有文字
    if len(transcription.strip()) == 0:
        print("錯誤：最終文字為空，無法總結！")
        return

    # Step 3: 生成總結（加除錯）
    print("\n開始生成總結...")
    summaries = []
    for model in MODELS:
        print(f"\n用 {model['name']} 生成總結...")
        try:
            summary = summarize_text(transcription, model)
            summaries.append((model['name'], summary))
            print(f"{model['name']} 總結")
            print("="*50)
            print(summary)
            print(f"字數：{len(summary.split())}")
            print("="*50)
        except Exception as e:
            print(f"{model['name']} 總結錯誤：{str(e)}")

    # Step 4: 儲存結果
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"完整轉錄：\n{transcription}\n\n")
        for name, summ in summaries:
            f.write(f"{name} 總結：\n{summ}\n\n")
    print(f"\n結果已儲存到 {output_file}")

if __name__ == "__main__":
    main()
