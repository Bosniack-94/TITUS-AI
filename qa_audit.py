import time
import requests
import subprocess
from core.orchestrator import TITUSOrchestrator

def run_diamond_audit():
    print("=== TITUS DIAMOND TIER QA AUDIT ===")
    errors = 0
    
    # 1. Start API Mock
    print("[QA-1] Starting Integration Bridge...")
    api_process = subprocess.Popen(["python", "bridge/env_mock/psiquis_api.py"])
    time.sleep(2)
    
    try:
        # TEST A: Bridge Connectivity
        print("[QA-2] Testing Bridge Latency (Retry-Enabled)...")
        for i in range(5):
            try:
                start = time.time()
                resp = requests.get("http://localhost:8000/", timeout=5)
                latency = time.time() - start
                if resp.status_code == 200:
                    print(f"[OK] Bridge latency: {latency:.4f}s (Attempt {i+1})")
                    break
            except Exception:
                time.sleep(1)
        else:
            print("[FAIL] Bridge critical or unreachable after 5 attempts")
            errors += 1

        # TEST B: Orchestration & Discovery
        print("[QA-3] Testing Multi-Agent Discovery...")
        orchestrator = TITUSOrchestrator(agents_path="agents")
        orchestrator.discover_agents()
        required_agents = ["scanner_agent", "vision_agent", "executor_agent", "voice_agent"]
        for agent in required_agents:
            if agent in orchestrator.active_agents:
                print(f"[OK] {agent} found and loaded.")
            else:
                print(f"[FAIL] {agent} missing or invalid.")
                errors += 1

        # TEST C: Sense Loopback (Eyes/Hands/Voice)
        print("[QA-4] Testing Multi-Sense Execution...")
        orchestrator.initialize_all()
        
        # Test Voice
        res = orchestrator.dispatch_task("voice_agent", {"action": "SAY", "text": "Audit in progress."})
        if res.get("status") == "SUCCESS": print("[OK] Voice Agent Responsive.")
        else: errors += 1

        # Test Executor
        res = orchestrator.dispatch_task("executor_agent", {"action": "RUN_SHELL", "command": "echo 'Diamond Test'"})
        if res.get("status") == "SUCCESS": print("[OK] Executor Agent Authorized.")
        else: errors += 1
        
    except Exception as e:
        print(f"[CRITICAL ERROR] {e}")
        errors += 1
    finally:
        print(f"\n--- AUDIT COMPLETE ---")
        print(f"Total Failures: {errors}")
        orchestrator.shutdown_all()
        api_process.terminate()
        
    return errors == 0

if __name__ == "__main__":
    success = run_diamond_audit()
    if success:
        print("\n[CONCLUSION] TITUS SYSTEM STATUS: DIAMOND / OPTIMAL")
    else:
        print("\n[CONCLUSION] TITUS SYSTEM STATUS: DEGRADED / FIX REQUIRED")
