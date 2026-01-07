#!/bin/bash
pkill -9 uvicorn
sleep 2
cd /home/cyberdude/Documents/Projects/CA-final
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 > /tmp/taxease-api.log 2>&1 &
echo "API restarting... waiting 7 seconds"
sleep 7
echo "API should be ready"
