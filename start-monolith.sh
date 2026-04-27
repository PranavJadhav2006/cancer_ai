#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Starting RESONANCE AI Engine (Port 5000)..."
cd /app/ai_engine
python app.py &
AI_PID=$!

echo "Starting RESONANCE Backend Server (Port 8000)..."
cd /app/Backend
node server.js &
BACK_PID=$!

# Wait for any process to exit
wait -n

echo "One of the processes exited. Shutting down container..."
kill $AI_PID
kill $BACK_PID
exit 1
