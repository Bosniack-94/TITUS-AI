import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """
    TITUS Central Configuration.
    Stores professional environment settings and model parameters.
    """
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    
    # Versioning & Environment
    VERSION = os.getenv("TITUS_VERSION", "3.14_RIGOR")
    ENV = os.getenv("ENV", "DEVELOPMENT")
    
    # Models
    GEMINI_MODEL = "gemini-2.0-flash"
    CLAUDE_MODEL = "claude-3-5-sonnet-20241022"
    
    # Paths
    BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    AGENTS_PATH = os.path.join(BASE_PATH, "features", "collaboration", "agents")
    TOOLS_PATH = os.path.join(BASE_PATH, "features", "action", "tools")
    DATA_PATH = os.path.join(BASE_PATH, "data")
    RAW_DATA_PATH = os.path.join(DATA_PATH, "raw")
    PROCESSED_DATA_PATH = os.path.join(DATA_PATH, "processed")

if __name__ == "__main__":
    print(f"[*] TITUS Config: Loading {Config.VERSION} in {Config.ENV} mode.")
    if not Config.GOOGLE_API_KEY: print("[!] WARNING: Google API Key missing!")
    if not Config.ANTHROPIC_API_KEY: print("[!] WARNING: Anthropic API Key missing!")
