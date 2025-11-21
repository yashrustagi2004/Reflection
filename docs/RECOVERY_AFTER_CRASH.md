# Recovery Guide After System Crash

**Date:** November 13, 2025  
**Issue:** Namespace and configurations lost after system crash  
**Status:** 🚨 CRITICAL - Immediate Action Required

---

## 🔍 What Happened?

When your system crashed, one of these occurred:

1. **Docker Desktop Kubernetes was reset** - Lost all cluster data
2. **Kubernetes etcd database corrupted** - Cluster state lost
3. **Docker Desktop reinitialized** - Started fresh cluster
4. **VM backing Docker Desktop was reset** - All data gone

**Result:** All your Kubernetes resources (namespace, deployments, configmaps, secrets) are **GONE** ❌

---

## ⚡ Immediate Verification Steps

### Step 1: Check What Survived

```bash
# Check if Kubernetes is running
kubectl cluster-info

# List all namespaces
kubectl get namespaces

# Expected: Only default namespaces (kube-system, kube-public, etc.)
# Missing: reflection namespace ❌

# Check if any deployments exist
kubectl get deployments --all-namespaces

# Check if any pods exist
kubectl get pods --all-namespaces

# Check Docker images (these should still exist)
docker images | grep reflection
```

### Step 2: Verify Docker Desktop Status

```bash
# Check Docker status
docker info

# Check Kubernetes nodes
kubectl get nodes

# Expected: 1-3 nodes in Ready state
# If no nodes or not ready, Docker Desktop needs restart
```

---

## 🔧 Recovery Options

### Option 1: Quick Redeployment (Recommended)

Since you still have:
- ✅ Source code
- ✅ Docker images (if not deleted)
- ✅ Deployment YAML files
- ✅ Credentials file

You can **redeploy everything** in ~15 minutes.

### Option 2: Restore from Backup

