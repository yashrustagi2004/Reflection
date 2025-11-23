#!/bin/bash

# MongoDB & Mongo Express Deployment Script
# Date: November 13, 2025

set -e

echo "🗄️ Deploying MongoDB & Mongo Express to Kubernetes..."
echo ""

# Check if kubectl is working
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Kubernetes cluster not accessible. Start Docker Desktop first."
    exit 1
fi

# Check if namespace exists
if ! kubectl get namespace reflection &> /dev/null; then
    echo "❌ Namespace 'reflection' not found. Create it first:"
    echo "   kubectl create namespace reflection"
    exit 1
fi

echo "✅ Kubernetes cluster is accessible"
echo "✅ Namespace 'reflection' exists"
echo ""

# Step 1: Create persistent storage directory
echo "📁 Step 1/9: Creating persistent storage directory..."
sudo mkdir -p /opt/kubernetes-data/mongodb
sudo chmod 777 /opt/kubernetes-data/mongodb
echo "   ✅ Created: /opt/kubernetes-data/mongodb"
echo ""

# Step 2: Create MongoDB credentials secret
echo "🔐 Step 2/9: Creating MongoDB credentials secret..."
if kubectl get secret mongodb-credentials -n reflection &> /dev/null; then
    echo "   ℹ️  Secret already exists, skipping creation"
else
    kubectl create secret generic mongodb-credentials \
      --namespace=reflection \
      --from-literal=MONGO_INITDB_ROOT_USERNAME=admin \
      --from-literal=MONGO_INITDB_ROOT_PASSWORD=admin123
    echo "   ✅ MongoDB credentials secret created"
fi
echo ""

# Step 3: Deploy MongoDB StatefulSet (with auto-created PVCs)
echo "🚀 Step 3/7: Deploying MongoDB StatefulSet..."
kubectl apply -f k8s/mongodb-deployment.yaml
echo "   ✅ MongoDB StatefulSet and headless service created"
echo ""

# Step 4: Wait for MongoDB to be ready
echo "⏳ Step 4/7: Waiting for MongoDB pod to be ready (max 30s)..."
if kubectl wait --for=condition=ready pod -l app=mongodb -n reflection --timeout=30s; then
    echo "   ✅ MongoDB is ready!"
else
    echo "   ⚠️  MongoDB is taking longer than expected. Check logs:"
    echo "      kubectl logs -n reflection -l app=mongodb"
fi
echo ""

# Step 5: Apply mongo express config
echo "🚀 Step 5/7: Applying Mongo Express ConfigMap..."
kubectl apply -f k8s/mongo-express-configmap.yaml
echo "   ✅ Mongo Express ConfigMap applied"
echo ""

# Step 6: Deploy Mongo Express
echo "🚀 Step 6/7: Deploying Mongo Express..."
kubectl apply -f k8s/mongo-express-deployment.yaml
echo "   ✅ Mongo Express deployment and service created"
echo ""

# Wait for Mongo Express
echo "⏳ Waiting for Mongo Express to be ready (max 60s)..."
if kubectl wait --for=condition=ready pod -l app=mongo-express -n reflection --timeout=60s; then
    echo "   ✅ Mongo Express is ready!"
else
    echo "   ⚠️  Mongo Express is taking longer than expected. Check logs:"
    echo "      kubectl logs -n reflection -l app=mongo-express"
fi
echo ""

