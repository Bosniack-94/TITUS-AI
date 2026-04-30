from core.orchestrator import TITUSOrchestrator
import os

def main():
    print("=== TITUS SYSTEM ONLINE ===")
    
    # Initialize the orchestrator
    # We assume 'agents' folder is in the same directory as where we run this
    orchestrator = TITUSOrchestrator(agents_path="agents")
    
    # 1. Discover agents
    orchestrator.discover_agents()
    
    # 2. Boot up agents
    orchestrator.initialize_all()
    
    # 3. Test: Dispatch a task to the new agent
    if "scanner_agent" in orchestrator.active_agents:
        task = {"target": "System Context Alpha"}
        result = orchestrator.dispatch_task("scanner_agent", task)
        print(f"[>] TITUS Result: {result}")
    else:
        print("[!] No scanner agent found to test.")
    
    # 4. Shutdown
    orchestrator.shutdown_all()
    print("=== TITUS SYSTEM OFFLINE ===")

if __name__ == "__main__":
    main()
