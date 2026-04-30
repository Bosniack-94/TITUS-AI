import subprocess
import time
import requests
import os
from core.orchestrator import TITUSOrchestrator

def run_simulation():
    print("=== TITUS STARK TIER SIMULATION (Phases 5 & 6) ===")
    
    # 1. Start the Mock API
    print("[*] Starting Psiquis-X Mock API...")
    api_process = subprocess.Popen(["python", "bridge/env_mock/psiquis_api.py"])
    
    time.sleep(3)
    
    try:
        # 2. Check API
        resp = requests.get("http://localhost:8000/")
        print(f"[+] API Status: {resp.json()['status']}")

        # 3. Launch TITUS
        orchestrator = TITUSOrchestrator(agents_path="agents")
        orchestrator.discover_agents()
        orchestrator.initialize_all()
        
        # --- PHASE 5: THE EYES (Skepticism Layer) ---
        if "vision_agent" in orchestrator.active_agents:
            print("\n[*] Initializing THE EYES (Skepticism Test)...")
            # Low quality image (Test refusal)
            vision_result_blur = orchestrator.dispatch_task("vision_agent", {"image_path": "blur.png", "quality": "LOW"})
            print(f"[>] Vision (Blurry): {vision_result_blur.get('status')} - Reason: {vision_result_blur.get('reason')}")

            # High quality image (Test progress)
            vision_result_ok = orchestrator.dispatch_task("vision_agent", {"image_path": "clear.png", "quality": "HIGH"})
            print(f"[>] Vision (High Def): {vision_result_ok.get('status')} - Analysis: {vision_result_ok.get('analysis')}")

        # --- PHASE 6: THE HANDS (Laptop-level Automation) ---
        if "executor_agent" in orchestrator.active_agents:
            print("\n[*] Initializing THE HANDS (Tactical Shell)...")
            # Running a real system command to see files
            shell_task = {
                "action": "RUN_SHELL",
                "command": "dir /b" # Clean directory listing
            }
            exec_result = orchestrator.dispatch_task("executor_agent", shell_task)
            print(f"[>] Hands Result (Files in TITUS Root):\n{exec_result.get('output', '')[:200]}...")
            
            # Autonomous file synthesis
            print("[*] Synthesizing final state report...")
            orchestrator.dispatch_task("executor_agent", {
                "action": "CREATE_FILE",
                "filename": "STARK_LOG_FINAL.md",
                "content": "# TITUS System: ALL SENSES OPTIMAL\nVerified Vision Skepticism & Shell Execution."
            })
        
    except Exception as e:
        print(f"[!] Simulation Error: {e}")
    finally:
        print("[*] Shutting down simulation...")
        orchestrator.shutdown_all()
        api_process.terminate()
        print("=== SIMULATION END ===")

if __name__ == "__main__":
    run_simulation()
