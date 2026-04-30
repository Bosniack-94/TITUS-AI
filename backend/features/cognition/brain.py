import json
from shared.config import Config
from shared.schemas import AutonomousPlan, UserIntent, PerceptionReport, TaskStep
from google import genai as google_genai
from anthropic import Anthropic
from typing import Tuple


class TITUSBrain:
    """
    The Dual-LLM Logic Core (Unified version).
    
    Orchestrates high-level strategy and tactical execution steps.
    - Vision context is injected into every thought.
    - Output is strictly validated against TITUS Schemas.
    """

    def __init__(self):
        self.gemini_client = google_genai.Client(api_key=Config.GOOGLE_API_KEY)
        self.claude = Anthropic(api_key=Config.ANTHROPIC_API_KEY)

    def formulate_plan(self, goal: str, perception: PerceptionReport) -> AutonomousPlan:
        """
        Main Strategy Layer.
        Uses Gemini 2.0 Flash (fast/vision-aware) to create a multi-step execution plan.
        """
        system_prompt = f"""
        You are the TITUS Strategic Core. 
        CURRENT CONTEXT (What you see on screen): {perception.screen_summary}
        
        GOAL: {goal}
        
        Respond ONLY with a valid JSON object matching this structure:
        {{
            "goal": "string",
            "intent": {{
                "action_type": "buy|research|design|control|social",
                "parameters": {{}},
                "voice_preference": true
            }},
            "steps": [
                {{"agent_id": "EXECUTOR_AGENT", "action": "cmd", "params": {{}}}},
                {{"agent_id": "TRAVEL_AGENT", "action": "SEARCH_FLIGHTS", "params": {{}}}}
            ],
            "estimated_time": "string",
            "reasoning": "string"
        }}
        """
        
        try:
            response = self.gemini_client.models.generate_content(
                model=Config.GEMINI_MODEL,
                contents=system_prompt,
                config={'response_mime_type': 'application/json'}
            )
            
            plan_data = json.loads(response.text)
            # Validate with Pydantic
            return AutonomousPlan(**plan_data)
            
        except Exception as e:
            print(f"[!] Brain Error: Failed to formulate plan: {e}")
            # Fallback trivial plan
            return AutonomousPlan(
                goal=goal,
                intent=UserIntent(action_type="research", voice_preference=True),
                steps=[TaskStep(agent_id="EXECUTOR_AGENT", action="research", params={"query": goal})],
                estimated_time="Unknown",
                reasoning=f"Fallback due to error: {str(e)}"
            )

    def process_tactical_logic(self, prompt: str, context: str) -> str:
        """
        High-precision tactical reasoning using Claude.
        """
        system_msg = f"Tactical Context: {context}\nEnsure code/logic precision. Stark-tier requirements."
        try:
            message = self.claude.messages.create(
                model=Config.CLAUDE_MODEL,
                max_tokens=2048,
                system=system_msg,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            return f"Tactical Error: {str(e)}"
