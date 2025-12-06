
from flask import Flask, render_template, jsonify
import csv
import pandas as pd
import os
import datetime

app = Flask(__name__)

LEDGER_PATH = os.path.join(os.path.expanduser("~"), ".chronon_ledger.csv")

def read_ledger():
    runs = []
    if os.path.exists(LEDGER_PATH):
        with open(LEDGER_PATH, 'r') as f:
            reader = csv.DictReader(f)
            runs = list(reader)
            # Sort by timestamp desc
            runs.reverse()
    return runs

@app.route('/')
def index():
    runs = read_ledger()
    # Calculate stats
    total = len(runs)
    passed = sum(1 for r in runs if r.get('verdict') == 'PASS')
    failed = total - passed
    
    return render_template('index.html', runs=runs, stats={'total': total, 'pass': passed, 'fail': failed})

@app.route('/api/runs')
def api_runs():
    return jsonify(read_ledger())

@app.route('/api/status')
def api_status():
    runs = read_ledger()
    if not runs:
        return jsonify({"status": "idle"})
    last = runs[0]
    return jsonify({
        "last_run": last.get('timestamp'),
        "verdict": last.get('verdict'),
        "id": last.get('run_id')
    })

if __name__ == '__main__':
    print("Starting CHRONON Dashboard on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
