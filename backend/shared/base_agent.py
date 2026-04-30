from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """
    TITUS Base Agent Contract (The 'Lego' Stud).
    All agents in the TITUS system must inherit from this class.
    """

    def __init__(self, agent_id: str, name: str):
        self.agent_id = agent_id
        self.name = name
        self.status = "OFFLINE"

    @abstractmethod
    def initialize(self):
        """Initializes agent resources and connections."""
        pass

    @abstractmethod
    def execute(self, task: dict):
        """Executes a specific tactical task."""
        pass

    @abstractmethod
    def shutdown(self):
        """Safely shuts down the agent."""
        pass

    def get_status(self):
        """Returns the current status of the agent."""
        return {
            "id": self.agent_id,
            "name": self.name,
            "status": self.status
        }
