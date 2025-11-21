# MongoDB & Mongo Express - Quick Reference

**Date:** November 13, 2025  
**Purpose:** Quick access guide for MongoDB database and Mongo Express GUI

---

## 🗄️ MongoDB Configuration

### Connection Details

| Property | Value |
|----------|-------|
| **Host** | `mongodb-service` (internal) or `localhost` (via port-forward) |
| **Port** | `27017` |
| **Database** | `Reflection` |
| **Username** | `admin` |
| **Password** | `reflectionpass123` |
| **Connection String** | `mongodb://admin:reflectionpass123@mongodb-service:27017/` |

### Data Storage

- **Host Directory:** `/opt/kubernetes-data/mongodb`
- **Container Path:** `/data/db`
- **Persistence:** ✅ Data survives pod restarts
- **Retain Policy:** ✅ Data survives PV deletion

---

## 🌐 Mongo Express GUI

### Access Information

| Property | Value |
|----------|-------|
| **URL** | http://localhost:8081 |
| **Username** | `admin` |
| **Password** | `admin123` |
| **MongoDB Connection** | Automatically configured |

### How to Access

```bash
# Option 1: Via LoadBalancer (Docker Desktop)
# Open browser to: http://localhost:8081

# Option 2: Via Port Forward (if LoadBalancer not working)
kubectl port-forward -n reflection svc/mongo-express-service 8081:8081

# Then open: http://localhost:8081
```

### Login Credentials

When you open http://localhost:8081, you'll be prompted for HTTP Basic Auth:

```
Username: admin
Password: admin123
```

After logging in, you'll see the Mongo Express interface with:
- Database: `Reflection`
- Collections: `users`, `user_questions`, `resources`, etc.

---

## 🔧 Common Operations

### 1. Check MongoDB Status

```bash
# Check if MongoDB pod is running
kubectl get pods -n reflection -l app=mongodb

# Check MongoDB logs
kubectl logs -n reflection -l app=mongodb --tail=50

# Check if MongoDB is responding
kubectl exec -it -n reflection deployment/mongodb -- \
  mongosh "mongodb://admin:reflectionpass123@localhost:27017/Reflection" \
  --eval "db.adminCommand('ping')"
```

### 2. Access MongoDB Shell

```bash
# Open MongoDB shell in the pod
kubectl exec -it -n reflection deployment/mongodb -- mongosh -u admin -p reflectionpass123

# Or with connection string
kubectl exec -it -n reflection deployment/mongodb -- \
  mongosh "mongodb://admin:reflectionpass123@localhost:27017/Reflection"
```

### 3. View Collections

```bash
# List all collections in Reflection database
kubectl exec -it -n reflection deployment/mongodb -- \
  mongosh "mongodb://admin:reflectionpass123@localhost:27017/Reflection" \
  --eval "db.getCollectionNames()"
```

### 4. Query Data

```bash
# View all users
kubectl exec -it -n reflection deployment/mongodb -- \
  mongosh "mongodb://admin:reflectionpass123@localhost:27017/Reflection" \
  --eval "db.users.find().pretty()"

# Count documents in a collection
kubectl exec -it -n reflection deployment/mongodb -- \
  mongosh "mongodb://admin:reflectionpass123@localhost:27017/Reflection" \
  --eval "db.users.countDocuments()"
```

### 5. Backup MongoDB

```bash
# Create backup directory
mkdir -p ~/mongodb-backups

# Backup all databases
kubectl exec -n reflection deployment/mongodb -- \
  mongodump --username=admin --password=reflectionpass123 --authenticationDatabase=admin --out=/tmp/backup

# Copy backup from pod to local machine
POD_NAME=$(kubectl get pod -n reflection -l app=mongodb -o jsonpath='{.items[0].metadata.name}')
kubectl cp "reflection/$POD_NAME:/tmp/backup" ~/mongodb-backups/backup-$(date +%Y%m%d-%H%M%S)

echo "✅ Backup completed!"
```

### 6. Restore MongoDB

```bash
# Copy backup to pod
POD_NAME=$(kubectl get pod -n reflection -l app=mongodb -o jsonpath='{.items[0].metadata.name}')
kubectl cp ~/mongodb-backups/backup-20251113-120000 "reflection/$POD_NAME:/tmp/restore"

# Restore database
kubectl exec -n reflection deployment/mongodb -- \
  mongorestore --username=admin --password=reflectionpass123 --authenticationDatabase=admin /tmp/restore

echo "✅ Restore completed!"
```

---

## 🎨 Using Mongo Express GUI

### Features Available

1. **View Databases**
   - See all databases in MongoDB instance
   - View database statistics

2. **Manage Collections**
   - View all collections in a database
   - Create new collections
   - Delete collections
   - View collection statistics

3. **Browse Documents**
   - View documents in a collection
   - Search/filter documents
   - Sort documents
   - Paginate through results

4. **Edit Documents**
   - Add new documents
   - Edit existing documents
   - Delete documents
   - Clone documents

5. **Query Builder**
   - Build MongoDB queries visually
   - Execute custom queries
   - View query results

6. **Import/Export**
   - Export collections to JSON
   - Import JSON data

### Common Tasks in Mongo Express

#### View User Data

1. Open http://localhost:8081
2. Login with `admin` / `admin123`
3. Click on `Reflection` database
4. Click on `users` collection
5. Browse user documents

#### Add Test Data

1. Click on a collection (e.g., `users`)
2. Click "New Document"
3. Enter JSON data:
```json
{
  "email": "test@example.com",
  "name": "Test User",
  "provider": "google",
  "created_at": "2025-11-13T00:00:00Z"
}
```
4. Click "Save"

#### Search Documents

