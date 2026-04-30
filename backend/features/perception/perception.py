"""
TITUS Perception Manager
========================
Central coordinator for all sensory input to the TITUS system.

Follows Hexagonal Architecture:
  - Delegatess Vision capture → VisionTool
  - Delegates Audio capture  → AudioTool
  - Delegates Voice output   → VoiceTool

This class is the only entry point for Perception in the entire system.
No agent or orchestrator should import AudioTool or VisionTool directly.
"""

from features.action.tools.vision_tool import VisionTool
from features.action.tools.audio_tool import AudioTool
from features.action.tools.voice_tool import VoiceTool
from typing import Optional
import threading
import time


class PerceptionManager:
    """
    TITUS Perception Layer.
    Unifies Vision (Gemini Multimodal) and Audio (microphone STT)
    into a single, clean interface.
    """

    def __init__(self):
        self._is_active: bool = False
        self._screen_context: str = ""
        self._passive_vision_thread: Optional[threading.Thread] = None
        self._vision_interval: int = 5  # Seconds between passive screen reads
        print("[+] PerceptionManager: Initializing sensory systems...")

    # -------------------------------------------------------------------------
    # PUBLIC API
    # -------------------------------------------------------------------------

    def startup(self):
        """
        Activates all sensory channels.
        NOTE: Passive vision loop is DISABLED to prevent API quota exhaustion on startup.
        Call analyze_screen() on-demand instead.
        """
        print("[*] PerceptionManager: Starting sensory channels...")
        AudioTool.calibrate()
        self._is_active = True
        # Passive vision intentionally disabled — call analyze_screen() on demand
        # self._start_passive_vision()
        print("[+] PerceptionManager: All senses are ONLINE.")

    def shutdown(self):
        """Gracefully shuts down all sensory channels."""
        self._is_active = False
        if self._passive_vision_thread and self._passive_vision_thread.is_alive():
            self._passive_vision_thread.join(timeout=3)
        print("[-] PerceptionManager: Senses OFFLINE.")

    def listen_for_command(self, timeout: int = 7) -> Optional[str]:
        """
        Listens via microphone and returns the spoken command as text.
        Returns None if no speech is detected.
        """
        return AudioTool.listen(timeout=timeout)

    def analyze_screen(self, context_query: str = "What is the user currently doing on screen?") -> str:
        """
        Takes a real screenshot and returns Gemini's analysis in natural language.
        """
        return VisionTool.analyze_frame(context_query)

    def get_current_screen_context(self) -> str:
        """
        Returns the latest passive screen analysis (collected in the background loop).
        Does not block. Returns the most recent cached context.
        """
        return self._screen_context or "Screen context not yet available."

    def perceive(self) -> dict:
        """
        Full active perception cycle: listens to voice and analyzes screen simultaneously.
        Returns a unified Perception Report.
        """
        print("[*] PerceptionManager: Full perception cycle initiated...")

        # Kick off screen analysis in parallel with audio capture
        screen_result = {"text": ""}
        def analyze():
            screen_result["text"] = VisionTool.analyze_frame(
                "Describe in detail what is visible on the screen. Focus on active windows and content."
            )

        vision_thread = threading.Thread(target=analyze, daemon=True)
        vision_thread.start()

        # Capture voice in the main thread
        voice_command = AudioTool.listen(timeout=6)

        # Wait for vision to complete (max 10s)
        vision_thread.join(timeout=10)

        return {
            "voice_command": voice_command,
            "screen_context": screen_result["text"],
            "perception_complete": True
        }

    # -------------------------------------------------------------------------
    # INTERNAL
    # -------------------------------------------------------------------------

    def _start_passive_vision(self):
        """
        Starts a background daemon thread that periodically analyzes the screen.
        Keeps self._screen_context updated without blocking the main loop.
        """
        def vision_loop():
            print("[*] PerceptionManager: Passive vision loop started.")
            while self._is_active:
                try:
                    self._screen_context = VisionTool.analyze_frame(
                        "In one sentence, describe the primary task the user is currently performing."
                    )
                except Exception as e:
                    print(f"[!] PerceptionManager: Vision loop error: {e}")
                time.sleep(self._vision_interval)

        self._passive_vision_thread = threading.Thread(
            target=vision_loop, daemon=True, name="TITUS_PassiveVision"
        )
        self._passive_vision_thread.start()
