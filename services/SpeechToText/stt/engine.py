# stt/engine.py
from pathlib import Path
from pydub import AudioSegment
import speech_recognition as sr
import os

def _convert_to_wav(file_path: str) -> str:
    """
    Convert any supported audio file to WAV format for STT processing.
    Supports webm, mp3, m4a, ogg, wav, etc.
    """
    path = Path(file_path)
    if path.suffix.lower() == ".wav":
        return str(path)

    audio = AudioSegment.from_file(path)
    wav_path = path.with_suffix(".wav")

    # Convert to mono, 16kHz for best STT performance
    audio = audio.set_frame_rate(16000).set_channels(1)
    audio.export(wav_path, format="wav")

    return str(wav_path)


def transcribe_audio(audio_path: str) -> dict:
    """Transcribe speech using Google Speech-to-Text."""
    recognizer = sr.Recognizer()
    wav_path = _convert_to_wav(audio_path)

    with sr.AudioFile(wav_path) as source:
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio)
        return {"text": text, "engine": "google"}
    except sr.UnknownValueError:
        return {"error": "Could not understand the audio", "engine": "google"}
    except sr.RequestError as e:
        return {"error": f"Google API error: {e}", "engine": "google"}
    finally:
        # Clean up temporary WAV file if conversion happened
        if wav_path != audio_path and os.path.exists(wav_path):
            os.remove(wav_path)
