#!/bin/bash

echo "🔄 Restarting Client Backend and Testing OTP..."
echo ""

# Step 1: Stop the backend
echo "1️⃣ Stopping backend..."
PID=$(ps aux | grep "uvicorn main:app.*8001" | grep -v grep | awk '{print $2}')
if [ ! -z "$PID" ]; then
    echo "   Found process: $PID"
    kill $PID
    sleep 3
    echo "   ✅ Backend stopped"
else
    echo "   ℹ️ No backend process found"
fi

# Step 2: Start the backend
echo ""
echo "2️⃣ Starting backend..."
cd client_side

# Create logs directory if it doesn't exist
mkdir -p ../logs

# Start backend in background
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload > ../logs/client_backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../logs/client_backend.pid

echo "   Backend started (PID: $BACKEND_PID)"
echo "   Waiting for backend to be ready..."

# Wait for backend to start
for i in {1..10}; do
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        echo "   ✅ Backend is ready!"
        break
    fi
    sleep 1
    echo -n "."
done
echo ""

# Step 3: Test OTP
echo ""
echo "3️⃣ Testing OTP verification..."
cd ..
./test_otp.sh

echo ""
echo "📋 Check backend logs:"
echo "   tail -f logs/client_backend.log"


