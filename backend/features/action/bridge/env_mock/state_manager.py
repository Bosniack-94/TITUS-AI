import sqlite3
import os

class PsiquisStateManagerMock:
    """
    Mock of the Psiquis-X StateManager.
    Internalizes the LTM (Long-Term Memory) concepts.
    """
    def __init__(self, db_path="psiquis_state_mock.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_state (
                agent_id TEXT PRIMARY KEY,
                last_thought TEXT,
                token_usage INTEGER,
                status TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def update_agent(self, agent_id, thought, tokens, status):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO agent_state (agent_id, last_thought, token_usage, status)
            VALUES (?, ?, ?, ?)
        ''', (agent_id, thought, tokens, status))
        conn.commit()
        conn.close()
        print(f"[MOCK] Psiquis State Updated: {agent_id} -> {status}")

    def get_all_states(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM agent_state')
        rows = cursor.fetchall()
        conn.close()
        return rows
