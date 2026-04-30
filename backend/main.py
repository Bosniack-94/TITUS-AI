from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import time
import asyncio
from features.collaboration.orchestrator import TITUSOrchestrator
from shared.config import Config
from features.perception.perception import PerceptionManager
from shared.schemas import UserIntent, PerceptionReport
from features.cognition.brain import TITUSBrain
from features.action.tools.memory_tool import MemoryTool
from dotenv import load_dotenv

app = FastAPI(title=f"TITUS RIGOR {Config.VERSION}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# CORE SYSTEM INITIALIZATION
# ─────────────────────────────────────────────
perception  = PerceptionManager()
brain       = TITUSBrain()
orchestrator = TITUSOrchestrator(agents_path=Config.AGENTS_PATH)

perception.startup()
orchestrator.discover_agents()
orchestrator.initialize_all()


# ─────────────────────────────────────────────
# STARTUP BRIEFING — "Buenos días, Yayo"
# ─────────────────────────────────────────────
def _run_startup_briefing():
    """
    Fires the Librarian's proactive daily briefing in a background thread.
    - Only fires once per calendar day (anti-repeat guard inside LibrarianAgent).
    - Runs async so the FastAPI server starts instantly without waiting.
    """
    import threading, time
    def _briefing():
        time.sleep(1.5)  # Let all agents fully settle first
        librarian = orchestrator.active_agents.get("librarian_agent")
        if librarian:
            librarian.execute({"action": "GENERATE_STARTUP_BRIEFING"})

    thread = threading.Thread(target=_briefing, daemon=True, name="TITUS_StartupBriefing")
    thread.start()

_run_startup_briefing()


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def _get_librarian():
    """Convenience shortcut to the LibrarianAgent."""
    return orchestrator.active_agents.get("librarian_agent")

def _get_voice():
    """Convenience shortcut to the VoiceAgent."""
    return orchestrator.active_agents.get("voice_agent")


# ─────────────────────────────────────────────
# EVENT ORCHESTRATION LOOP
# ─────────────────────────────────────────────
async def run_unified_orchestration(goal: str, voice_pref: bool):
    """
    TITUS Unified Event Loop (Sense → Remember → Think → Ask → Act → Archive)

    Step 1 — SENSE   : Perception takes a screenshot for visual context.
    Step 2 — REMEMBER: LibrarianAgent retrieves relevant past memories.
    Step 3 — THINK   : Brain formulates a plan using perception + memory.
    Step 4 — ASK     : VoiceAgent announces the plan (if voice_pref=True).
    Step 5 — ACT     : Orchestrator executes the plan step-by-step.
    Step 6 — ARCHIVE : LibrarianAgent stores the mission outcome.
    """
    print(f"[*] TITUS Core: Unified Protocol ENGAGED → '{goal}'")

    # STEP 1 — SENSE
    report_data = perception.perceive()
    session_report = PerceptionReport(
        screen_summary=report_data.get("screen_context", "Screen unavailable."),
        timestamp=time.time()
    )
    MemoryTool.push_instant(f"New mission: {goal}", source="ORCHESTRATOR")
    MemoryTool.append_linear({"source": "USER", "content": goal, "metadata": {}})

    # STEP 2 — REMEMBER (LibrarianAgent is gatekeeper)
    memory_context = "No prior memories for this goal."
    librarian = _get_librarian()
    if librarian:
        recall_result = librarian.execute({"action": "RECALL", "query": goal})
        if recall_result.get("status") == "SUCCESS":
            memory_context = recall_result.get("context", memory_context)
            print(f"[+] LibrarianAgent: Context loaded ({recall_result['vectorial_matches']} vectorial matches).")

    # Inject memory context into the perception report
    enriched_summary = f"{session_report.screen_summary}\n\n[LIBRARIAN CONTEXT]\n{memory_context}"
    enriched_report  = PerceptionReport(
        screen_summary=enriched_summary,
        timestamp=session_report.timestamp
    )

    # STEP 3 — THINK
    plan = brain.formulate_plan(goal, enriched_report)
    print(f"[+] Brain: Plan formulated — {len(plan.steps)} steps. Reasoning: {plan.reasoning[:60]}...")

    # STEP 4 — ASK / ADAPT
    if voice_pref:
        voice = _get_voice()
        if voice:
            msg = (f"Señor, tengo un plan de {len(plan.steps)} pasos para: {goal}. "
                   f"Iniciando ejecución.")
            voice.execute({"action": "SAY", "text": msg})

    # STEP 5 — ACT
    results = await orchestrator.execute_strategic_plan(plan)
    print(f"[+] TITUS: Mission execution done. {len(results)} steps completed.")

    # STEP 6 — ARCHIVE
    if librarian:
        outcome_summary = f"Completed {len(results)} steps successfully."
        librarian.execute({
            "action": "SYNTHESIZE",
            "mission": goal,
            "outcome": outcome_summary
        })

    if voice_pref:
        voice = _get_voice()
        if voice:
            voice.execute({
                "action": "SAY",
                "text": "Misión archivada. El Bibliotecario ha registrado los resultados en la memoria permanente."
            })


# ─────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────
@app.post("/research")
async def research(req: dict, background_tasks: BackgroundTasks):
    """
    Primary entry point. Triggers the full Event Orchestration Loop.
    Supports voice_preference (bool) to control vocal feedback.
    """
    goal = req.get("query")
    voice_pref = req.get("voice_preference", True)

    if not goal:
        raise HTTPException(status_code=400, detail="'query' is required.")

    background_tasks.add_task(run_unified_orchestration, goal, voice_pref)
    return {
        "status": "TITUS_PROTOCOL_ENGAGED",
        "goal": goal,
        "perception": "ACTIVE",
        "librarian": "ACTIVE"
    }


@app.get("/status")
async def get_status():
    """Returns system health including memory statistics."""
    librarian = _get_librarian()
    memory_stats = {}
    if librarian:
        memory_stats = librarian.execute({"action": "STATUS"})

    return {
        "status": "ONLINE",
        "version": Config.VERSION,
        "perception_active": perception._is_active,
        "agents": {name: agent.status for name, agent in orchestrator.active_agents.items()},
        "memory": memory_stats
    }


@app.get("/memory/recall")
async def recall_memory(query: str):
    """Direct endpoint to ask the LibrarianAgent for memories."""
    librarian = _get_librarian()
    if not librarian:
        raise HTTPException(status_code=503, detail="LibrarianAgent not available.")
    result = librarian.execute({"action": "RECALL", "query": query})
    return result


@app.post("/memory/store")
async def store_memory(req: dict):
    """Direct endpoint to store a fact in the memory system."""
    librarian = _get_librarian()
    if not librarian:
        raise HTTPException(status_code=503, detail="LibrarianAgent not available.")
    result = librarian.execute({
        "action": "STORE",
        "content": req.get("content", ""),
        "scope": req.get("scope", "all"),
        "source": req.get("source", "USER"),
        "metadata": req.get("metadata", {})
    })
    return result


@app.on_event("shutdown")
def shutdown_event():
    perception.shutdown()
    orchestrator.shutdown_all()


if __name__ == "__main__":
    import uvicorn
    print(f"[*] TITUS v{Config.VERSION}: Event Orchestrator launching on port 8001...")
    uvicorn.run(app, host="127.0.0.1", port=8001)
