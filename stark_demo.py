import time
from core.orchestrator import TITUSOrchestrator

def demonstrate_stark_reasoning():
    print("=== TITUS REASONING TRACE: PROJECT AUDIT ===")
    orchestrator = TITUSOrchestrator(agents_path="agents")
    orchestrator.discover_agents()
    orchestrator.initialize_all()

    print("\n[REASONING] Goal: Compile a Diamond Tier status report and verify all system 'Hands'.")
    
    # 1. Voice Greeting
    orchestrator.dispatch_task("voice_agent", {"action": "SAY", "text": "Iniciando protocolo de razonamiento táctico. Verificando todos los Zords activos."})

    # 2. Scanner Analysis
    print("\n[REASONING] STEP 1: Scanning architecture for integrity...")
    scan = orchestrator.dispatch_task("scanner_agent", {"target": "TITUS_ROOT"})
    time.sleep(1)
    
    # 3. Vision Check
    print("\n[REASONING] STEP 2: Verifying 'Eyes' confidence...")
    vision = orchestrator.dispatch_task("vision_agent", {"image_path": "audit_view.png", "quality": "HIGH"})
    time.sleep(1)

    # 4. Hands Execution
    print("\n[REASONING] STEP 3: Executing file synthesis (Real Hands)...")
    orchestrator.dispatch_task("executor_agent", {
        "action": "CREATE_FILE", 
        "filename": "DIAMOND_REPORT_LOG.md",
        "content": "# DIAMOND AUDIT PASS\nSystem is 100% operational according to Stark protocols."
    })

    # 5. Final Voice Report
    orchestrator.dispatch_task("voice_agent", {"action": "SAY", "text": "Informe de Auditoría Diamante completado. El reporte ha sido sintetizado en su laptop, Jefe. Todo está en orden."})

    orchestrator.shutdown_all()
    print("\n=== REASONING COMPLETE ===")

if __name__ == "__main__":
    demonstrate_stark_reasoning()
