import os
import json
import time
import datetime
from shared.base_agent import BaseAgent
from shared.config import Config
from features.action.tools.memory_tool import MemoryTool
from features.action.tools.voice_tool import VoiceTool


# ─── Paths for data files ─────────────────────────────────────────────────────
AGENDA_PATH      = os.path.join(Config.BASE_PATH, "data", "agenda.json")
STATE_PATH       = os.path.join(Config.BASE_PATH, "data", "system_state.json")


class LibrarianAgent(BaseAgent):
    """
    TITUS Agent 7: The Archivist.

    Identity   : Formal, deliberate, archival.
    Voice      : Distinct vocal prefix to signal memory-recall moments.
    Personality: The keeper of all past missions, failures, and victories.

    Responsibilities:
      • STORE                    → Persist new facts/events to the appropriate memory layer.
      • RECALL                   → Semantically retrieve relevant memories for a given query.
      • SYNTHESIZE               → Generate a brief mission summary and commit it to long-term memory.
      • STATUS                   → Report the health of the memory system.
      • CLEAR_SESSION            → Wipe the linear log after a mission concludes.
      • GENERATE_STARTUP_BRIEFING → Proactive "Buenos días, Yayo" protocol.
    """

    VOICE_PREFIX     = "Señor, consultando los archivos de TITUS..."
    OWNER_NAME       = "Yayo"

    # ─────────────────────────────────────────
    # LIFECYCLE
    # ─────────────────────────────────────────

    def initialize(self):
        print(f"[+] {self.name}: Opening the Archive vaults. Scanning memory banks...")
        from features.action.bridge.connector import PsiquisBridge
        self.bridge = PsiquisBridge()

        count = MemoryTool.memory_count()
        self.status = "ACTIVE"
        self.bridge.sync_agent_status(
            self.agent_id, self.status,
            f"Archive ready. {count} long-term memories loaded."
        )
        print(f"[+] {self.name}: Archive online. {count} vectorial memories indexed.")

    def execute(self, task: dict) -> dict:
        action = task.get("action", "STATUS")

        if action == "STORE":
            return self._store(task)
        elif action == "RECALL":
            return self._recall(task)
        elif action == "SYNTHESIZE":
            return self._synthesize(task)
        elif action == "CLEAR_SESSION":
            return self._clear_session()
        elif action == "STATUS":
            return self._status()
        elif action == "GENERATE_STARTUP_BRIEFING":
            return self._generate_startup_briefing()

        return {"status": "UNKNOWN_ACTION", "action": action}

    # ─────────────────────────────────────────
    # ACTIONS
    # ─────────────────────────────────────────

    def _store(self, task: dict) -> dict:
        """Stores information across memory layers based on scope."""
        content  = task.get("content", "")
        scope    = task.get("scope", "all")
        source   = task.get("source", "SYSTEM")
        metadata = task.get("metadata", {})
        stored_in = []

        if scope in ("instant", "all"):
            MemoryTool.push_instant(content, source=source)
            stored_in.append("INSTANT")
        if scope in ("linear", "all"):
            MemoryTool.append_linear({"source": source, "content": content, "metadata": metadata})
            stored_in.append("LINEAR")
        if scope in ("vectorial", "all"):
            doc_id = MemoryTool.store_vectorial(content, metadata={**metadata, "source": source})
            stored_in.append(f"VECTORIAL[{doc_id}]")

        self.bridge.sync_agent_status(self.agent_id, "SUCCESS", f"Archived in: {', '.join(stored_in)}")
        return {"status": "SUCCESS", "stored_in": stored_in}

    def _recall(self, task: dict) -> dict:
        """Retrieves memories relevant to a query."""
        query = task.get("query", "")
        if not query:
            return {"status": "ERROR", "msg": "No query provided."}

        self.bridge.sync_agent_status(self.agent_id, "SEARCHING", f"Consulting archives for: {query[:30]}")
        print(f"[*] {self.name}: Searching memory for: '{query}'")

        instant   = MemoryTool.get_instant(n=3)
        linear    = MemoryTool.get_linear(last_n=5)
        vectorial = MemoryTool.recall_vectorial(query, n_results=3)

        if vectorial:
            top_memory = vectorial[0]["content"]
            VoiceTool.speak(f"{self.VOICE_PREFIX} He encontrado experiencia relevante: {top_memory[:60]}.")

        context = self._build_context(instant, linear, vectorial)
        self.bridge.sync_agent_status(self.agent_id, "SUCCESS",
            f"Recalled {len(vectorial)} vectorial + {len(linear)} linear memories.")
        return {
            "status": "SUCCESS", "query": query, "context": context,
            "vectorial_matches": len(vectorial), "linear_entries": len(linear),
            "instant_events": len(instant)
        }

    def _synthesize(self, task: dict) -> dict:
        """Generates a mission summary and stores it in long-term vectorial memory."""
        mission_name = task.get("mission", "Unknown Mission")
        outcome      = task.get("outcome", "")
        session      = MemoryTool.get_linear(last_n=50)

        if not session:
            return {"status": "EMPTY", "msg": "No session data to synthesize."}

        events  = [e.get("content", "") for e in session[:10]]
        summary = f"MISSION '{mission_name}': {outcome}. Key events: {' | '.join(events[:5])}"

        doc_id = MemoryTool.store_vectorial(
            summary,
            metadata={"type": "mission_summary", "mission": mission_name,
                      "outcome": outcome, "session_length": str(len(session))}
        )
        VoiceTool.speak(f"Señor, el resumen de la misión '{mission_name}' ha sido archivado en la memoria permanente.")

        count = MemoryTool.memory_count()
        self.bridge.sync_agent_status(self.agent_id, "SUCCESS", f"Mission synthesized. Total memories: {count}")
        return {"status": "SUCCESS", "doc_id": doc_id, "total_memories": count, "summary": summary}

    def _clear_session(self) -> dict:
        """Wipes the linear session log after mission close."""
        MemoryTool.clear_linear()
        self.bridge.sync_agent_status(self.agent_id, "ACTIVE", "Session cleared. Archive ready.")
        return {"status": "SESSION_CLEARED"}

    def _status(self) -> dict:
        """Returns a health report of all memory layers."""
        total_vectorial = MemoryTool.memory_count()
        recent_linear   = len(MemoryTool.get_linear(last_n=100))
        instant_events  = len(MemoryTool.get_instant(n=10))
        status_report = {
            "status": "NOMINAL",
            "vectorial_memories": total_vectorial,
            "linear_entries_this_session": recent_linear,
            "instant_buffer_size": instant_events,
            "layers": {"INSTANT": "ONLINE", "LINEAR": "ONLINE", "VECTORIAL": "ONLINE"}
        }
        self.bridge.sync_agent_status(self.agent_id, "ACTIVE",
            f"Memory: {total_vectorial} long-term | {recent_linear} session")
        return status_report

    # ─────────────────────────────────────────
    # PROACTIVE STARTUP BRIEFING
    # ─────────────────────────────────────────

    def _generate_startup_briefing(self) -> dict:
        """
        Generates and delivers the proactive 'Buenos días, Yayo' protocol.
        • Fires only once per calendar day.
        • Detects if it is a work day or rest day.
        • Recalls last project milestones.
        • Suggests (does not assign) the next step.
        """
        today     = datetime.date.today()
        today_str = today.isoformat()                            # "2026-04-08"
        weekday   = today.weekday()                              # 0=Mon … 6=Sun

        # ── 1. ANTI-REPEAT GUARD ──────────────────────────────
        state = self._load_state()
        if state.get("last_greeting_date") == today_str:
            print(f"[*] {self.name}: Briefing already delivered today. Skipping.")
            return {"status": "ALREADY_GREETED", "date": today_str}

        # ── 2. LOAD AGENDA ────────────────────────────────────
        agenda = self._load_agenda()
        is_rest_day = self._is_rest_day(today_str, weekday, agenda)

        # ── 3. BUILD SCRIPT ───────────────────────────────────
        script = self._build_briefing_script(today, weekday, is_rest_day, agenda)

        # ── 4. DELIVER VOICE BRIEFING ─────────────────────────
        print(f"\n{'═'*60}")
        print(f"[📋 TITUS MORNING BRIEFING — {today_str}]")
        print(f"{'═'*60}")
        print(script)
        print(f"{'═'*60}\n")
        VoiceTool.speak(script)

        # ── 5. PERSIST STATE ──────────────────────────────────
        state["last_greeting_date"]   = today_str
        state["session_count_today"]  = 1
        state["last_session_summary"] = script
        self._save_state(state)

        # ── 6. ARCHIVE IN MEMORY ──────────────────────────────
        MemoryTool.store_vectorial(
            f"Daily briefing delivered on {today_str}.",
            metadata={"type": "daily_briefing", "date": today_str,
                      "day_type": "REST" if is_rest_day else "WORK"}
        )

        self.bridge.sync_agent_status(self.agent_id, "ACTIVE", f"Morning briefing delivered — {today_str}")
        return {"status": "BRIEFING_DELIVERED", "date": today_str, "script": script}

    # ─────────────────────────────────────────
    # BRIEFING HELPERS
    # ─────────────────────────────────────────

    def _build_briefing_script(
        self, today: datetime.date, weekday: int, is_rest_day: bool, agenda: dict
    ) -> str:
        """Constructs the full natural-language greeting script."""
        owner     = agenda.get("owner", self.OWNER_NAME)
        day_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        month_names = ["enero","febrero","marzo","abril","mayo","junio",
                       "julio","agosto","septiembre","octubre","noviembre","diciembre"]
        day_name  = day_names[weekday]
        date_str  = f"{today.day} de {month_names[today.month - 1]} de {today.year}"

        # Greeting line
        hour = datetime.datetime.now().hour
        if hour < 12:
            greeting_time = "Buenos días"
        elif hour < 19:
            greeting_time = "Buenas tardes"
        else:
            greeting_time = "Buenas noches"

        lines = [f"{greeting_time}, {owner}. Hoy es {day_name}, {date_str}."]

        if is_rest_day:
            lines.append("Hoy es su día de descanso. No hay pendientes de trabajo activos.")
            # Personal reminders on rest days
            personal = agenda.get("personal_reminders", [])
            for reminder in personal:
                if reminder.get("day_of_week", "").lower() == day_names[weekday].lower():
                    lines.append(reminder["message"])
            # Check for personal tasks
            personal_tasks = [t for t in agenda.get("pending_tasks", [])
                              if t.get("type") != "technical"]
            if personal_tasks:
                titles = ", ".join(t["title"] for t in personal_tasks[:2])
                lines.append(f"Sin embargo, tiene estos recordatorios personales pendientes: {titles}.")
            else:
                lines.append("No tiene pendientes personales registrados para hoy. Disfrute su descanso.")
        else:
            # Work day — report active projects
            active_projects = agenda.get("active_projects", [])
            if active_projects:
                lines.append("Aquí está el estado de sus proyectos activos:")
                for project in active_projects[:2]:
                    name       = project["name"]
                    milestone  = project["current_milestone"]
                    total      = project["total_milestones"]
                    last_worked = project.get("last_worked", "días pasados")
                    lines.append(
                        f"El proyecto {name} está en el hito {milestone} de {total}. "
                        f"La última vez trabajamos en él fue el {last_worked}."
                    )
                    # Suggest next step
                    next_milestone = milestone + 1
                    if next_milestone <= total:
                        lines.append(
                            f"¿Le gustaría que hoy avanzáramos hacia el hito {next_milestone} de {name}?"
                        )

            # Pending tasks
            pending = [t for t in agenda.get("pending_tasks", []) if t.get("priority") == "HIGH"]
            if pending:
                titles = ", ".join(t["title"] for t in pending[:2])
                lines.append(f"También tiene tareas de alta prioridad pendientes: {titles}.")

            lines.append("¿Tiene algo adicional en mente para el día de hoy?")

        return " ".join(lines)

    @staticmethod
    def _is_rest_day(today_str: str, weekday: int, agenda: dict) -> bool:
        """Returns True if today is a designated rest day."""
        if weekday in agenda.get("rest_days", [5, 6]):
            return True
        if today_str in agenda.get("special_rest_days", []):
            return True
        return False

    # ─────────────────────────────────────────
    # STATE / AGENDA I/O
    # ─────────────────────────────────────────

    @staticmethod
    def _load_agenda() -> dict:
        try:
            with open(AGENDA_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    @staticmethod
    def _load_state() -> dict:
        try:
            with open(STATE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    @staticmethod
    def _save_state(state: dict) -> None:
        with open(STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    # ─────────────────────────────────────────
    # GENERIC HELPERS
    # ─────────────────────────────────────────

    @staticmethod
    def _build_context(instant: list, linear: list, vectorial: list) -> str:
        """Builds a clean context string for the Brain."""
        parts = []
        if vectorial:
            parts.append("=== LONG-TERM MEMORY (Vectorial) ===")
            for v in vectorial:
                parts.append(f"  [{round(1 - v['distance'], 2)*100:.0f}% relevance] {v['content']}")
        if linear:
            parts.append("=== SESSION LOG (Linear) ===")
            for entry in linear[-3:]:
                parts.append(f"  [{entry.get('source', '?')}] {entry.get('content', '')}")
        if instant:
            parts.append("=== RECENT EVENTS (Instant) ===")
            for ev in instant:
                parts.append(f"  [{ev['source']}] {ev['event']}")
        return "\n".join(parts) if parts else "No prior memories found."

    def shutdown(self):
        print(f"[-] {self.name}: Sealing the Archive.")
        self.status = "OFFLINE"
