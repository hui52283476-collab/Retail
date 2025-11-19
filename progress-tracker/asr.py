import speech_recognition as sr
import wave
import os

def split_wav_to_chunks(audio_path, chunk_duration=30):
    """
    用純 Python wave 模塊，將 WAV 分成 chunk_duration 秒塊。
    Returns: list of chunk file paths.
    """
    chunks = []
    try:
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
    except wave.Error as e:
        print(f"Wave error in split: {e}")
        raise


def transcribe_audio(audio_path=None, language="zh-TW", chunk_duration=30):
    """
    轉錄音頻到文字。只支援文件，不支援麥克風。
    Args:
        audio_path (str): 音頻文件路徑（wav 格式）。
        language (str): 語言，如 "zh-TW"。
        chunk_duration (int): 分段秒數（預設 30 秒）。
    Returns:
        str: 完整轉錄文字。
    """
    if not audio_path or not os.path.exists(audio_path):
        raise FileNotFoundError(f"文件唔見：{audio_path}")

    recognizer = sr.Recognizer()
    full_text = ""

    file_size = os.path.getsize(audio_path)
    print(f"文件大小：{file_size / 1024 / 1024:.1f} MB")

    if file_size > 1 * 1024 * 1024:  # >1MB 分段
        print(f"文件太大，自動分段（每 {chunk_duration} 秒一塊）...")
        chunks = split_wav_to_chunks(audio_path, chunk_duration)
    else:
        chunks = [audio_path]

    for idx, chunk in enumerate(chunks):
        try:
            with sr.AudioFile(chunk) as source:
                audio = recognizer.record(source)
            text = recognizer.recognize_google(audio, language=language)
            full_text += text + " "
            print(f"分段轉錄：{text}")
        except sr.UnknownValueError:
            full_text += "[聽唔清] "
            print(f"分段 {idx+1} 聽唔清")
        except sr.RequestError as e:
            full_text += "[網絡問題] "
            print(f"網絡錯誤: {e}")

    # 刪除臨時 chunks
    for chunk in chunks:
        if chunk != audio_path:
            try:
                os.remove(chunk)
            except:
                pass

    return full_text.strip()


# 測試用
if __name__ == "__main__":
    print(transcribe_audio(audio_path="sample.wav", language="zh-TW"))
