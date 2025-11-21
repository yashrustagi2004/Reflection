# Kubernetes Persistence Guide - What Survives a Restart?

**Date:** November 13, 2025  
**Topic:** Understanding what persists after system restart in Kubernetes

---

## 🔍 Quick Answer

**YES**, most of your Kubernetes deployment **WILL PERSIST** after a system restart when using Docker Desktop Kubernetes, but there are some important considerations.

---

## 📊 What Persists vs What Doesn't

### ✅ **PERSISTS** (Survives Restart)

| Component | Status | Details |
|-----------|--------|---------|
| **Kubernetes Cluster** | ✅ Persists | Docker Desktop automatically starts Kubernetes |
| **Namespaces** | ✅ Persists | All namespaces remain |
| **Deployments** | ✅ Persists | Deployment configurations remain |
| **Services** | ✅ Persists | Service definitions remain |
| **ConfigMaps** | ✅ Persists | All configuration data persists |
| **Secrets** | ✅ Persists | All secrets persist (encrypted) |
| **Docker Images** | ✅ Persists | Locally built images remain |
| **PersistentVolumes (hostPath)** | ⚠️ **DEPENDS** | See details below |
| **MongoDB Data** | ⚠️ **DEPENDS** | Depends on storage configuration |

### ❌ **DOES NOT PERSIST** (Lost on Restart)

| Component | Status | Details |
|-----------|--------|---------|
| **Pod State** | ❌ Lost | Pods restart, lose in-memory data |
| **Temporary Storage (emptyDir)** | ❌ Lost | All emptyDir volumes are cleared |
| **Uploaded Files (without PV)** | ❌ Lost | Files in containers without persistent storage |
| **In-Memory Sessions** | ❌ Lost | Unless using external session store (Redis) |
| **Logs** | ❌ Lost | Unless exported to external system |
| **Port Forwards** | ❌ Lost | Need to be re-established manually |

---

## 🗄️ MongoDB Data Persistence - CRITICAL

### Problem with Current Setup

In the guide, we used `hostPath` for MongoDB persistence:

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: mongodb-pv
spec:
  hostPath:
    path: "/mnt/data/mongodb"  # ⚠️ THIS MIGHT NOT PERSIST
```

### Issue with Docker Desktop

**Docker Desktop on Linux uses a VM**, and the hostPath `/mnt/data/mongodb` is inside that VM. When you restart:
- ✅ The VM **usually** persists data in Docker Desktop
- ⚠️ But it **may not be reliable** for production use

### Solution 1: Use Docker Desktop's Persistent Path (Recommended)

Docker Desktop has specific paths that persist reliably:

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: mongodb-pv
  namespace: reflection
spec:
  capacity:
    storage: 5Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain  # Important!
  hostPath:
    path: "/var/lib/docker/volumes/mongodb-data"  # Docker manages this
    type: DirectoryOrCreate
  storageClassName: standard
```

### Solution 2: Use Local Storage (More Reliable)

Create a directory on your actual host machine:

```bash
# Create directory on your real Linux filesystem
sudo mkdir -p /opt/kubernetes-data/mongodb
sudo chmod 777 /opt/kubernetes-data/mongodb

# Update PV to use this path
```

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: mongodb-pv
  namespace: reflection
spec:
  capacity:
    storage: 5Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain  # CRITICAL - prevents data deletion
  hostPath:
    path: "/opt/kubernetes-data/mongodb"
    type: DirectoryOrCreate
  storageClassName: standard
```

### Solution 3: Use StatefulSet for MongoDB (Production-Grade)

For production, use StatefulSet instead of Deployment:

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mongodb
  namespace: reflection
spec:
  serviceName: mongodb-service
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
        volumeMounts:
        - name: mongodb-persistent-storage
          mountPath: /data/db
  volumeClaimTemplates:
  - metadata:
      name: mongodb-persistent-storage
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: standard
      resources:
        requests:
          storage: 5Gi
```

---

## 🔄 What Happens on System Restart

### Step-by-Step Process

#### 1. **System Shuts Down**
```
Your System Powers Off
         ↓
Docker Desktop Stops
         ↓
Kubernetes Cluster Stops
         ↓
All Pods Terminate
```

#### 2. **System Starts Up**
```
Your System Boots
         ↓
Docker Desktop Auto-Starts
         ↓
Kubernetes Cluster Auto-Starts
         ↓
Deployments Detected
         ↓
Pods Recreated Automatically
         ↓
Services Reconnect
```

#### 3. **What Gets Restored**

```bash
# After restart, check what's running
kubectl get all -n reflection

# Expected output - everything should be back:
NAME                                    READY   STATUS    RESTARTS   AGE
pod/frontend-xxxxx                      1/1     Running   0          2m
pod/login-management-xxxxx              1/1     Running   0          2m
pod/file-parsing-xxxxx                  1/1     Running   0          2m
pod/qa-generation-xxxxx                 1/1     Running   0          2m
pod/speechtotext-xxxxx                  1/1     Running   0          2m
pod/resources-xxxxx                     1/1     Running   0          2m
pod/mongodb-xxxxx                       1/1     Running   0          2m
```

