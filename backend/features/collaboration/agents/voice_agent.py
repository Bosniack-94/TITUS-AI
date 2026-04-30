from shared.base_agent import BaseAgent
from features.action.tools.voice_tool import VoiceTool
import time

class VoiceAgent(BaseAgent):
    """
    TITUS Digital Sense: The Voice.
    
    Refactored to Hexagonal Architecture:
    - Logic: Vocal feedback orchestration.
    - Infrastructure: Hardware TTS (VoiceTool).
    """

    def initialize(self):
        print(f"[+] {self.name}: Calibrating vocal drivers & hardware link...")
        from features.action.bridge.connector import PsiquisBridge
        self.bridge = PsiquisBridge()
        self.status = "ACTIVE"
        self.bridge.sync_agent_status(self.agent_id, self.status, "Vocal synthesis ACTIVE")

    def execute(self, task: dict):
        action = task.get("action", "SAY")
        
        if action == "SAY":
            text = task.get("text", "Sistemas operativos, Señor.")
            print(f"[*] {self.name}: Emitiendo reporte vocal...")
            self.bridge.sync_agent_status(self.agent_id, "RESPONDING", f"Speaking: {text[:15]}...")
            
            # Use Infrastructure Tool
            success = VoiceTool.speak(text)
            
            if success:
                self.bridge.sync_agent_status(self.agent_id, "SUCCESS", "Speech emitted")
                return {"status": "SUCCESS"}
            else:
                self.bridge.sync_agent_status(self.agent_id, "ERROR", "Hardware failure")
                return {"status": "ERROR"}

        return {"status": "UNKNOWN_ACTION"}

    def shutdown(self):
        self.status = "OFFLINE"
