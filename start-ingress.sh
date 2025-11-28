#!/bin/bash
# ==========================================
# Start All Port Forwards
# ==========================================
# This script creates port forwards for:
# - Frontend (port 5000)
# - All microservices (direct access on their ports)
# - Mongo Express (port 8081) - Database UI
# Runs in background (detached mode)

echo "🚀 Starting Port Forwards for all services..."
echo ""

# Kill any existing port-forwards
echo "🧹 Cleaning up existing port-forwards..."
pkill -f "port-forward.*reflection" 2>/dev/null
pkill -f "port-forward.*ingress-nginx" 2>/dev/null
sleep 1

# Start port-forward for frontend (direct service access)
echo "📡 Starting Frontend Service (port 5000)..."
nohup kubectl port-forward -n reflection service/frontend-service 5000:80 > /tmp/frontend-port-forward.log 2>&1 &

# Start port-forwards for all microservices
echo "📡 Starting Login Management Service (port 5001)..."
nohup kubectl port-forward -n reflection service/login-management-service 5001:5001 > /tmp/login-port-forward.log 2>&1 &

echo "📡 Starting File Parsing Service (port 5002)..."
nohup kubectl port-forward -n reflection service/file-parsing-service 5002:5002 > /tmp/file-parsing-port-forward.log 2>&1 &

echo "📡 Starting QA Generation Service (port 5003)..."
nohup kubectl port-forward -n reflection service/qa-generation-service 5003:5003 > /tmp/qa-generation-port-forward.log 2>&1 &

echo "📡 Starting Speech to Text Service (port 5004)..."
nohup kubectl port-forward -n reflection service/speechtotext-service 5004:5004 > /tmp/speechtotext-port-forward.log 2>&1 &

echo "📡 Starting Resources Service (port 5005)..."
nohup kubectl port-forward -n reflection service/resources-service 5005:5005 > /tmp/resources-port-forward.log 2>&1 &

echo "📡 Starting Mongo Express (port 8081)..."
nohup kubectl port-forward -n reflection service/mongo-express-service 8081:8081 > /tmp/mongo-express-port-forward.log 2>&1 &

# Wait for port-forwards to initialize
echo ""
echo "⏳ Waiting for port-forwards to initialize..."
sleep 3

# Check status
echo ""
echo "📊 Port Forward Status:"
echo "================================================"

FAILED=0

if pgrep -f "port-forward.*frontend-service.*5000:80" > /dev/null; then
    echo "✅ Frontend:           http://localhost:5000"
else
    echo "❌ Frontend:           FAILED"
    FAILED=1
fi

if pgrep -f "port-forward.*login-management-service.*5001:5001" > /dev/null; then
    echo "✅ Login Management:   http://localhost:5001"
else
    echo "❌ Login Management:   FAILED"
    FAILED=1
fi

if pgrep -f "port-forward.*file-parsing-service.*5002:5002" > /dev/null; then
    echo "✅ File Parsing:       http://localhost:5002"
else
    echo "❌ File Parsing:       FAILED"
    FAILED=1
fi

if pgrep -f "port-forward.*qa-generation-service.*5003:5003" > /dev/null; then
    echo "✅ QA Generation:      http://localhost:5003"
else
    echo "❌ QA Generation:      FAILED"
    FAILED=1
fi

if pgrep -f "port-forward.*speechtotext-service.*5004:5004" > /dev/null; then
    echo "✅ Speech to Text:     http://localhost:5004"
else
    echo "❌ Speech to Text:     FAILED"
    FAILED=1
fi

if pgrep -f "port-forward.*resources-service.*5005:5005" > /dev/null; then
    echo "✅ Resources:          http://localhost:5005"
else
    echo "❌ Resources:          FAILED"
    FAILED=1
fi

if pgrep -f "port-forward.*mongo-express-service.*8081:8081" > /dev/null; then
    echo "✅ Mongo Express:      http://localhost:8081 (admin/admin123)"
else
    echo "❌ Mongo Express:      FAILED"
    FAILED=1
fi

echo "================================================"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "🎉 All port forwards started successfully!"
    echo ""
    echo " Test with:"
    echo "   curl http://localhost:5001/health  # Login Management"
    echo "   curl http://localhost:5002/health  # File Parsing"
    echo "   curl http://localhost:5003/health  # QA Generation"
    echo "   curl http://localhost:5004/health  # Speech to Text"
    echo "   curl http://localhost:5005/health  # Resources"
    echo "   curl http://localhost:5000/health  # Frontend"
    echo ""
    echo "🗄️  Mongo Express:  http://localhost:8081"
    echo "   Username: admin  Password: admin123"
    echo ""
    echo "Logs in /tmp/*-port-forward.log"
    echo "To stop all: pkill -f 'port-forward'"
else
    echo "Some port forwards failed to start"
    echo "Check logs in /tmp/*-port-forward.log"
    exit 1
fi
