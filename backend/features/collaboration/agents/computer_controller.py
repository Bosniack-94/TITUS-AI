from shared.base_agent import BaseAgent
from shared.config import Config
from features.action.tools.computer_tool import ComputerTool
from anthropic import Anthropic
import time
from typing import Optional


class ComputerController(BaseAgent):
    """
    TITUS Digital Sense: The Puppet Master.
    
    Refactored to Hexagonal Architecture: 
    - Logic: Claude Vision/Planning (Agent)
    - Infrastructure: OS Operations (ComputerTool)
    """

    # Tools declared for Claude Computer Use
    COMPUTER_TOOLS = [
        {
            "type": "computer_20241022",
            "name": "computer",
            "display_width_px": 1920,
            "display_height_px": 1080,
            "display_number": 1,
        }
    ]

    def initialize(self):
        print(f"[+] {self.name}: Initializing logic core & OS linkage...")
        self.client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.model = "claude-3-5-sonnet-20241022"  # Using Sonnet for real-time control
        self.max_iterations = 12
        
        # Configure tool safety
        ComputerTool.configure_safety()
        
        from features.action.bridge.connector import PsiquisBridge
        self.bridge = PsiquisBridge()
        self.status = "ACTIVE"
        self.bridge.sync_agent_status(self.agent_id, self.status, "OS control READY")

    def execute(self, task: dict) -> dict:
        """
        Main Computer Use loop using ComputerTool abstraction.
        """
        goal = task.get("goal", "Describe the screen.")
        
        print(f"[*] {self.name}: Executing OS task: '{goal}'")
        self.bridge.sync_agent_status(self.agent_id, "EXECUTING", f"Task: {goal[:30]}")

        messages = []
        iteration = 0
        final_result = "No conclusion reached."

        # Initial Screenshot
        screenshot_b64 = ComputerTool.capture_screenshot()
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": screenshot_b64
                    }
                },
                {"type": "text", "text": f"Your goal is: {goal}. Use the computer tool."}
            ]
        })

        while iteration < self.max_iterations:
            iteration += 1
            print(f"[*] {self.name}: Loop iteration {iteration}...")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                tools=self.COMPUTER_TOOLS,
                messages=messages,
                betas=["computer-use-2024-10-22"]
            )

            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "end_turn":
                for block in response.content:
                    if hasattr(block, "text"):
                        final_result = block.text
                print(f"[+] {self.name}: Goal achieved.")
                self.bridge.sync_agent_status(self.agent_id, "SUCCESS", "Task finished")
                break

            # Execute tool calls via ComputerTool
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    action_res = ComputerTool.execute_action(
                        block.input.get("action"), 
                        block.input
                    )
                    
                    # Refresh screenshot for Claude after action
                    new_screenshot = ComputerTool.capture_screenshot()
                    
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": new_screenshot
                                }
                            },
                            {"type": "text", "text": action_res}
                        ]
                    })

            if tool_results:
                messages.append({"role": "user", "content": tool_results})

        return {
            "status": "SUCCESS",
            "result": final_result
        }

    def shutdown(self):
        self.status = "OFFLINE"
