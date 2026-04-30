import speech_recognition as sr
from typing import Optional


class AudioTool:
    """
    Infrastructure Adapter for Audio Input.
    Captures real audio from the microphone and converts it to text
    using Google's Speech Recognition service (no API key required for basic use).
    
    Future: Swap recognizer for OpenAI Realtime or Gemini Live Audio.
    """

    _recognizer: sr.Recognizer = None
    _microphone: sr.Microphone = None

    @classmethod
    def _get_engine(cls):
        if cls._recognizer is None:
            cls._recognizer = sr.Recognizer()
            cls._recognizer.energy_threshold = 4000
            cls._recognizer.pause_threshold = 0.8
        if cls._microphone is None:
            try:
                cls._microphone = sr.Microphone()
            except Exception as e:
                print(f"[!] AudioTool: No se pudo inicializar el micrófono (PyAudio missing): {e}")
                cls._microphone = None
        return cls._recognizer, cls._microphone

    @classmethod
    def calibrate(cls):
        """
        Calibrates the microphone against ambient noise.
        Should be called once during initialization.
        """
        recognizer, mic = cls._get_engine()
        if not mic:
            print("[!] AudioTool: No se puede calibrar; micrófono no disponible.")
            return

        print("[*] AudioTool: Calibrating against ambient noise (1 second)...")
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
        print("[+] AudioTool: Calibration complete.")

    @classmethod
    def listen(cls, timeout: int = 5, phrase_time_limit: int = 10) -> Optional[str]:
        """
        Listens for a spoken command and returns the transcribed text.
        """
        recognizer, mic = cls._get_engine()
        
        if not mic:
            print("[!] AudioTool: No se puede escuchar; micrófono no disponible.")
            return None

        print("[*] AudioTool: Listening for command...")

        try:
            with mic as source:
                audio = recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )

            # Primary: Google Web Speech (free, no key needed)
            text = recognizer.recognize_google(audio, language="es-MX")
            print(f"[+] AudioTool: Captured → '{text}'")
            return text

        except sr.WaitTimeoutError:
            print("[!] AudioTool: No speech detected within timeout.")
            return None
        except sr.UnknownValueError:
            print("[!] AudioTool: Speech was heard but could not be understood.")
            return None
        except sr.RequestError as e:
            print(f"[!] AudioTool: Speech recognition service error: {e}")
            return None
