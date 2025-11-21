#!/bin/bash
# ==========================================
# Monitor All Services
# ==========================================
# Shows status and recent logs for all services

NAMESPACE="reflection"

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Reflection Services - Monitor${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Get all pods
echo -e "${CYAN}📊 Pod Status:${NC}"
kubectl get pods -n $NAMESPACE -o wide
echo ""

# Get all services
echo -e "${CYAN}🌐 Services:${NC}"
kubectl get services -n $NAMESPACE
echo ""

# Get ingress
echo -e "${CYAN}🔀 Ingress:${NC}"
kubectl get ingress -n $NAMESPACE
echo ""

# Show recent logs for each service
SERVICES=("frontend" "login-management" "file-parsing" "resources" "speechtotext")

echo -e "${CYAN}📋 Recent Logs (last 5 lines per service):${NC}"
echo ""

for service in "${SERVICES[@]}"; do
    pod=$(kubectl get pods -n $NAMESPACE -l app=$service -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
    
    if [ -n "$pod" ]; then
        status=$(kubectl get pod -n $NAMESPACE $pod -o jsonpath='{.status.phase}')
        
        if [ "$status" == "Running" ]; then
            echo -e "${GREEN}▶ ${service} (${pod}):${NC}"
            kubectl logs -n $NAMESPACE $pod --tail=5 2>/dev/null | sed 's/^/  /'
        else
            echo -e "${YELLOW}⚠ ${service} (${pod}) - Status: ${status}${NC}"
        fi
    else
        echo -e "${RED}✗ ${service} - No pods found${NC}"
    fi
    echo ""
done

echo -e "${BLUE}========================================${NC}"
echo -e "${YELLOW}💡 Tips:${NC}"
echo "  View logs:      ./view-logs.sh <service-name>"
echo "  Follow logs:    ./view-logs.sh <service-name> --follow"
echo "  All pods:       kubectl get pods -n reflection"
echo "  Describe pod:   kubectl describe pod -n reflection <pod-name>"
echo ""
