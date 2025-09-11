# utils/voice_tts.py
from gtts import gTTS
import tempfile

def synthesize_text_to_mp3(text: str, lang: str = "en") -> str:
    """
    Convert text to speech using gTTS and return path to generated MP3 file.
    """
    try:
        tts = gTTS(text=text, lang=lang)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tmp_path = tmp.name
        tmp.close()
        tts.save(tmp_path)
        return tmp_path
    except Exception as e:
        raise RuntimeError(f"TTS synthesis failed: {e}")
