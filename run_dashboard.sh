#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "=== BatteryTwin Simulation Suite Startup ==="

# --- ADDED: ROS 2 Build & Source Step ---
if [ -f "/opt/ros/humble/setup.bash" ]; then
    echo "[1/5] Sourcing ROS 2 Humble & Building Workspace..."
    source /opt/ros/humble/setup.bash
    
    # Build only the required packages to avoid Gazebo errors
    colcon build --packages-select batterytwin_msgs batterytwin_core
    
    # Source the newly built local overlay
    source install/setup.bash
else
    echo "[Warning] ROS 2 Humble not found. Skipping build step."
fi

# --- ADDED: Python Environment Fix ---
# Force system Python (3.10) to prevent Miniconda conflicts with ROS 2
if [ -x "/usr/bin/python3" ]; then
    PYTHON_CMD="/usr/bin/python3"
else
    PYTHON_CMD="python3"
fi

# 1. Check and Install Python Requirements
if [ -f "requirements.txt" ]; then
    echo "[2/5] Checking Python dependencies..."
    $PYTHON_CMD -m pip install -r requirements.txt --quiet
    $PYTHON_CMD -m pip install "uvicorn[standard]" websockets --quiet
else
    echo "[Warning] requirements.txt not found. Skipping automated pip install."
fi

# 2. Check and Install Node.js Frontend Dependencies inside dashboard/frontend
FRONTEND_DIR="dashboard/frontend"

if [ -d "$FRONTEND_DIR" ]; then
    if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
        echo "[3/5] Node modules missing. Installing frontend packages in $FRONTEND_DIR..."
        cd "$FRONTEND_DIR" && npm install && cd ../..
    else
        echo "[3/5] Node modules already installed."
    fi
else
    echo "[Error] Frontend directory '$FRONTEND_DIR' not found!"
    exit 1
fi

# 3. Start the FastAPI backend from dashboard/backend in the background
echo "[4/5] Launching FastAPI Backend..."
cd dashboard/backend
$PYTHON_CMD -m uvicorn main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!
cd ../..

# Wait 2 seconds for backend to initialize
sleep 2

# 4. Start the React frontend from dashboard/frontend
echo "[5/5] Launching React Vite Frontend..."
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
