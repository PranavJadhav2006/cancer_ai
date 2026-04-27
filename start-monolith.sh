#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Starting RESONANCE Backend Server (Port 8000)..."
cd /app/Backend
node server.js &
BACK_PID=$!

echo "Starting RESONANCE AI Engine (Port 5000)..."
cd /app/ai_engine
# If python crashes (e.g. Out of Memory on Render free tier), just print an error instead of taking the whole container down
python app.py || echo "WARNING: AI ENGINE CRASHED! (Likely Render Out Of Memory)" &
AI_PID=$!

# Wait ONLY for the Node server. If Node stays alive, the UI stays alive!
wait $BACK_PID

echo "Backend server exited. Shutting down container..."
kill $AI_PID || true
exit 1
