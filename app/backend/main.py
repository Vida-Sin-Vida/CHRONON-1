from fastapi import FastAPI, WebSocket, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import json
import os
import csv
from .process_manager import manager, runs_store

from fastapi.staticfiles import StaticFiles

app = FastAPI(title="CHRONON-1 Interface")

# Mount frontend
# In prod, we would build React and serve 'dist'.
# For dev/demo without build, we try to serve source or just a placeholder.
# Let's assume we might rely on the user running Vite, but if we want to serve:
if os.path.exists("app/frontend"):
    app.mount("/ui", StaticFiles(directory="app/frontend", html=True), name="frontend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class RunConfig(BaseModel):
    command_type: str # simulate, ingest, preprocess, analyze
    args: Optional[dict] = {}

class UnblindRequest(BaseModel):
    admin_token: str

@app.get("/api/runs")
async def list_runs():
    # Return list of runs (in-memory + potentially loaded from ledger)
    # Convert dict to list, sorted by time desc
    runs_list = list(runs_store.values())
    runs_list.sort(key=lambda x: x["timestamp"], reverse=True)
    return runs_list

@app.get("/api/runs/{run_id}")
async def get_run(run_id: str):
    if run_id not in runs_store:
        raise HTTPException(status_code=404, detail="Run not found")
    return runs_store[run_id]

@app.post("/api/runs/launch")
async def launch_run(config: RunConfig):
    # Map high level request to CLI args
    cmd_args = []
    
    if config.command_type == "simulate":
        eps = config.args.get("eps", 0.0)
        output = config.args.get("output", f"data/raw/sim_{uuid.uuid4().hex[:6]}.csv")
        cmd_args = ["simulate", "--eps", str(eps), "--output", output]
        
    elif config.command_type == "ingest":
        input_file = config.args.get("input_file")
        cmd_args = ["ingest", input_file]
        
    elif config.command_type == "preprocess":
        input_file = config.args.get("input_file")
        output = config.args.get("output", input_file.replace("raw", "processed"))
        cmd_args = ["preprocess", "--input_file", input_file, "--output", output]
        
    elif config.command_type == "analyze":
        input_file = config.args.get("input_file")
        cmd_args = ["analyze", "--input_file", input_file, "--bootstrap"]
        
    else:
        raise HTTPException(status_code=400, detail="Unknown command type")
        
    run_id = manager.start_run(cmd_args, config.command_type, config.args)
    return {"run_id": run_id, "status": "started"}

@app.websocket("/ws/runs/{run_id}/logs")
async def websocket_logs(websocket: WebSocket, run_id: str):
    await websocket.accept()
    
    if run_id not in runs_store:
        await websocket.close(code=4004)
        return
        
    run_data = runs_store[run_id]
    
    # Send existing logs
    for line in run_data["logs"]:
        await websocket.send_text(line)
        
    # Stream new logs
    # Simple polling for this demo since we store in list
    # In prod, use asyncio Queue / PubSub
    last_idx = len(run_data["logs"])
    
    try:
        while run_data["status"] == "running":
            current_len = len(run_data["logs"])
            if current_len > last_idx:
                for i in range(last_idx, current_len):
                    await websocket.send_text(run_data["logs"][i])
                last_idx = current_len
            await asyncio.sleep(0.5)
            
        # Send remaining
        current_len = len(run_data["logs"])
        if current_len > last_idx:
            for i in range(last_idx, current_len):
                await websocket.send_text(run_data["logs"][i])
                
        await websocket.send_text(f"[System] Run finished with code {run_data.get('return_code')}")
        
    except Exception as e:
        print(f"WS Error: {e}")
        pass

@app.get("/api/ledger")
async def get_ledger():
    ledger_path = "ledger/runs_ledger.csv"
    if not os.path.exists(ledger_path):
        return []
        
    rows = []
    with open(ledger_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows

@app.post("/api/unblind")
async def unblind(req: UnblindRequest):
    # Simple mock check
    if req.admin_token != "admin-secret-123":
        raise HTTPException(status_code=403, detail="Invalid token")
        
    # Call CLI unblind
    # manager.start_run(["unblind", "--token", req.admin_token], "unblind")
    return {"status": "Unblind triggered defined in CLI"}
    
import uuid
import sys
