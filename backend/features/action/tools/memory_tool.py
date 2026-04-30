import chromadb
import json
import time
import os
from collections import deque
from typing import Optional, List
from shared.config import Config


# ─────────────────────────────────────────────
#  STORAGE PATHS
# ─────────────────────────────────────────────
CHROMA_PATH = os.path.join(Config.BASE_PATH, "data", "memory", "chroma_db")
LINEAR_LOG  = os.path.join(Config.BASE_PATH, "data", "memory", "session_log.json")


class MemoryTool:
    """
    Infrastructure Adapter for TITUS Triple-Layer Memory.

    • INSTANT  (Capa 0) — RAM ring-buffer, last N events (ultra-fast, no I/O).
    • LINEAR   (Capa 1) — JSON log persisted to disk (current mission thread).
    • VECTORIAL(Capa 2) — ChromaDB semantic store (long-term, survives restarts).
    """

    # -------------------------------------------------------------------
    # Instant Memory — ring buffer in RAM
    # -------------------------------------------------------------------
    _instant_buffer: deque = deque(maxlen=10)   # last 10 events

    @classmethod
    def push_instant(cls, event: str, source: str = "SYSTEM") -> None:
        cls._instant_buffer.append({
            "ts": time.time(),
            "source": source,
            "event": event
        })

    @classmethod
    def get_instant(cls, n: int = 5) -> List[dict]:
        """Return the N most-recent instant events."""
        return list(cls._instant_buffer)[-n:]

    # -------------------------------------------------------------------
    # Linear Memory — ordered JSON file (session thread)
    # -------------------------------------------------------------------
    @classmethod
    def append_linear(cls, entry: dict) -> None:
        """Appends one entry to the session log (creates file if absent)."""
        history = cls._load_linear()
        entry["ts"] = time.time()
        history.append(entry)
        with open(LINEAR_LOG, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    @classmethod
    def get_linear(cls, last_n: int = 20) -> List[dict]:
        """Returns the last N entries from the session log."""
        return cls._load_linear()[-last_n:]

    @classmethod
    def clear_linear(cls) -> None:
        """Wipes the session log (call after mission success)."""
        with open(LINEAR_LOG, "w", encoding="utf-8") as f:
            json.dump([], f)

    @classmethod
    def _load_linear(cls) -> list:
        if not os.path.exists(LINEAR_LOG):
            return []
        try:
            with open(LINEAR_LOG, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    # -------------------------------------------------------------------
    # Vectorial Memory — ChromaDB (persistent semantic search)
    # -------------------------------------------------------------------
    _chroma_client: Optional[chromadb.PersistentClient] = None
    _collection = None

    @classmethod
    def _get_collection(cls):
        if cls._chroma_client is None:
            os.makedirs(CHROMA_PATH, exist_ok=True)
            cls._chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
        if cls._collection is None:
            cls._collection = cls._chroma_client.get_or_create_collection(
                name="titus_memory",
                metadata={"hnsw:space": "cosine"}
            )
        return cls._collection

    @classmethod
    def store_vectorial(
        cls,
        content: str,
        doc_id: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> str:
        """
        Stores a fact/experience in the vectorial memory.
        ChromaDB uses its own embedding model (default: all-MiniLM-L6-v2).
        Returns the document ID.
        """
        collection = cls._get_collection()
        doc_id = doc_id or f"mem_{int(time.time()*1000)}"
        meta = metadata or {}
        meta["ts"] = str(time.time())
        collection.add(
            documents=[content],
            metadatas=[meta],
            ids=[doc_id]
        )
        return doc_id

    @classmethod
    def recall_vectorial(cls, query: str, n_results: int = 3) -> List[dict]:
        """
        Semantic search: returns the N most-relevant memories for the query.
        Each result: {"content": str, "metadata": dict, "distance": float}
        """
        collection = cls._get_collection()
        if collection.count() == 0:
            return []
        
        results = collection.query(
            query_texts=[query],
            n_results=min(n_results, collection.count())
        )
        
        output = []
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for doc, meta, dist in zip(docs, metas, distances):
            output.append({"content": doc, "metadata": meta, "distance": round(dist, 4)})
        return output

    @classmethod
    def memory_count(cls) -> int:
        """Returns the total number of vectorial memories stored."""
        return cls._get_collection().count()
