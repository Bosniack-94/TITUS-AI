import os
import importlib.util
import inspect
import json
from typing import Dict, List
from shared.base_agent import BaseAgent
from shared.config import Config
from shared.schemas import AutonomousPlan, TaskStep


class TITUSOrchestrator:
    """
    The 'Baseplate' of TITUS.
    Dynamic agent lifecycle management and strategic execution.
    """

    def __init__(self, agents_path: str = None):
        self.agents_path = agents_path or Config.AGENTS_PATH
        self.active_agents: Dict[str, BaseAgent] = {}

    def discover_agents(self):
        """Scans the agents directory and loads all valid TITUS agents."""
        print(f"[*] TITUS: Scanning for agents in '{self.agents_path}'...")
        if not os.path.exists(self.agents_path):
            print(f"[!] Error: Agents directory '{self.agents_path}' not found.")
            return

        for filename in os.listdir(self.agents_path):
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = filename[:-3]
                file_path = os.path.join(self.agents_path, filename)
                self._load_agent(module_name, file_path)

    def _load_agent(self, module_name: str, file_path: str):
        """Dynamically loads a Python module and finds the BaseAgent subclass."""
        try:
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, BaseAgent) and obj is not BaseAgent:
                    # Map the internal agent ID to its module name for easy lookup
                    agent_instance = obj(agent_id=module_name, name=name)
                    print(f"[+] TITUS: Registered agent '{name}' as '{module_name}'")
                    self.active_agents[module_name] = agent_instance
                    return
        except Exception as e:
            print(f"[!] TITUS: Failed to load agent {module_name}: {e}")

    def initialize_all(self):
        """Initializes all discovered agents."""
        for agent in self.active_agents.values():
            try:
                agent.initialize()
                agent.status = "READY"
            except Exception as e:
                print(f"[!] TITUS: Error initializing {agent.name}: {e}")
                agent.status = "ERROR"

    async def execute_strategic_plan(self, plan: AutonomousPlan) -> List[dict]:
        """
        Executes a pre-formulated strategic plan step-by-step.
        """
        print(f"[*] TITUS Orchestrator: Executing strategic plan for goal: '{plan.goal}'")
        results = []

        for step in plan.steps:
            # Map agent_id carefully (lowercase vs class name)
            # In our system, agent_id in dispatch_task refers to the module name (e.g. 'executor_agent')
            agent_key = step.agent_id.lower()
            
            # Handling potential uppercase IDs from Brain
            if agent_key not in self.active_agents:
                # Try finding by class name or substring
                for key in self.active_agents.keys():
                    if key in agent_key or agent_key in key:
                        agent_key = key
                        break

            if agent_key in self.active_agents:
                print(f"[*] TITUS: Dispatching step '{step.action}' to {agent_key}")
                try:
                    res = self.active_agents[agent_key].execute({
                        "action": step.action,
                        **step.params
                    })
                    results.append(res)
                except Exception as e:
                    print(f"[!] TITUS: Step execution failed at {agent_key}: {e}")
                    results.append({"status": "ERROR", "msg": str(e)})
            else:
                print(f"[!] TITUS: Target agent '{step.agent_id}' not found in active registry.")

        return results

    def shutdown_all(self):
        """Safely shuts down all agents."""
        for agent in self.active_agents.values():
            agent.shutdown()
            agent.status = "OFFLINE"
        print("[*] TITUS: All agents deactivated.")
