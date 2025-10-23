# ASR.py
# 重新生成：speech_recognition + Google API，分段處理長音頻。加錯誤處理，支援粵語。

import speech_recognition as sr
import wave
import os

def split_wav_to_chunks(audio_path, chunk_duration=20):  # 減到 20 秒，提高準度
    """
    分段 WAV 文件到 chunks。
    """
    chunks = []
    with wave.open(audio_path, 'rb') as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        chunk_length = int(chunk_duration * rate)
        
        for i in range(0, frames, chunk_length):
            wf.setpos(i)
            chunk_data = wf.readframes(min(chunk_length, frames - i))
            chunk_file = f"chunk_{len(chunks)}.wav"
            with wave.open(chunk_file, 'wb') as chunk_wf:
                chunk_wf.setparams(wf.getparams())
                chunk_wf.writeframes(chunk_data)
            chunks.append(chunk_file)
    
    return chunks

def transcribe_audio(audio_path=None, use_mic=False, language="zh-HK", chunk_duration=20):  # 改 zh-HK 支援粵語
    """
    轉錄音頻。長文件分段。
    """
    recognizer = sr.Recognizer()
    full_text = ""
    
    if use_mic:
        try:
            with sr.Microphone() as source:
                print("講野啦...（講完按 Enter）")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio, language=language)
            return text.strip()
        except sr.UnknownValueError:
            return "聽唔清，試下再嚟。"
        except sr.RequestError:
            return "網絡問題，檢查連接。"
        except Exception as e:
            return f"麥克風錯誤：{str(e)}"
    
    elif audio_path:
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"文件唔見：{audio_path}")
        
        file_size = os.path.getsize(audio_path)
        print(f"文件大小：{file_size / 1024 / 1024:.1f} MB")
        
        if file_size > 0.5 * 1024 * 1024:  # >0.5MB 分段
            print(f"自動分段（每 {chunk_duration} 秒一塊）...")
            chunks = split_wav_to_chunks(audio_path, chunk_duration)
        else:
            chunks = [audio_path]
        
        for idx, chunk in enumerate(chunks):
            try:
                with sr.AudioFile(chunk) as source:
                    audio = recognizer.record(source)
                text = recognizer.recognize_google(audio, language=language)
                full_text += f"[分段 {idx+1}] {text} "
                print(f"分段 {idx+1}: {text}")
            except sr.UnknownValueError:
                full_text += "[聽唔清] "
            except sr.RequestError:
                full_text += "[網絡問題] "
            except Exception as e:
                full_text += f"[錯誤: {str(e)}] "
        
        # 刪 chunks
        for chunk in chunks:
            if chunk != audio_path:
                try:
                    os.remove(chunk)
                except:
                    pass
        
        return full_text.strip()
    
    else:
        raise ValueError("要指定 audio_path 或 use_mic=True")

if __name__ == "__main__":
    print(transcribe_audio(audio_path="sample.wav", language="zh-HK"))
# ASR.py
# 使用 speech_recognition + Google API，分段處理長音頻。免費、無新下載。

import speech_recognition as sr
import wave
import os

def split_wav_to_chunks(audio_path, chunk_duration=30):
    """
    用純 Python wave 模塊，將 WAV 分成 chunk_duration 秒塊。
    Returns: list of chunk file paths.
    """
    chunks = []
    with wave.open(audio_path, 'rb') as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        chunk_length = int(chunk_duration * rate)
        
        for i in range(0, frames, chunk_length):
            wf.setpos(i)
            chunk_data = wf.readframes(min(chunk_length, frames - i))
            chunk_file = f"chunk_{len(chunks)}.wav"
            with wave.open(chunk_file, 'wb') as chunk_wf:
                chunk_wf.setparams(wf.getparams())
                chunk_wf.writeframes(chunk_data)
            chunks.append(chunk_file)
    
    return chunks

def transcribe_audio(audio_path=None, use_mic=False, language="zh-TW", chunk_duration=30):
    """
    轉錄音頻到文字。長文件自動分段。
    
    Args:
        audio_path (str): 音頻文件路徑（wav 格式）。
        use_mic (bool): 是否用麥克風（需 pyaudio）。
        language (str): 語言，如 "zh-TW"。
        chunk_duration (int): 分段秒數（預設 30 秒）。
    
    Returns:
        str: 完整轉錄文字。
    """
    recognizer = sr.Recognizer()
    full_text = ""
    
    if use_mic:
        with sr.Microphone() as source:
            print("講野啦...（講完按 Enter）")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio, language=language)
            return text.strip()
        except sr.UnknownValueError:
            return "聽唔清，試下再嚟。"
        except sr.RequestError:
            return "網絡問題，檢查連接。"
    
    elif audio_path:
        # 檢查文件大小，如果大過 1MB，分段
        file_size = os.path.getsize(audio_path)
        if file_size > 1 * 1024 * 1024:  # >1MB
            print(f"文件太大 ({file_size/1024/1024:.1f} MB)，自動分段...")
            chunks = split_wav_to_chunks(audio_path, chunk_duration)
        else:
            chunks = [audio_path]
        
        for chunk in chunks:
            with sr.AudioFile(chunk) as source:
                audio = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio, language=language)
                full_text += text + " "
                print(f"分段轉錄：{text}")
            except sr.UnknownValueError:
                full_text += "[聽唔清] "
            except sr.RequestError:
                full_text += "[網絡問題] "
        
        # 清潔 chunks
        for chunk in chunks:
            if chunk != audio_path:
                os.remove(chunk)
        
        return full_text.strip()
    
    else:
        raise ValueError("要指定 audio_path 或 use_mic=True")

# 測試用（用文件模式）
if __name__ == "__main__":
    print(transcribe_audio(audio_path="sample.wav", language="zh-TW"))
# ASR.py
# 使用 speech_recognition + Google Web Speech API 轉文字。免費、線上、無模型下載。

import speech_recognition as sr

def transcribe_audio(audio_path=None, use_mic=False, language="zh-TW"):  # zh-TW 為繁中，改成 "en-US" 為英文
    """
    轉錄音頻到文字。
    
    Args:
        audio_path (str): 音頻文件路徑（wav 格式最佳）。如果 None 且 use_mic=True，用麥克風。
        use_mic (bool): 是否用麥克風即時輸入。
        language (str): 語言代碼，如 "zh-TW" (繁中)、"en-US" (英文)。
    
    Returns:
        str: 轉錄文字。
    
    Raises:
        Exception: 如果錯誤。
    """
    recognizer = sr.Recognizer()
    
    if use_mic:
        with sr.Microphone() as source:
            print("講野啦...（講完按 Enter）")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
    elif audio_path:
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
    else:
        raise ValueError("要指定 audio_path 或 use_mic=True")
    
    try:
        # 用 Google Web Speech API 轉錄（免費、無 key）
        text = recognizer.recognize_google(audio, language=language)
        return text.strip()
    except sr.UnknownValueError:
        return "聽唔清，試下再嚟。"
    except sr.RequestError:
        return "網絡問題，檢查連接。"

# 測試用（可獨立跑）
if __name__ == "__main__":
    # 測試文件：transcribe_audio(audio_path="sample.wav")
   print(transcribe_audio(audio_path="sample.wav", language="zh-TW"))
