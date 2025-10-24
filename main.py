import os
from summarizer import read_docx, summarize_text, MODELS

def main(docx_file="scrip.docx", output_file="output.txt"):
    """
    主流程：從 DOCX 檔案讀取內容並生成總結，儲存到輸出檔案。
    
    Args:
        docx_file (str): DOCX 檔案路徑。
        output_file (str): 儲存總結嘅輸出檔案。
    """
    # Step 1: 檢查 DOCX 檔案
    if not os.path.exists(docx_file):
        print(f"錯誤：DOCX 檔案 '{docx_file}' 唔存在。")
        return
    
    # Step 2: 讀取 DOCX 內容
    print(f"開始讀取 {docx_file}...")
    text, error = read_docx(docx_file)
    if error:
        print(error)
        return
    
    print(f"\n📄 提取文字總字符數：{len(text)}")
    
    # Step 3: 用兩個模型生成總結
    print("\n生成總結...")
    summaries = []
    for model in MODELS:
        print(f"\n⏳ 用 {model['name']} 生成總結...")
        try:
            summary = summarize_text(text, model)
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
        f.write("原始文字：\n")

if __name__ == "__main__":
    main()
