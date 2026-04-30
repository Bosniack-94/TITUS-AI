import requests
from .env_mock.state_manager import PsiquisStateManagerMock

class PsiquisBridge:
    """
    The TITUS Bridge to Psiquis-X.
    Uses non-invasive protocols (API/DB) to interact with the host system.
    """
    def __init__(self, api_url="http://localhost:8001"):
        self.api_url = api_url
        self.state_mock = PsiquisStateManagerMock()

    def sync_agent_status(self, agent_id, status, thought="No thought"):
        """Sends TITUS agent status to Psiquis telemetry."""
        payload = {
            "agent_id": f"TITUS_{agent_id}",
            "message": f"Status Update: {status} | Thought: {thought}",
            "level": "DEBUG"
        }
        try:
            # Try to push to API
            requests.post(f"{self.api_url}/telemetry", json=payload, timeout=2)
            # Log to Mock DB as well
            self.state_mock.update_agent(f"TITUS_{agent_id}", thought, 0, status)
            return True
        except Exception as e:
            print(f"[!] Bridge Error: Could not reach Psiquis API: {e}")
            return False
