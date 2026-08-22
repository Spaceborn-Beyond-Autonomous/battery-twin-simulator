#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "=== BatteryTwin Simulation Suite Startup ==="

# 1. Check and Install Python Requirements
if [ -f "requirements.txt" ]; then
    echo "[1/4] Checking Python dependencies..."
    pip install -r requirements.txt --quiet
else
    echo "[Warning] requirements.txt not found. Skipping automated pip install."
fi

# 2. Check and Install Node.js Frontend Dependencies inside dashboard/frontend
FRONTEND_DIR="dashboard/frontend"

if [ -d "$FRONTEND_DIR" ]; then
    if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
        echo "[2/4] Node modules missing. Installing frontend packages in $FRONTEND_DIR..."
        cd "$FRONTEND_DIR" && npm install && cd ../..
    else
        echo "[2/4] Node modules already installed."
    fi
else
    echo "[Error] Frontend directory '$FRONTEND_DIR' not found!"
    exit 1
fi

# 3. Start the FastAPI backend from dashboard/backend in the background
echo "[3/4] Launching FastAPI Backend..."
cd dashboard/backend
python3 -m uvicorn main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!
cd ../..

# Wait 2 seconds for backend to initialize
sleep 2

# 4. Start the React frontend from dashboard/frontend
echo "[4/4] Launching React Vite Frontend..."
cd "$FRONTEND_DIR" && npm run dev &
FRONTEND_PID=$!
cd ../..

echo "=== BatteryTwin is Running ==="
echo "Access the dashboard at: http://localhost:5173"
echo "Press Ctrl+C to stop all services."

# Trap Ctrl+C (SIGINT) so it cleanly kills both background jobs
trap "echo -e '\nShutting down BatteryTwin Simulator...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" SIGINT

# Keep script running to maintain background jobs and listen for Ctrl+C
wait