If you had backups (which we didn't set up yet), you could restore.

### Option 3: Infrastructure as Code

This crash shows why we need **GitOps** - all configs in version control.

---

## 🚀 Quick Redeployment Guide

Follow these steps to get back up and running:

### Step 1: Recreate Namespace

```bash
# Create namespace
kubectl create namespace reflection

# Set as default
kubectl config set-context --current --namespace=reflection

# Verify
kubectl get namespace reflection
```

### Step 2: Recreate ConfigMap

```bash
# Navigate to project directory
cd ~/Desktop/Study/7th_sem/capstone2/Reflection/Reflection

# Apply ConfigMap (if you created the file before)
kubectl apply -f k8s/configmap.yaml

# Or create it inline
kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: reflection-config
  namespace: reflection
data:
  DATABASE_NAME: "Reflection"
  MONGODB_URI: "mongodb://mongodb-service:27017/"
  FRONTEND_PORT: "5000"
  LOGIN_MANAGEMENT_PORT: "5001"
  LOGIN_MANAGEMENT_URL: "http://login-management-service:5001"
  FILE_PARSING_PORT: "5002"
  FILE_PARSING_URL: "http://file-parsing-service:5002"
  QA_GENERATION_PORT: "5003"
  QA_GENERATION_URL: "http://qa-generation-service:5003"
  ANSWER_ANALYSIS_PORT: "5004"
  ANSWER_ANALYSIS_URL: "http://speechtotext-service:5004"
  RESOURCES_PORT: "5005"
  RESOURCES_URL: "http://resources-service:5005"
  PINECONE_ENVIRONMENT: "us-east-1-aws"
  PINECONE_INDEX_NAME: "interview-prep-assistant"
  GOOGLE_REDIRECT_URI: "http://localhost:5000/api/auth/google/callback"
  GITHUB_REDIRECT_URI: "http://localhost:5000/api/auth/github/callback"
  UPLOAD_FOLDER: "uploads"
  MAX_FILE_SIZE_MB: "10"
  JWT_EXPIRY_HOURS: "24"
  FLASK_DEBUG: "False"
  ALLOWED_ORIGINS: "http://localhost:5000,http://localhost:3000"
EOF

# Verify
kubectl get configmap reflection-config -n reflection
```

### Step 3: Recreate Secrets

**IMPORTANT:** Get your credentials from `deployment-credentials.txt`

```bash
# Replace <your-*> with actual values from deployment-credentials.txt
kubectl create secret generic reflection-secrets \
  --namespace=reflection \
  --from-literal=FLASK_SECRET_KEY='<your-flask-secret>' \
  --from-literal=JWT_SECRET='<your-jwt-secret>' \
  --from-literal=GOOGLE_CLIENT_ID='<your-google-client-id>' \
  --from-literal=GOOGLE_CLIENT_SECRET='<your-google-client-secret>' \
  --from-literal=GITHUB_CLIENT_ID='<your-github-client-id>' \
  --from-literal=GITHUB_CLIENT_SECRET='<your-github-client-secret>' \
  --from-literal=GOOGLE_API_KEY='<your-gemini-api-key>' \
  --from-literal=PINECONE_API_KEY='<your-pinecone-api-key>'

# Verify (values will be hidden)
kubectl get secret reflection-secrets -n reflection
```

### Step 4: Setup Persistent Storage (CRITICAL!)

This time, let's ensure data persists:

```bash
# Create storage directories on your host
sudo mkdir -p /opt/kubernetes-data/mongodb
sudo mkdir -p /opt/kubernetes-data/uploads
sudo chmod -R 777 /opt/kubernetes-data

# Create MongoDB PersistentVolume with Retain policy
kubectl apply -f - <<EOF
apiVersion: v1
kind: PersistentVolume
metadata:
  name: mongodb-pv
spec:
  capacity:
    storage: 5Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  hostPath:
    path: "/opt/kubernetes-data/mongodb"
    type: DirectoryOrCreate
  storageClassName: standard
EOF

# Create MongoDB PersistentVolumeClaim
kubectl apply -f - <<EOF
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mongodb-pvc
  namespace: reflection
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
  storageClassName: standard
EOF

# Verify
kubectl get pv
kubectl get pvc -n reflection
```

### Step 5: Deploy MongoDB

```bash
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mongodb
  namespace: reflection
  labels:
    app: mongodb
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mongodb
  template:
    metadata:
      labels:
        app: mongodb
    spec:
      containers:
      - name: mongodb
        image: mongo:7.0
        ports:
        - containerPort: 27017
          name: mongodb
        volumeMounts:
        - name: mongodb-storage
          mountPath: /data/db
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
      volumes:
      - name: mongodb-storage
        persistentVolumeClaim:
          claimName: mongodb-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: mongodb-service
  namespace: reflection
  labels:
    app: mongodb
spec:
  type: ClusterIP
  ports:
  - port: 27017
    targetPort: 27017
    protocol: TCP
    name: mongodb
  selector:
    app: mongodb
EOF

# Wait for MongoDB to be ready
kubectl wait --for=condition=ready pod -l app=mongodb -n reflection --timeout=120s

# Verify
kubectl get pods -n reflection -l app=mongodb
```

### Step 6: Check Docker Images

```bash
# Check if your images still exist
docker images | grep reflection

# If images are missing, rebuild them
cd ~/Desktop/Study/7th_sem/capstone2/Reflection/Reflection/services

# Rebuild all images (this will take 5-10 minutes)
docker build -t reflection/frontend:latest -f frontend/Dockerfile .
docker build -t reflection/login-management:latest -f login-management/Dockerfile .
docker build -t reflection/file-parsing:latest -f file-parsing/Dockerfile .
docker build -t reflection/qa-generation:latest -f question-answer-generation/Dockerfile .
docker build -t reflection/speechtotext:latest -f SpeechToText/Dockerfile .
docker build -t reflection/resources:latest -f resources/Dockerfile .

cd ..
```

### Step 7: Deploy All Services

```bash
# If you created the YAML files before, apply them
kubectl apply -f k8s/login-management-deployment.yaml
kubectl apply -f k8s/file-parsing-deployment.yaml
kubectl apply -f k8s/qa-generation-deployment.yaml
kubectl apply -f k8s/speechtotext-deployment.yaml
kubectl apply -f k8s/resources-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml

# Wait for all to be ready
kubectl wait --for=condition=available --timeout=300s deployment --all -n reflection

# Check status
kubectl get pods -n reflection
```

### Step 8: Fix Metrics Server (if needed)

```bash
# Check if metrics-server exists
kubectl get deployment metrics-server -n kube-system

# If not, or if broken, redeploy with patch
kubectl delete deployment metrics-server -n kube-system 2>/dev/null || true

kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: metrics-server
  namespace: kube-system
spec:
  selector:
    matchLabels:
      k8s-app: metrics-server
  template:
    metadata:
      labels:
        k8s-app: metrics-server
    spec:
      containers:
      - name: metrics-server
        image: registry.k8s.io/metrics-server/metrics-server:v0.6.4
        args:
        - --cert-dir=/tmp
        - --secure-port=4443
        - --kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname
        - --kubelet-use-node-status-port
        - --metric-resolution=15s
        - --kubelet-insecure-tls
      serviceAccountName: metrics-server
EOF

# Wait and test
sleep 30
kubectl top nodes
```

### Step 9: Verify Everything

```bash
# Check all resources
kubectl get all -n reflection

# Test health endpoints
kubectl run -it --rm test --image=curlimages/curl --restart=Never -n reflection -- curl http://frontend-service:5000/health

# Access application
kubectl port-forward -n reflection svc/frontend-service 5000:5000 &

# Open browser to http://localhost:5000
```

---

## 🛡️ Prevent Future Data Loss

### 1. Enable Docker Desktop Data Persistence

Check Docker Desktop settings:

```bash
# On Linux, check Docker Desktop VM settings
docker info | grep "Docker Root Dir"

# Ensure it's using a persistent location
```

### 2. Backup Kubernetes Configurations

Create a backup script:

```bash
# Create backup directory
mkdir -p ~/kubernetes-backups

# Create backup script
cat > ~/kubernetes-backups/backup-k8s-configs.sh <<'EOF'
#!/bin/bash

BACKUP_DIR=~/kubernetes-backups/$(date +%Y%m%d-%H%M%S)
mkdir -p "$BACKUP_DIR"

echo "📦 Backing up Kubernetes configurations..."

# Backup all resources
kubectl get all -n reflection -o yaml > "$BACKUP_DIR/all-resources.yaml"
kubectl get configmap -n reflection -o yaml > "$BACKUP_DIR/configmaps.yaml"
kubectl get secret -n reflection -o yaml > "$BACKUP_DIR/secrets.yaml"
kubectl get pv -o yaml > "$BACKUP_DIR/persistent-volumes.yaml"
kubectl get pvc -n reflection -o yaml > "$BACKUP_DIR/persistent-volume-claims.yaml"

echo "✅ Backup saved to: $BACKUP_DIR"
EOF

chmod +x ~/kubernetes-backups/backup-k8s-configs.sh

# Run backup
~/kubernetes-backups/backup-k8s-configs.sh
```

### 3. Version Control for K8s Manifests

```bash
# Commit all your k8s YAML files to Git
cd ~/Desktop/Study/7th_sem/capstone2/Reflection/Reflection

git add k8s/
git commit -m "Add Kubernetes deployment manifests"
git push
```

### 4. Setup Automated Daily Backups

```bash
# Add to crontab for daily backups at 2 AM
(crontab -l 2>/dev/null; echo "0 2 * * * ~/kubernetes-backups/backup-k8s-configs.sh") | crontab -

# Verify
crontab -l
```

### 5. Document Your Setup

Keep a checklist of what's deployed:

```bash
# Create deployment checklist
cat > DEPLOYMENT_CHECKLIST.md <<'EOF'
# Deployment Checklist

## Current Status

- [ ] Namespace: reflection
- [ ] ConfigMap: reflection-config
- [ ] Secret: reflection-secrets
- [ ] MongoDB PV & PVC
- [ ] MongoDB Deployment & Service
- [ ] Login Management Deployment & Service
- [ ] File Parsing Deployment & Service
- [ ] Q&A Generation Deployment & Service
- [ ] SpeechToText Deployment & Service
- [ ] Resources Deployment & Service
- [ ] Frontend Deployment & Service
- [ ] Metrics Server

## Last Deployed

Date: $(date)
By: $(whoami)
Cluster: $(kubectl config current-context)

## Verify Commands

```bash
kubectl get all -n reflection
kubectl get configmap,secret -n reflection
kubectl get pv,pvc -n reflection
```
EOF
```

---

## 🔄 Quick Recovery Script

Create an all-in-one recovery script:

```bash
cat > ~/Desktop/Study/7th_sem/capstone2/Reflection/Reflection/quick-recovery.sh <<'EOF'
#!/bin/bash

set -e

echo "🔄 Starting Quick Recovery..."
echo ""

# Check if k8s is running
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Kubernetes cluster not accessible. Start Docker Desktop first."
    exit 1
fi

# Create namespace
echo "1️⃣ Creating namespace..."
kubectl create namespace reflection 2>/dev/null || echo "   Namespace already exists"
kubectl config set-context --current --namespace=reflection

# Apply configs if files exist
echo "2️⃣ Applying configurations..."
if [ -f k8s/configmap.yaml ]; then
    kubectl apply -f k8s/configmap.yaml
else
    echo "   ⚠️  ConfigMap file not found, skipping"
fi

# Note: Secrets must be created manually (contains sensitive data)
echo "3️⃣ Checking secrets..."
if kubectl get secret reflection-secrets -n reflection &> /dev/null; then
    echo "   ✅ Secrets exist"
else
    echo "   ⚠️  Secrets not found. Create manually with your credentials."
    echo "   Run: kubectl create secret generic reflection-secrets ..."
fi

# Setup persistent storage
echo "4️⃣ Setting up persistent storage..."
sudo mkdir -p /opt/kubernetes-data/mongodb /opt/kubernetes-data/uploads
sudo chmod -R 777 /opt/kubernetes-data

# Apply all k8s manifests
echo "5️⃣ Deploying services..."
if [ -d k8s ]; then
    kubectl apply -f k8s/ 2>/dev/null || echo "   Some resources may already exist"
else
    echo "   ⚠️  k8s directory not found"
fi

# Wait for pods
echo "6️⃣ Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod --all -n reflection --timeout=300s 2>/dev/null || echo "   Some pods may still be starting"

# Show status
echo ""
echo "✅ Recovery complete!"
echo ""
echo "📊 Current Status:"
kubectl get pods -n reflection

echo ""
echo "🌐 Access application:"
echo "   kubectl port-forward -n reflection svc/frontend-service 5000:5000"
echo "   Then open: http://localhost:5000"
EOF

chmod +x quick-recovery.sh
```

Run recovery:

```bash
cd ~/Desktop/Study/7th_sem/capstone2/Reflection/Reflection
./quick-recovery.sh
```

---

## 📊 Post-Recovery Verification

### Checklist

- [ ] Namespace exists: `kubectl get namespace reflection`
- [ ] ConfigMap exists: `kubectl get configmap -n reflection`
- [ ] Secrets exist: `kubectl get secret -n reflection`
- [ ] PV/PVC created: `kubectl get pv,pvc -n reflection`
- [ ] MongoDB running: `kubectl get pods -n reflection -l app=mongodb`
- [ ] All services running: `kubectl get pods -n reflection`
- [ ] Services accessible: `kubectl get svc -n reflection`
- [ ] Health checks passing: `kubectl get pods -n reflection` (all Running)
- [ ] Application accessible: http://localhost:5000

---

## 🎓 Lessons Learned

### Why This Happened

1. **Docker Desktop uses ephemeral storage by default**
2. **System crashes can corrupt Kubernetes etcd database**
3. **No backup strategy was in place**
4. **Configurations weren't version controlled**

### What to Do Differently

1. ✅ **Always use PersistentVolumes with `Retain` policy**
2. ✅ **Keep all YAML manifests in Git**
3. ✅ **Setup automated backups**
4. ✅ **Document deployment process**
5. ✅ **Test recovery procedures regularly**
6. ✅ **Use Infrastructure as Code (IaC)**

---

## 🚀 Next Steps

1. **Complete the recovery** using steps above
2. **Setup automated backups** (Section: Prevent Future Data Loss)
3. **Test the recovery script** to ensure it works
4. **Commit all k8s manifests** to Git
5. **Create a runbook** for future reference

---

**Need Help?**

If recovery fails, check:
- Docker Desktop is running and healthy
- Kubernetes is enabled in Docker Desktop
- Enough disk space: `df -h`
- Docker images exist: `docker images | grep reflection`
- Error logs: `kubectl logs -n reflection <pod-name>`

---

**Last Updated:** November 13, 2025  
**Status:** 🚨 Critical Issue - Recovery Required
