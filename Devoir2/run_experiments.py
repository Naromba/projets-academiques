#!/usr/bin/env python3
"""
Run experiments for the assignment.

- Scenarios 1..3 (single run)
- Test 4: set TIMEOUT_MS=200 and vary delaiMax in [50,180,300], 3 runs each

Produces logs/*.txt and results.csv
"""
import os
import csv
from pathlib import Path
from contextlib import redirect_stdout
import importlib

ROOT = Path(__file__).parent
LOGS = ROOT / 'logs'
LOGS.mkdir(exist_ok=True)
OUTCSV = ROOT / 'results.csv'

import code.protocole as protocole

results = []

# Helper to run and capture output by calling run_scenario inside the module
def run_and_capture(name, func, *args, **kwargs):
    logfile = LOGS / f"{name}.txt"
    with open(logfile, 'w', encoding='utf-8') as f:
        with redirect_stdout(f):
            func(*args, **kwargs)
    # parse logfile to extract metrics
    metrics = {
        'log': str(logfile),
        'frames_envoyees': None,
        'frames_retransmises': None,
        'acks_recus': None,
        'duree_s': None,
        'integrity': None,
    }
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'Frames envoyées' in line:
                metrics['frames_envoyees'] = int(line.split(':')[-1].strip())
            if 'Frames retransmises' in line:
                metrics['frames_retransmises'] = int(line.split(':')[-1].strip())
            if 'ACK reçus' in line:
                metrics['acks_recus'] = int(line.split(':')[-1].strip())
            if 'Durée totale' in line:
                parts = line.split(':')[-1].strip().split()
                try:
                    metrics['duree_s'] = float(parts[0])
                except Exception:
                    metrics['duree_s'] = None
            if 'Intégrité message' in line:
                metrics['integrity'] = line.split(':')[-1].strip()
    return metrics

# 1) Scenarios 1..3
print('Running scenarios 1..3')
for sc in (1,2,3):
    name = f'sc_{sc}_run1'
    print('->', name)
    # Ensure module globals are original
    importlib.reload(protocole)
    met = run_and_capture(name, protocole.run_scenario, sc)
    met.update({'scenario': sc, 'run': 1, 'timeout_ms': getattr(protocole, 'TIMEOUT_MS', None), 'delaiMax': protocole.SCENARIOS[sc]['delaiMax'], 'probErreur': protocole.SCENARIOS[sc]['probErreur'], 'probPerte': protocole.SCENARIOS[sc]['probPerte']})
    results.append(met)

# 2) Test 4: timeout fixed = 200, vary delaiMax
print('Running test 4 (timeout fixed = 200)')
for delai in (50, 180, 300):
    for run in (1,2,3):
        name = f'test4_del{delai}_run{run}'
        print('->', name)
        importlib.reload(protocole)
        # force TIMEOUT_MS
        protocole.TIMEOUT_MS = 200
        # set delaiMax of scenario 2
        protocole.SCENARIOS[2]['delaiMax'] = delai
        met = run_and_capture(name, protocole.run_scenario, 2)
        met.update({'scenario': 2, 'run': run, 'timeout_ms': protocole.TIMEOUT_MS, 'delaiMax': delai, 'probErreur': protocole.SCENARIOS[2]['probErreur'], 'probPerte': protocole.SCENARIOS[2]['probPerte']})
        results.append(met)

# Write results.csv
fieldnames = ['scenario','run','log','timeout_ms','delaiMax','probErreur','probPerte','frames_envoyees','frames_retransmises','acks_recus','duree_s','integrity']
with open(OUTCSV, 'w', newline='', encoding='utf-8') as cf:
    writer = csv.DictWriter(cf, fieldnames=fieldnames)
    writer.writeheader()
    for r in results:
        writer.writerow({k: r.get(k, '') for k in fieldnames})

print('All runs complete. Logs in logs/, summary in results.csv')