---

## 🛡️ How to Ensure Data Persistence

### For MongoDB (Database)

**Step 1: Update PersistentVolume with Retain Policy**

```bash
# Edit existing PV
kubectl edit pv mongodb-pv
```

Change:
```yaml
persistentVolumeReclaimPolicy: Delete  # ❌ BAD
```

To:
```yaml
persistentVolumeReclaimPolicy: Retain  # ✅ GOOD
```

**Step 2: Verify Data Directory**

```bash
# Check where data is stored
kubectl get pv mongodb-pv -o yaml | grep path

# Backup the data directory regularly
kubectl exec -n reflection deployment/mongodb -- mongodump --out=/backup
```

**Step 3: Test Persistence**

```bash
# 1. Insert test data
kubectl exec -it -n reflection deployment/mongodb -- mongo

# In MongoDB shell:
use Reflection
db.test.insert({message: "This should persist", date: new Date()})
db.test.find()
exit

# 2. Restart your computer

# 3. After restart, check if data exists
kubectl exec -it -n reflection deployment/mongodb -- mongo

# In MongoDB shell:
use Reflection
db.test.find()  # Should show your test data
```

### For Uploaded Files

**Current Issue:**
```yaml
volumes:
- name: uploads
  emptyDir: {}  # ❌ This gets deleted on pod restart!
```

**Solution: Use PersistentVolume**

Create file: `k8s/file-uploads-pv.yaml`

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: uploads-pv
  namespace: reflection
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteMany  # Multiple pods can access
  persistentVolumeReclaimPolicy: Retain
  hostPath:
    path: "/opt/kubernetes-data/uploads"
    type: DirectoryOrCreate
  storageClassName: standard
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: uploads-pvc
  namespace: reflection
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 10Gi
  storageClassName: standard
```

Then update `file-parsing-deployment.yaml`:

```yaml
volumes:
- name: uploads
  persistentVolumeClaim:
    claimName: uploads-pvc  # ✅ Now persists!
```

### For Session Data

**Problem:** User sessions stored in Flask are lost on restart.

**Solution 1: Use Redis for Session Storage**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: reflection
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        volumeMounts:
        - name: redis-storage
          mountPath: /data
      volumes:
      - name: redis-storage
        persistentVolumeClaim:
          claimName: redis-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: redis-service
  namespace: reflection
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
```

**Solution 2: Update Flask to Use Redis**

```python
# In frontend/app.py
from flask_session import Session
import redis

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.from_url('redis://redis-service:6379')
Session(app)
```

---

## 🔧 Recommended Persistence Setup

### Complete Persistent Setup Script

Create file: `k8s/setup-persistent-storage.sh`

```bash
#!/bin/bash

echo "🗄️ Setting up persistent storage for Reflection app..."

# Create host directories
echo "Creating storage directories..."
sudo mkdir -p /opt/kubernetes-data/mongodb
sudo mkdir -p /opt/kubernetes-data/uploads
sudo mkdir -p /opt/kubernetes-data/redis
sudo chmod -R 777 /opt/kubernetes-data

# Apply persistent volumes
echo "Creating PersistentVolumes..."

# MongoDB PV
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

# Uploads PV
kubectl apply -f - <<EOF
apiVersion: v1
kind: PersistentVolume
metadata:
  name: uploads-pv
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain
  hostPath:
    path: "/opt/kubernetes-data/uploads"
    type: DirectoryOrCreate
  storageClassName: standard
EOF

echo "✅ Persistent storage setup complete!"
echo ""
echo "📁 Storage locations:"
echo "   MongoDB data: /opt/kubernetes-data/mongodb"
echo "   Uploaded files: /opt/kubernetes-data/uploads"
echo ""
echo "💡 These directories will persist across system restarts"
```

Make it executable and run:

```bash
chmod +x k8s/setup-persistent-storage.sh
./k8s/setup-persistent-storage.sh
```

---

## 🧪 Testing Persistence

### Test 1: MongoDB Data Persistence

```bash
# 1. Add test data
kubectl exec -it -n reflection deployment/mongodb -- mongo Reflection --eval 'db.test.insert({test: "restart_test", time: new Date()})'

# 2. Restart Docker Desktop
# On Linux: System Settings → restart or
sudo systemctl restart docker

# Wait for cluster to come back
kubectl wait --for=condition=ready pod -l app=mongodb -n reflection --timeout=180s

# 3. Verify data
kubectl exec -it -n reflection deployment/mongodb -- mongo Reflection --eval 'db.test.find()'

# Should show your test data! ✅
```

### Test 2: Application State After Restart

```bash
# Before restart
kubectl get all -n reflection > before-restart.txt

# Restart system

# After restart
kubectl get all -n reflection > after-restart.txt

# Compare (should be similar, just new pod names and ages)
diff before-restart.txt after-restart.txt
```

