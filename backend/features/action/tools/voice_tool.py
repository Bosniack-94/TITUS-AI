import pyttsx3

class VoiceTool:
    """
    Infrastructure Adapter for Vocal Synthesis.
    Encapsulates the hardware TTS engine.
    """
    
    _engine = None

    @classmethod
    def _get_engine(cls):
        if cls._engine is None:
            try:
                cls._engine = pyttsx3.init()
                cls._engine.setProperty('rate', 175)
                cls._engine.setProperty('volume', 1.0)
            except Exception as e:
                print(f"[!] VoiceTool: Hardware Error: {e}")
                return None
        return cls._engine

    @classmethod
    def speak(cls, text: str) -> bool:
        """Executes Text-to-Speech synchronously."""
        engine = cls._get_engine()
        if engine:
            try:
                engine.say(text)
                engine.runAndWait()
                return True
            except Exception as e:
                print(f"[!] VoiceTool: Playback Error: {e}")
                return False
        return False
