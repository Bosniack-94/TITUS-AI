# TITUS AI: Autonomous Orchestration & Perception Framework

![TITUS Banner](https://img.shields.io/badge/Project-TITUS_AI-ff4b4b?style=for-the-badge&logo=ai&logoColor=white)
![Status](https://img.shields.io/badge/Status-Autonomous_MVP-green?style=for-the-badge)
![Tech](https://img.shields.io/badge/Logic-LangChain_/_FastAPI-blue?style=for-the-badge)

## 🧠 The Philosophy: "Sense → Remember → Think → Act"
TITUS is not just a chatbot; it is a **Proactive Autonomous Agent** designed with a cognitive architecture that mimics human-like decision-making processes. It operates on a unified event orchestration loop to solve complex goals through multi-agent collaboration.

## 🚀 Key Architectural Pillars

### 1. 👁️ Perception (SENSE)
Equipped with a `PerceptionManager`, TITUS captures real-time visual context (screenshots) to understand the environment before making decisions. It doesn't just read text; it *sees* the workspace.

### 2. 📚 The Librarian (REMEMBER)
A dedicated `LibrarianAgent` manages long-term memory using vector-based retrieval (RAG). TITUS recalls past missions, user preferences, and historical data to enrich its current reasoning.

### 3. 🧠 The Brain (THINK)
Powered by high-reasoning LLMs (Gemini 2.0 / Claude 3.5), the `TITUSBrain` formulates strategic plans. It decomposes high-level goals into actionable, step-by-step missions.

### 4. 🛠️ Orchestrator (ACT)
The `TITUSOrchestrator` manages a fleet of specialized agents (Scanner, Voice, Research) to execute the strategic plan, handling error recovery and state persistence.

## 🛠️ Tech Stack
- **Engine**: Python 3.11+ / FastAPI
- **Intelligence**: Gemini 2.0 Flash / Anthropic Claude
- **Frontend**: Vite + React (High-Fidelity Dashboard)
- **Memory**: Vector DB + SQLite Persistence
- **Communication**: WebSockets / SSE for real-time orchestration logs

## 🏗️ Cognitive Workflow
1. **SENSE**: Capture visual/system context.
2. **REMEMBER**: Retrieve relevant memories via LibrarianAgent.
3. **THINK**: Generate a multi-step execution plan.
4. **ASK**: Provide vocal/textual feedback via VoiceAgent (Buenos días, Yayo protocol).
5. **ACT**: Execute steps through specialized sub-agents.
6. **ARCHIVE**: Synthesize and store results in long-term memory.

---
*Developed by [Bosniack-94] - Advancing the frontier of Autonomous Intelligence.*
