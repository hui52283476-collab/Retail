import os
from ASR import transcribe_audio
from summarizer import summarize_text, MODELS, read_docx  # Add read_docx for backup

def main(audio_path="sample.wav", backup_docx="scrip.docx", output_file="output.txt"):
    """
    主流程：轉錄音頻並總結，或喺轉錄失敗時用備份 DOCX 檔案總結。
    
    Args:
        audio_path (str): WAV 音頻檔案路徑。
        backup_docx (str): 備份 DOCX 檔案路徑。
        output_file (str): 儲存轉錄同總結嘅輸出檔案。
    """
    # Step 1: 檢查音頻檔案
    if not os.path.exists(audio_path):
        print(f"錯誤：音頻檔案 '{audio_path}' 唔存在。用備份 DOCX...")
        text, error = read_docx(backup_docx)
        if error:
            print(f"讀取備份錯誤：{error}")
            return
        transcription = text
    else:
        # Step 2: 嘗試轉錄
        print(f"開始轉錄 {audio_path}...")
        try:
            transcription = transcribe_audio(audio_path=audio_path, language="zh-HK")
            
            # 檢查轉錄是否失敗
            if "[聽唔清]" in transcription or "[網絡問題]" in transcription:
                print("轉錄失敗，用備份 DOCX...")
                text, error = read_docx(backup_docx)
                if error:
                    print(f"讀取備份錯誤：{error}")
                    return
                transcription = text
            else:
                print("轉錄成功！")
                
        except Exception as e:
            print(f"轉錄錯誤：{str(e)}，用備份 DOCX...")
            text, error = read_docx(backup_docx)
            if error:
                print(f"讀取備份錯誤：{error}")
                return
            transcription = text
    
    # Step 3: 用兩個模型總結
    print("\n生成總結...")
    summaries = []
    for model in MODELS:
        print(f"\n⏳ 用 {model['name']} 生成總結...")
        try:
            summary = summarize_text(transcription, model)
            summaries.append((model['name'], summary))
            print(f"\n📄 {model['name']} 總結")
            print("=" * 50)
            print(summary)
            print(f"📏 字數：{len(summary.split())}")
            print("=" * 50)
        except Exception as e:
            print(f"{model['name']} 總結錯誤：{str(e)}")
            summaries.append((model['name'], f"生成總結失敗：{str(e)}"))
    
    # Step 4: 儲存結果
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"完整轉錄：\n{transcription}\n\n")
        for model_name, summary in summaries:
            f.write(f"{model_name} 總結：\n{summary}\n\n")
    print(f"\n結果已儲存到 {output_file}")

if __name__ == "__main__":
    main()