---

## 📋 Pre-Restart Checklist

Before restarting your system, verify:

```bash
# 1. Check PersistentVolumes have Retain policy
kubectl get pv -o custom-columns=NAME:.metadata.name,RECLAIMPOLICY:.spec.persistentVolumeReclaimPolicy

# Expected: All show "Retain"

# 2. Check PVC is bound
kubectl get pvc -n reflection

# Expected: All show "Bound"

# 3. Verify data locations
ls -la /opt/kubernetes-data/mongodb
ls -la /opt/kubernetes-data/uploads

# 4. Optional: Backup MongoDB
kubectl exec -n reflection deployment/mongodb -- mongodump --out=/tmp/backup
kubectl cp reflection/$(kubectl get pod -n reflection -l app=mongodb -o jsonpath='{.items[0].metadata.name}'):/tmp/backup ./mongodb-backup-$(date +%Y%m%d)
```

---

## 🚨 What to Do After Restart

### Automatic Recovery

Usually, everything starts automatically:

```bash
# Wait 2-3 minutes after restart, then check
kubectl get pods -n reflection

# All should be "Running"
```

### If Pods Don't Start

```bash
# Check cluster status
kubectl cluster-info

# Check node status
kubectl get nodes

# If nodes not ready, restart Docker Desktop
sudo systemctl restart docker

# Or from Docker Desktop UI: Settings → Kubernetes → Reset Kubernetes Cluster (last resort)
```

### Re-establish Port Forwards

Port forwards don't persist:

```bash
# If you were using port-forward, restart it
kubectl port-forward -n reflection svc/frontend-service 5000:5000 &

# Or access via LoadBalancer (should work automatically)
```

---

## 💾 Backup Strategy

### Daily Automated Backup

Create file: `k8s/backup-cronjob.yaml`

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: mongodb-backup
  namespace: reflection
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: mongo:7.0
            command:
            - /bin/sh
            - -c
            - |
              BACKUP_DIR=/backup/$(date +\%Y\%m\%d-\%H\%M\%S)
              mongodump --host=mongodb-service --out=$BACKUP_DIR
              echo "Backup completed: $BACKUP_DIR"
              # Keep only last 7 days of backups
              find /backup -type d -mtime +7 -exec rm -rf {} +
            volumeMounts:
            - name: backup-storage
              mountPath: /backup
          restartPolicy: OnFailure
          volumes:
          - name: backup-storage
            hostPath:
              path: /opt/kubernetes-data/backups
              type: DirectoryOrCreate
```

Apply:
```bash
kubectl apply -f k8s/backup-cronjob.yaml
```

### Manual Backup Before Restart

```bash
# Quick backup script
cat > backup-before-restart.sh <<'EOF'
#!/bin/bash
BACKUP_DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="./backups/$BACKUP_DATE"

mkdir -p "$BACKUP_DIR"

echo "📦 Backing up MongoDB..."
kubectl exec -n reflection deployment/mongodb -- mongodump --out=/tmp/backup
POD_NAME=$(kubectl get pod -n reflection -l app=mongodb -o jsonpath='{.items[0].metadata.name}')
kubectl cp "reflection/$POD_NAME:/tmp/backup" "$BACKUP_DIR/mongodb"

echo "📦 Backing up Kubernetes configs..."
kubectl get all -n reflection -o yaml > "$BACKUP_DIR/kubernetes-resources.yaml"
kubectl get configmap -n reflection -o yaml > "$BACKUP_DIR/configmaps.yaml"

echo "✅ Backup completed: $BACKUP_DIR"
EOF

chmod +x backup-before-restart.sh
./backup-before-restart.sh
```

---

## 📝 Summary

### What You Need to Know

1. **Kubernetes Configuration Persists** ✅
   - Your deployments, services, configmaps will survive restarts

2. **Pod State Does NOT Persist** ❌
   - Pods restart fresh, lose in-memory data

3. **Database Data CAN Persist** ⚠️
   - IF you configure PersistentVolumes correctly with `Retain` policy
   - IF you use proper storage paths

4. **Uploaded Files NEED PersistentVolumes** ⚠️
   - Don't use `emptyDir` for important data
   - Use PVC with `hostPath` or cloud storage

5. **Docker Desktop Usually Reliable** ✅
   - Docker Desktop's Kubernetes persists most things
   - But don't rely on it for production without testing

### Action Items

- [ ] Update MongoDB PV with `Retain` policy
- [ ] Create persistent storage for uploads
- [ ] Test persistence by restarting system
- [ ] Setup automated backups
- [ ] Document recovery procedures

---

## 🔗 Related Resources

- **KUBERNETES_DEPLOYMENT_GUIDE.md** - Main deployment guide
- **API_CURL_COMMANDS.md** - Testing endpoints after restart
- **Kubernetes Persistent Volumes Docs**: https://kubernetes.io/docs/concepts/storage/persistent-volumes/

---

**Last Updated:** November 13, 2025  
**Version:** 1.0
