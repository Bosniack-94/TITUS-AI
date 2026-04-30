import io
import base64
from PIL import ImageGrab
from google import genai
from google.genai import types
from shared.config import Config


class VisionTool:
    """
    Infrastructure Adapter for Vision Analysis.
    Captures real screenshots and sends them to Gemini Vision for analysis.
    """

    _client: genai.Client = None

    @classmethod
    def _get_client(cls) -> genai.Client:
        if cls._client is None:
            cls._client = genai.Client(api_key=Config.GOOGLE_API_KEY)
        return cls._client

    @staticmethod
    def capture_frame_b64() -> tuple[bytes, str]:
        """
        Captures the current screen.
        Returns: (raw_bytes, base64_encoded_string)
        """
        screenshot = ImageGrab.grab()
        buffer = io.BytesIO()
        screenshot.save(buffer, format="PNG")
        raw = buffer.getvalue()
        b64 = base64.standard_b64encode(raw).decode("utf-8")
        return raw, b64

    @classmethod
    def analyze_frame(cls, context_goal: str = "Describe what is on screen.") -> str:
        """
        Captures the screen and asks Gemini to analyze it contextually.
        Returns a natural language description of the visual state.
        """
        client = cls._get_client()
        raw_bytes, _ = cls.capture_frame_b64()

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                types.Part.from_bytes(data=raw_bytes, mime_type="image/png"),
                types.Part.from_text(text=f"You are TITUS's visual cortex. {context_goal}")
            ]
        )
        return response.text
