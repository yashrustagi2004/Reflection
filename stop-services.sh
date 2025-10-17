#!/bin/bash
# Script to stop all microservices

echo "🛑 Stopping Reflection Microservices..."
echo ""

# Function to stop a service
stop_service() {
    SERVICE_NAME=$1
    PID_FILE="logs/$SERVICE_NAME.pid"
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "Stopping $SERVICE_NAME (PID: $PID)..."
            kill $PID
            rm "$PID_FILE"
            echo "✅ $SERVICE_NAME stopped"
        else
            echo "⚠️  $SERVICE_NAME is not running"
            rm "$PID_FILE"
        fi
    else
        echo "⚠️  No PID file found for $SERVICE_NAME"
    fi
}

# Stop all services
stop_service "frontend"
stop_service "login-management"
stop_service "file-parsing"
stop_service "question-answer-generation"
stop_service "answer-analysis"
stop_service "resources"

echo ""
echo "✅ All services stopped!"
