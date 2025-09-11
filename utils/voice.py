# utils/voice.py
import os
import tempfile
from config.config import OPENAI_API_KEY
# FIX: Import the OpenAI client
from openai import OpenAI

def transcribe_with_openai(file_bytes: bytes, filename: str = "audio.wav"):
    """
    Transcribe audio file using OpenAI Whisper API.
    Returns dict: {"text": "..."} or {"error": "..."}.
    """
    if not OPENAI_API_KEY:
        return {"error": "OPENAI_API_KEY missing."}
    try:
        # FIX: Instantiate the client with the API key
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # save temp file
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1] or ".wav")
        tmp.write(file_bytes)
        tmp.flush()
        tmp.close()
        
        with open(tmp.name, "rb") as fh:
            # FIX: Use the modern client method for transcriptions
            resp = client.audio.transcriptions.create(model="whisper-1", file=fh)
            text = resp.text
            
        try:
            os.unlink(tmp.name)
        except Exception:
            pass
        return {"text": text}
    except Exception as e:
        return {"error": str(e)}
