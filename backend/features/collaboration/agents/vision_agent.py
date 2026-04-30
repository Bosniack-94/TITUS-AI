from shared.base_agent import BaseAgent
import time

class VisionAgent(BaseAgent):
    """
    TITUS Digital Sense: The Eyes.
    Agent focused on visual interpretation and pattern recognition.
    """

    def initialize(self):
        print(f"[+] {self.name}: Calibrating optical sensors...")
        from features.action.bridge.connector import PsiquisBridge
        self.bridge = PsiquisBridge()
        self.status = "ACTIVE"
        self.bridge.sync_agent_status(self.agent_id, self.status, "Optical feedback READY")
        time.sleep(0.5)

    def execute(self, task: dict):
        image_path = task.get("image_path", "N/A")
        print(f"[*] {self.name}: Analyzing visual input at '{image_path}'...")
        
        # 1. Hallucination Guard (Skepticism Layer)
        image_quality = task.get("quality", "HIGH")
        if image_quality == "LOW":
            self.bridge.sync_agent_status(self.agent_id, "LIMITATION", "Visual input too blurry. Analysis aborted to prevent hallucination.")
            return {
                "agent": self.name,
                "status": "ABORTED",
                "reason": "Low image quality detected. Please provide a clearer visual source."
            }

        # 2. Report "Seeing" state to bridge
        self.bridge.sync_agent_status(self.agent_id, "ANALYZING", f"Interpreting {image_path}")
        
        # Simulate Vision Processing
        time.sleep(1.5)
        
        # Mocking real-world discovery
        result = {
            "agent": self.name,
            "analysis": "High-fidelity match found. UI contains 4 active modules.",
            "objects_detected": ["Dashboard Frame", "Telemetry Widget", "Neon Border"],
            "status": "SUCCESS"
        }
        
        self.bridge.sync_agent_status(self.agent_id, "SUCCESS", "Visual analysis complete")
        return result

    def shutdown(self):
        print(f"[-] {self.name}: Deactivating optical sensors...")
        self.status = "OFFLINE"
