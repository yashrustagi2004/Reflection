#!/bin/bash
# Script to start all microservices

echo "🚀 Starting Reflection Microservices..."
echo ""

# Check if .env file exists
if [ ! -f services/.env ]; then
    echo ".env file not found. Copying from .env.example..."
    cp services/.env.example services/.env
    echo "Please configure services/.env with your API keys and settings!"
    exit 1
fi

# Function to start a service in the background
start_service() {
    SERVICE_NAME=$1
    PORT=$2
    SERVICE_DIR="services/$SERVICE_NAME"
    
    echo "Starting $SERVICE_NAME on port $PORT..."
    
    cd "$SERVICE_DIR"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "  Creating virtual environment for $SERVICE_NAME..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment and install dependencies
    source venv/bin/activate
    pip install -q -r requirements.txt
    
    # Start the service
    python app.py > "../../logs/$SERVICE_NAME.log" 2>&1 &
    echo $! > "../../logs/$SERVICE_NAME.pid"
    
    deactivate
    cd ../..
    
    echo "✅ $SERVICE_NAME started (PID: $(cat logs/$SERVICE_NAME.pid))"
}

# Create logs directory
mkdir -p logs

# Start all services
start_service "login-management" 5001
sleep 2

start_service "file-parsing" 5002
sleep 2

start_service "question-answer-generation" 5003
sleep 2

start_service "answer-analysis" 5004
sleep 2

start_service "resources" 5005
sleep 2

start_service "frontend" 5000

echo ""
echo "✅ All services started!"
echo ""
echo "📝 Service URLs:"
echo "   Frontend:                  http://localhost:5000"
echo "   Login Management:          http://localhost:5001"
echo "   File Parsing:              http://localhost:5002"
echo "   Q&A Generation:            http://localhost:5003"
echo "   Answer Analysis:           http://localhost:5004"
echo "   Resources:                 http://localhost:5005"
echo ""
echo "📋 Logs are available in the logs/ directory"
echo "🛑 To stop all services, run: ./stop-services.sh"
