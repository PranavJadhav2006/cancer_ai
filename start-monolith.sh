#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Starting RESONANCE Backend Server (Port 8000)..."
cd /app/Backend
node server.js &
BACK_PID=$!

echo "\n============================================="
echo "WARNING: AI ENGINE STARTUP IS TEMPORARILY DISABLED FOR DIAGNOSTICS."
echo "If your website and signup load flawlessly now, it 100% confirms that Python was starving your Render instance of memory, causing the server freezes. You will need to upgrade Render RAM to turn AI back on."
echo "=============================================\n"
# cd /app/ai_engine
# python app.py &
# AI_PID=$!

# Wait ONLY for the Node server. If Node stays alive, the UI stays alive!
wait $BACK_PID

echo "Backend server exited. Shutting down container..."
exit 1
