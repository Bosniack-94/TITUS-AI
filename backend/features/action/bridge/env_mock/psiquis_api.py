from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel

app = FastAPI(title="Psiquis-X server_v3 (MOCK)")

class TelemetryData(BaseModel):
    agent_id: str
    message: str
    level: str = "INFO"

@app.get("/")
def read_root():
    return {"status": "Psiquis-X Mock Online", "version": "v3-minimal-mock"}

@app.post("/telemetry")
def post_telemetry(data: TelemetryData):
    # Mocking the telemetry ingestion
    print(f"[MOCK SSE] Broadcast: {data.agent_id} -> {data.message}")
    return {"status": "broadcasted"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
