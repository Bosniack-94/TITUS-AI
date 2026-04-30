from shared.base_agent import BaseAgent
from features.action.tools.travel_tool import TravelTool
import time

class TravelAgent(BaseAgent):
    """
    TITUS Digital Sense: The Concierge.
    
    Specialized in searching for flights, hotels, and travel options.
    Returns structured JSON for user approval.
    """

    def initialize(self):
        print(f"[+] {self.name}: Calibrating flight paths & global search engines...")
        from features.action.bridge.connector import PsiquisBridge
        self.bridge = PsiquisBridge()
        self.status = "ACTIVE"
        self.bridge.sync_agent_status(self.agent_id, self.status, "Travel Intelligence READY")

    def execute(self, task: dict) -> dict:
        action = task.get("action", "SEARCH_FLIGHTS")
        origin = task.get("origin")
        destination = task.get("destination")
        date = task.get("date")

        print(f"[*] {self.name}: Iniciando misión de investigación: {origin} -> {destination}")
        self.bridge.sync_agent_status(self.agent_id, "RESEARCHING", f"Buscando vuelos para {destination}")

        if action == "SEARCH_FLIGHTS":
            # Call Infrastructure Tool
            res = TravelTool.search_vuelos(origin, destination, date)
            
            if res["status"] == "SUCCESS":
                count = len(res.get("listings", []))
                self.bridge.sync_agent_status(self.agent_id, "SUCCESS", f"Encontradas {count} opciones de viaje.")
                return {
                    "agent": self.name,
                    "status": "SUCCESS",
                    "data": res
                }
            else:
                self.bridge.sync_agent_status(self.agent_id, "ERROR", res.get("msg", "Error desconocido"))
                return {
                    "agent": self.name,
                    "status": "ERROR",
                    "msg": res.get("msg")
                }

        return {"status": "UNKNOWN_ACTION"}

    def shutdown(self):
        print(f"[-] {self.name}: Parking concierge services.")
        self.status = "OFFLINE"
