"""
Text-to-Speech Audio Guide generator for SchemeSaathi using gTTS.
"""
import io
import re
from gtts import gTTS

def generate_speech_audio(text: str, language: str = "English") -> bytes:
    """Converts plain text explanation to MP3 audio bytes using gTTS."""
    # Clean markdown formatting tags for audio readability
    clean_text = re.sub(r"[\*#_`~]", "", text)
    clean_text = clean_text[:800]  # Limit length for fast audio generation

    is_hindi = str(language).lower() in ["hi", "hindi"]
    lang_code = "hi" if is_hindi else "en"

    tts = gTTS(text=clean_text, lang=lang_code, slow=False)
    buffer = io.BytesIO()
    tts.write_to_fp(buffer)
    buffer.seek(0)
    return buffer.getvalue()

if __name__ == "__main__":
    audio = generate_speech_audio("PM-KISAN scheme gives 6000 rupees per year to farmers.", language="English")
    print(f"Generated Audio bytes length: {len(audio)}")
