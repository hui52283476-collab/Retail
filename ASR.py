# ASR.py
# Speech recognition with Google API, chunking for long audio, Cantonese support. Added debug prints.

import speech_recognition as sr
import wave
import os

def split_wav_to_chunks(audio_path, chunk_duration=20):
    """
    Split WAV file into chunks.
    """
    print(f"Debug: Splitting {audio_path} into {chunk_duration}s chunks...")
    chunks = []
    try:
        with wave.open(audio_path, 'rb') as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            chunk_length = int(chunk_duration * rate)
            print(f"Debug: Frames: {frames}, Rate: {rate}, Chunk length: {chunk_length}")
            
            for i in range(0, frames, chunk_length):
                wf.setpos(i)
                chunk_data = wf.readframes(min(chunk_length, frames - i))
                chunk_file = f"chunk_{len(chunks)}.wav"
                with wave.open(chunk_file, 'wb') as chunk_wf:
                    chunk_wf.setparams(wf.getparams())
                    chunk_wf.writeframes(chunk_data)
                chunks.append(chunk_file)
                print(f"Debug: Created chunk {len(chunks)}")
        
        print(f"Debug: Created {len(chunks)} chunks.")
        return chunks
    except wave.Error as e:
        print(f"Debug: Wave error in split: {e}")
        raise

def transcribe_audio(audio_path=None, use_mic=False, language="zh-HK", chunk_duration=20):
    """
    Transcribe audio to text. Splits long files.
    """
    print("Debug: Starting transcription...")
    recognizer = sr.Recognizer()
    full_text = ""
    
    if use_mic:
        try:
            print("Debug: Using microphone...")
            with sr.Microphone() as source:
                print("Speak now... (press Enter when done)")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio, language=language)
            return text.strip()
        except sr.UnknownValueError:
            return "Could not understand audio, try again."
        except sr.RequestError:
            return "Network issue, check connection."
        except Exception as e:
            return f"Microphone error: {str(e)}"
    
    elif audio_path:
        print(f"Debug: Audio path = {audio_path}")
        if not os.path.exists(audio_path):
            print(f"Debug: File not found! {audio_path}")
            raise FileNotFoundError(f"File not found: {audio_path}")
        
        file_size = os.path.getsize(audio_path)
        print(f"File size: {file_size / 1024 / 1024:.1f} MB")
        
        if file_size > 0.5 * 1024 * 1024:
            print(f"Auto-splitting (every {chunk_duration} seconds)...")
            chunks = split_wav_to_chunks(audio_path, chunk_duration)
        else:
            chunks = [audio_path]
            print("Debug: No splitting needed.")
        
        for idx, chunk in enumerate(chunks):
            try:
                print(f"Debug: Processing chunk {idx+1}/{len(chunks)}")
                with sr.AudioFile(chunk) as source:
                    audio = recognizer.record(source)
                text = recognizer.recognize_google(audio, language=language)
                full_text += f"[Segment {idx+1}] {text} "
                print(f"Segment {idx+1}: {text}")
            except sr.UnknownValueError:
                full_text += "[Unclear] "
                print(f"Debug: Unclear for segment {idx+1}")
            except sr.RequestError:
                full_text += "[Network issue] "
                print(f"Debug: Network issue for segment {idx+1}")
            except Exception as e:
                full_text += f"[Error: {str(e)}] "
                print(f"Debug: Error for segment {idx+1}: {e}")
        
        # Clean up chunks
        for chunk in chunks:
            if chunk != audio_path:
                try:
                    os.remove(chunk)
                    print(f"Debug: Deleted {chunk}")
                except:
                    pass
        
        print("Debug: Transcription complete.")
        return full_text.strip()
    
    else:
        raise ValueError("Specify audio_path or use_mic=True")

if __name__ == "__main__":
    print(transcribe_audio(audio_path="sample.wav", language="zh-HK"))
