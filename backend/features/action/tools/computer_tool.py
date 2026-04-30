import pyautogui
import base64
import io
import time
from PIL import ImageGrab

class ComputerTool:
    """
    Infrastructure Adapter for OS operations.
    Handles all low-level calls to pyautogui and screen capture.
    """

    @staticmethod
    def configure_safety():
        """Configures global safety settings for pyautogui."""
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.3

    @staticmethod
    def capture_screenshot() -> str:
        """Captures current screen and returns a base64 string."""
        screenshot = ImageGrab.grab()
        buffer = io.BytesIO()
        screenshot.save(buffer, format="PNG")
        buffer.seek(0)
        return base64.standard_b64encode(buffer.read()).decode("utf-8")

    @staticmethod
    def execute_action(action: str, params: dict) -> str:
        """Executes a physical action on the OS."""
        try:
            if action == "mouse_move":
                x, y = params["coordinate"]
                pyautogui.moveTo(x, y, duration=0.25)
                return f"Mouse moved to ({x}, {y})"

            elif action == "left_click":
                x, y = params.get("coordinate", pyautogui.position())
                pyautogui.click(x, y)
                return f"Left clicked at ({x}, {y})"

            elif action == "double_click":
                x, y = params.get("coordinate", pyautogui.position())
                pyautogui.doubleClick(x, y)
                return f"Double clicked at ({x}, {y})"

            elif action == "right_click":
                x, y = params.get("coordinate", pyautogui.position())
                pyautogui.rightClick(x, y)
                return f"Right clicked at ({x}, {y})"

            elif action == "type":
                text = params.get("text", "")
                pyautogui.typewrite(text, interval=0.05)
                return f"Typed: {text[:30]}..."

            elif action == "key":
                key = params.get("key", "")
                if "+" in key:
                    pyautogui.hotkey(*key.split("+"))
                else:
                    pyautogui.press(key)
                return f"Key pressed: {key}"

            elif action == "scroll":
                x, y = params.get("coordinate", pyautogui.position())
                direction = params.get("direction", "down")
                amount = params.get("amount", 3)
                scroll_val = -amount if direction == "down" else amount
                pyautogui.scroll(scroll_val, x=x, y=y)
                return f"Scrolled {direction}"

            return f"Action {action} not recognized by ComputerTool."
        except Exception as e:
            return f"Tool Execution Error: {str(e)}"