# Step 7: Initialize Resources Data
echo "📚 Step 7/7: Initializing resources data..."
if [ -f "services/resources/data.py" ]; then
    echo "   📝 Copying resources data script to MongoDB pod..."
    
    # Get MongoDB pod name
    MONGO_POD=$(kubectl get pod -n reflection -l app=mongodb -o jsonpath='{.items[0].metadata.name}')
    
    if [ -z "$MONGO_POD" ]; then
        echo "   ⚠️  Could not find MongoDB pod, skipping data initialization"
    else
        # Copy data.py to pod
        kubectl cp services/resources/data.py reflection/$MONGO_POD:/tmp/data.py
        
        # Get DATABASE_NAME from ConfigMap
        DB_NAME=$(kubectl get configmap reflection-config -n reflection -o jsonpath='{.data.DATABASE_NAME}')
        echo "   📊 Using database: $DB_NAME"
        
        # Get MongoDB credentials from Kubernetes secret
        MONGO_USER=$(kubectl get secret mongodb-credentials -n reflection -o jsonpath='{.data.MONGO_INITDB_ROOT_USERNAME}' | base64 -d)
        MONGO_PASS=$(kubectl get secret mongodb-credentials -n reflection -o jsonpath='{.data.MONGO_INITDB_ROOT_PASSWORD}' | base64 -d)
        
        # Install pymongo in the pod and run the script
        echo "   🔄 Running data population script..."
        kubectl exec -n reflection $MONGO_POD -- bash -c "
            apt-get update -qq > /dev/null 2>&1 && 
            apt-get install -y python3-pip -qq > /dev/null 2>&1 && 
            pip3 install pymongo --quiet > /dev/null 2>&1 &&
            export MONGODB_URI='mongodb://$MONGO_USER:$MONGO_PASS@localhost:27017/' &&
            export DATABASE_NAME='$DB_NAME' &&
            python3 /tmp/data.py
        " 2>&1 | grep -v "debconf\|WARNING\|Collecting\|Downloading\|Installing" || true
        
        if [ $? -eq 0 ]; then
            echo "   ✅ Resources data initialized successfully!"
        else
            echo "   ⚠️  Resources data initialization may have had issues"
            echo "   💡 You can manually run: python3 services/resources/data.py"
        fi
    fi
else
    echo "   ⚠️  services/resources/data.py not found, skipping"
fi
echo ""

# Display status
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ DEPLOYMENT COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Show pod status
echo "📊 Pod Status:"
kubectl get pods -n reflection -l app=mongodb
kubectl get pods -n reflection -l app=mongo-express
echo ""

# Show service status
echo "🌐 Service Status:"
kubectl get svc -n reflection -l app=mongodb
kubectl get svc -n reflection -l app=mongo-express
echo ""

# Access instructions
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 How to Access:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Get credentials from secret for display
DISPLAY_USER=$(kubectl get secret mongodb-credentials -n reflection -o jsonpath='{.data.MONGO_INITDB_ROOT_USERNAME}' | base64 -d)
DISPLAY_PASS=$(kubectl get secret mongodb-credentials -n reflection -o jsonpath='{.data.MONGO_INITDB_ROOT_PASSWORD}' | base64 -d)
DISPLAY_DB=$(kubectl get configmap reflection-config -n reflection -o jsonpath='{.data.DATABASE_NAME}')

echo "📊 Mongo Express GUI:"
echo "   URL: http://localhost:8081"
echo "   Username: $DISPLAY_USER"
echo "   Password: $DISPLAY_PASS"
echo ""
echo "   If not accessible, try port-forwarding:"
echo "   kubectl port-forward -n reflection svc/mongo-express-service 8081:8081"
echo ""
echo "🗄️ MongoDB Connection:"
echo "   Host: mongodb-service"
echo "   Port: 27017"
echo "   Database: $DISPLAY_DB"
echo "   Username: $DISPLAY_USER"
echo "   Password: $DISPLAY_PASS"
echo "   Connection String: mongodb://$DISPLAY_USER:$DISPLAY_PASS@mongodb-service:27017/"
echo ""
echo "🔍 MongoDB Shell Access (StatefulSet pod):"
echo "   kubectl exec -it -n reflection mongodb-0 -- mongosh -u $DISPLAY_USER -p $DISPLAY_PASS"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📖 For more details, see: docs/MONGODB_ACCESS_GUIDE.md"
echo ""