1. Click on a collection
2. Use the search box at the top
3. Enter MongoDB query syntax:
```json
{"email": "test@example.com"}
```
4. Press Enter to search

#### Delete Documents

1. Browse to a document
2. Click the "Delete" button
3. Confirm deletion

---

## 🔒 Security Notes

### Current Setup (Development)

⚠️ **This configuration is for DEVELOPMENT only!**

- MongoDB credentials are hardcoded
- Mongo Express has basic auth with simple password
- Services are exposed via LoadBalancer

### For Production

1. **Use Kubernetes Secrets properly**
   ```bash
   # Generate strong passwords
   MONGO_PASSWORD=$(openssl rand -base64 32)
   
   kubectl create secret generic mongodb-credentials \
     --namespace=reflection \
     --from-literal=MONGO_INITDB_ROOT_USERNAME=admin \
     --from-literal=MONGO_INITDB_ROOT_PASSWORD="$MONGO_PASSWORD"
   ```

2. **Don't expose Mongo Express externally**
   ```yaml
   spec:
     type: ClusterIP  # Instead of LoadBalancer
   ```
   
   Then use port-forwarding only when needed:
   ```bash
   kubectl port-forward -n reflection svc/mongo-express-service 8081:8081
   ```

3. **Use Network Policies**
   - Restrict which pods can access MongoDB
   - Only allow application pods to connect

4. **Enable MongoDB SSL/TLS**
   - Configure MongoDB with SSL certificates
   - Enforce encrypted connections

5. **Use strong authentication**
   - Create separate users for each application
   - Use role-based access control (RBAC)

---

## 🛠️ Troubleshooting

### Issue 1: Can't Access Mongo Express

**Problem:** http://localhost:8081 not accessible

**Solution:**
```bash
# Check if pod is running
kubectl get pods -n reflection -l app=mongo-express

# Check pod logs
kubectl logs -n reflection -l app=mongo-express

# Check service
kubectl get svc mongo-express-service -n reflection

# If LoadBalancer pending, use port-forward
kubectl port-forward -n reflection svc/mongo-express-service 8081:8081
```

### Issue 2: Mongo Express Can't Connect to MongoDB

**Problem:** "Could not connect to database" error

**Solution:**
```bash
# Verify MongoDB is running
kubectl get pods -n reflection -l app=mongodb

# Test MongoDB connectivity
kubectl exec -it -n reflection deployment/mongodb -- \
  mongosh "mongodb://admin:reflectionpass123@localhost:27017" \
  --eval "db.adminCommand('ping')"

# Check Mongo Express environment variables
kubectl describe pod -n reflection -l app=mongo-express | grep -A 10 "Environment"

# Restart Mongo Express
kubectl rollout restart deployment/mongo-express -n reflection
```

### Issue 3: Authentication Failed

**Problem:** "Authentication failed" when connecting to MongoDB

**Solution:**
```bash
# Verify credentials in secret
kubectl get secret mongodb-credentials -n reflection -o jsonpath='{.data.MONGO_INITDB_ROOT_PASSWORD}' | base64 --decode

# Ensure ConfigMap has correct connection string
kubectl get configmap reflection-config -n reflection -o jsonpath='{.data.MONGODB_URI}'

# Should output: mongodb://admin:reflectionpass123@mongodb-service:27017/
```

### Issue 4: Data Not Persisting

**Problem:** MongoDB data lost after pod restart

**Solution:**
```bash
# Check PV and PVC status
kubectl get pv,pvc -n reflection

# Verify PV has Retain policy
kubectl get pv mongodb-pv -o jsonpath='{.spec.persistentVolumeReclaimPolicy}'
# Should output: Retain

# Check if data directory has content
kubectl exec -it -n reflection deployment/mongodb -- ls -la /data/db

# If empty, data was not mounted correctly
# Recreate PV/PVC and redeploy MongoDB
```

---

## 📊 Monitoring MongoDB

### Resource Usage

```bash
# Check MongoDB resource usage
kubectl top pod -n reflection -l app=mongodb

# Expected output:
# NAME                       CPU(cores)   MEMORY(bytes)
# mongodb-xxxxx             50m          450Mi
```

### Database Statistics

```bash
# Get database stats
kubectl exec -it -n reflection deployment/mongodb -- \
  mongosh "mongodb://admin:reflectionpass123@localhost:27017/Reflection" \
  --eval "db.stats()"
```

### Collection Statistics

```bash
# Get collection stats
kubectl exec -it -n reflection deployment/mongodb -- \
  mongosh "mongodb://admin:reflectionpass123@localhost:27017/Reflection" \
  --eval "db.users.stats()"
```

---

## 🔗 Related Documentation

- **KUBERNETES_DEPLOYMENT_GUIDE.md** - Full deployment guide
- **KUBERNETES_PERSISTENCE.md** - Data persistence guide
- **RECOVERY_AFTER_CRASH.md** - Recovery procedures

---

## 📝 Quick Command Reference

```bash
# Access Mongo Express GUI
http://localhost:8081 (admin/admin123)

# MongoDB Shell
kubectl exec -it -n reflection deployment/mongodb -- mongosh -u admin -p reflectionpass123

# View Logs
kubectl logs -n reflection -l app=mongodb
kubectl logs -n reflection -l app=mongo-express

# Backup Database
kubectl exec -n reflection deployment/mongodb -- mongodump --username=admin --password=reflectionpass123 --authenticationDatabase=admin --out=/tmp/backup

# Check Status
kubectl get pods,svc -n reflection -l app=mongodb
kubectl get pods,svc -n reflection -l app=mongo-express

# Restart Services
kubectl rollout restart deployment/mongodb -n reflection
kubectl rollout restart deployment/mongo-express -n reflection
```

---

**Last Updated:** November 13, 2025  
**Version:** 1.0
