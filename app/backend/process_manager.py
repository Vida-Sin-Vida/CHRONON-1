import asyncio
import subprocess
import os
import threading
import uuid
import time
from datetime import datetime
import json
import logging

# In-memory store for runs
# In a real app, this would be a database or persisted file
# We will sync with ledger csv on startup
runs_store = {}

class RunManager:
    def __init__(self):
        self.active_processes = {}
        self.log_queues = {} # rund_id -> list of log lines
        
    def start_run(self, command_args, run_type, config={}):
        run_id = str(uuid.uuid4())[:8]
        timestamp = datetime.utcnow().isoformat()
        
        # Prepare command
        # Assumes running from root of repo
        # python -m chronon_core.cli <command_args>
        cmd = [sys.executable, "-m", "chronon_core.cli"] + command_args
        
        # Store metadata
        runs_store[run_id] = {
            "id": run_id,
            "type": run_type,
            "status": "running",
            "timestamp": timestamp,
            "command": " ".join(cmd),
            "config": config,
            "logs": []
        }
        
        # Start subprocess
        # We need unbuffered output
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        env["PYTHONPATH"] = os.getcwd()
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, # Merge stderr to stdout
            text=True,
            bufsize=1,
            env=env,
            cwd=os.getcwd()
        )
        
        self.active_processes[run_id] = process
        
        # Start log reader thread
        t = threading.Thread(target=self._log_reader, args=(run_id, process))
        t.daemon = True
        t.start()
        
        return run_id

    def _log_reader(self, run_id, process):
        for line in iter(process.stdout.readline, ''):
            if line:
                runs_store[run_id]["logs"].append(line)
                # Keep active logs for WS
                # In real app, push to pubsub
        
        process.stdout.close()
        return_code = process.wait()
        
        runs_store[run_id]["status"] = "completed" if return_code == 0 else "failed"
        runs_store[run_id]["return_code"] = return_code
        del self.active_processes[run_id]

import sys
manager = RunManager()
