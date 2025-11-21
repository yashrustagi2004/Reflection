#!/bin/bash
# ==========================================
# View Logs - Quick Access to Service Logs
# ==========================================
# Usage: ./view-logs.sh [service-name] [options]
# Example: ./view-logs.sh frontend
# Example: ./view-logs.sh login-management --follow
# Example: ./view-logs.sh file-parsing --tail 100

NAMESPACE="reflection"

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Reflection Services - Log Viewer${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to show logs for a service
show_logs() {
    local service=$1
    shift
    local options="$@"
    
    echo -e "${GREEN}📋 Logs for: ${service}${NC}"
    echo ""
    
    # Get the deployment name
    local deployment="${service}-deployment"
    
    # Get the first pod for this deployment
    local pod=$(kubectl get pods -n $NAMESPACE -l app=$service -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
    
    if [ -z "$pod" ]; then
        echo -e "${RED}❌ No pods found for service: ${service}${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}Pod: ${pod}${NC}"
    echo ""
    
    # Show logs
    kubectl logs -n $NAMESPACE $pod $options
}

# Function to list all services
list_services() {
    echo -e "${GREEN}Available services:${NC}"
    echo "  - frontend"
    echo "  - login-management"
    echo "  - file-parsing"
    echo "  - qa-generation"
    echo "  - resources"
    echo "  - speechtotext"
    echo "  - mongodb"
    echo "  - mongo-express"
    echo ""
    echo -e "${YELLOW}Usage:${NC}"
    echo "  ./view-logs.sh <service-name> [options]"
    echo ""
    echo -e "${YELLOW}Options:${NC}"
    echo "  --follow, -f          Follow log output (live tail)"
    echo "  --tail N              Show last N lines (default: all)"
    echo "  --since TIME          Show logs since time (e.g., 5m, 1h)"
    echo "  --previous            Show logs from previous container instance"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  ./view-logs.sh frontend"
    echo "  ./view-logs.sh login-management --follow"
    echo "  ./view-logs.sh file-parsing --tail 50"
    echo "  ./view-logs.sh resources --since 10m"
}

# Main script
if [ $# -eq 0 ]; then
    list_services
    exit 0
fi

SERVICE=$1
shift
OPTIONS="$@"

show_logs $SERVICE $OPTIONS
