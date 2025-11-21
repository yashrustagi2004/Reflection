#!/bin/bash
# ==========================================
# Access Kubernetes Dashboard
# ==========================================
# This script helps you access the Kubernetes Dashboard

NAMESPACE="kubernetes-dashboard"

echo "🎨 Kubernetes Dashboard Access"
echo "=========================================="
echo ""

# Check if dashboard is running
echo "📊 Checking dashboard status..."
DASHBOARD_POD=$(kubectl get pods -n $NAMESPACE -l k8s-app=kubernetes-dashboard -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

if [ -z "$DASHBOARD_POD" ]; then
    echo "❌ Dashboard not found. Installing..."
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml
    echo "⏳ Waiting for dashboard to be ready..."
    kubectl wait --namespace $NAMESPACE \
        --for=condition=ready pod \
        --selector=k8s-app=kubernetes-dashboard \
        --timeout=90s
    echo "✅ Dashboard installed!"
else
    echo "✅ Dashboard is running"
fi

echo ""
echo "🔑 Getting access token..."
TOKEN=$(kubectl -n $NAMESPACE create token admin-user 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "⚠️  Admin user not found. Creating..."
    kubectl apply -f k8s/dashboard-admin.yaml
    sleep 2
    TOKEN=$(kubectl -n $NAMESPACE create token admin-user)
fi

echo ""
echo "=========================================="
echo "✅ Dashboard is ready!"
echo "=========================================="
echo ""
echo "📋 Access Token (copy this):"
echo "----------------------------------------"
echo "$TOKEN"
echo "----------------------------------------"
echo ""
echo "🌐 Starting port-forward..."
echo "   Dashboard will be available at:"
echo "   https://localhost:8443"
echo ""
echo "⚠️  IMPORTANT:"
echo "   1. Your browser will show a security warning (this is normal)"
echo "   2. Click 'Advanced' and 'Proceed to localhost'"
echo "   3. Select 'Token' as login method"
echo "   4. Paste the token above"
echo ""
echo "Press Ctrl+C to stop the dashboard"
echo ""

# Start port-forward
kubectl port-forward -n $NAMESPACE service/kubernetes-dashboard 8443:443
