from shared.base_agent import BaseAgent
import time

class ScannerAgent(BaseAgent):
    """
    TITUS Tactical Agent: Data Scanner.
    Simulates a non-invasive tool that scans for specific patterns.
    """

    def initialize(self):
        print(f"[+] {self.name}: Initializing sensors and bridge...")
        # Import bridge dynamically to avoid circular dependencies if any
        from features.action.bridge.connector import PsiquisBridge
        self.bridge = PsiquisBridge()
        self.status = "ACTIVE"
        self.bridge.sync_agent_status(self.agent_id, self.status, "Sensors online")
        time.sleep(0.5)

    def execute(self, task: dict):
        target = task.get("target", "unknown")
        print(f"[*] {self.name}: Scanning target '{target}' for threats...")
        
        # Report progress to Psiquis Bridge
        self.bridge.sync_agent_status(self.agent_id, "EXECUTING", f"Scanning {target}")
        
        # Simulate work
        time.sleep(1)
        result = {
            "agent": self.name,
            "status": "SUCCESS",
            "findings": ["No threats detected", "Syncing with Psiquis-X via TITUS Bridge"]
        }
        
        # Final update
        self.bridge.sync_agent_status(self.agent_id, "SUCCESS", "Scan complete")
        return result

    def shutdown(self):
        print(f"[-] {self.name}: Shutting down sensors...")
        self.status = "OFFLINE"
