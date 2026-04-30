import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = "http://127.0.0.1:8001";

function App() {
  const [goal, setGoal] = useState("");
  const [thoughts, setThoughts] = useState([
    { label: "SISTEMA_READY", text: "TITUS Professional Core v3.14 - Enlace de autonomía estable." }
  ]);
  const [agents, setAgents] = useState({});
  const [loading, setLoading] = useState(false);

  // Poll for agent status updates
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await axios.get(`${BACKEND_URL}/status`);
        setAgents(res.data.agents || {});
      } catch (e) {
        // Silent fail on polling - common for local dev startups
      }
    }, 2500);
    return () => clearInterval(interval);
  }, []);

  const handleRun = async () => {
    if (!goal.trim()) return;
    
    setLoading(true);
    setThoughts(prev => [...prev, { label: "GOAL_RECIBIDO", text: goal }]);
    
    try {
      const res = await axios.post(`${BACKEND_URL}/research`, { query: goal, voice_preference: true });
      if (res.data.status === "TITUS_PROTOCOL_ENGAGED" || res.data.status === "TITUS_AUTONOMOUS_MODE_ACTIVE") {
        setThoughts(prev => [...prev, 
          { label: "BRAIN_SYNK", text: "Dual-LLM (Gemini + Claude) activo. Planificación autónoma iniciada..." },
          { label: "LIBRARIAN_ACTIVE", text: "Consultando memoria histórica... Agente Bibliotecario en línea." }
        ]);
        setGoal("");
      }
    } catch (e) {
      setThoughts(prev => [...prev, { label: "ERROR_ENLACE", text: "Fallo crítico al conectar con el Backend TITUS." }]);
    }
    setLoading(false);
  };

  return (
    <div className="titus-container">
      {/* Telemetry Sidebar */}
      <aside className="titus-sidebar">
        <div style={{ padding: '20px', borderBottom: '1px solid var(--border)', fontFamily: 'Orbitron', fontSize: '0.7rem', color: 'var(--accent)' }}>
          TELEMETRÍA_AGENTES
        </div>
        <div className="agent-list">
          {Object.entries(agents).map(([name, status]) => (
            <div key={name} className="agent-card">
              <span className="agent-name">{name.toUpperCase()}</span>
              <span className="agent-state">{status}</span>
            </div>
          ))}
          {Object.keys(agents).length === 0 && (
            <div className="agent-card">
              <span className="agent-state">ESPERANDO_NUCLEO...</span>
            </div>
          )}
        </div>
      </aside>

      {/* Main Command Console */}
      <main className="titus-main">
        <header className="titus-header">
          <div className="titus-logo">TITUS <span style={{ fontWeight: 300 }}>AUTONOMOUS</span></div>
          <div style={{ fontSize: '0.6rem', color: '#8b949e', opacity: 0.5 }}>V3.14_RIGOR // STARK_INDUSTRIES_MODEL</div>
        </header>

        <section className="titus-content">
          <div className="thought-chain">
            {thoughts.map((t, i) => (
              <div key={i} className="thought-step">
                <div className="step-number">{(i + 1).toString().padStart(2, '0')}</div>
                <div className="step-card">
                  <div className="step-label">{t.label}</div>
                  <div className="step-text">{t.text}</div>
                </div>
              </div>
            ))}
            {loading && (
              <div className="thought-step">
                <div className="step-number">??</div>
                <div className="step-card" style={{ opacity: 0.5 }}>
                  <div className="step-label">PENSANDO...</div>
                  <div className="step-text">Procesando comandos tácticos...</div>
                </div>
              </div>
            )}
          </div>
        </section>

        <footer className="titus-input-section">
          <div className="input-wrapper">
            <input 
              type="text" 
              value={goal} 
              onChange={(e) => setGoal(e.target.value)} 
              onKeyDown={(e) => e.key === 'Enter' && handleRun()}
              placeholder="¿Qué órdenes desea ejecutar hoy, Señor?" 
              disabled={loading}
            />
            <button className="btn-execute" onClick={handleRun} disabled={loading}>
              EJECUTAR
            </button>
          </div>
        </footer>
      </main>
    </div>
  );
}

export default App;
