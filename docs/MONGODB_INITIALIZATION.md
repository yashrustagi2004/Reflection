# MongoDB Initialization Guide

## ✅ Status: Successfully Initialized

MongoDB has been successfully initialized with the following setup:

### Database Structure

**Database:** `Reflection`

**Collections:**
- ✅ `users` - User account information
- ✅ `user_questions` - Generated interview questions and user responses
- ✅ `resources` - Learning resources and materials

### Authentication Details

**Root User:**
- Username: `admin`
- Password: `reflectionpass123`
- Authentication Database: `admin`

**Important:** The root user is created in the `admin` database, not in the application database. You must always authenticate against the `admin` database first.

### Connection Strings

#### For Application Services (from within Kubernetes)
```
mongodb://admin:reflectionpass123@mongodb-service:27017/Reflection?authSource=admin
```

#### For Direct mongosh Access (from MongoDB pod)
```bash
mongosh "mongodb://admin:reflectionpass123@localhost:27017/admin"
```

### Common Operations

#### 1. List All Databases
```bash
kubectl exec -it -n reflection deployment/mongodb -- \
  mongosh "mongodb://admin:reflectionpass123@localhost:27017/admin" \
  --eval 'db.adminCommand("listDatabases")'
```

#### 2. List Collections in Reflection Database
```bash
kubectl exec -it -n reflection deployment/mongodb -- \
  mongosh "mongodb://admin:reflectionpass123@localhost:27017/admin" \
  --eval 'db.getSiblingDB("Reflection").getCollectionNames()'
```

#### 3. Insert Sample Data
```bash
kubectl exec -it -n reflection deployment/mongodb -- \
  mongosh "mongodb://admin:reflectionpass123@localhost:27017/admin" \
  --eval '
    db = db.getSiblingDB("Reflection");
    db.users.insertOne({
      email: "test@example.com",
      name: "Test User",
      created_at: new Date()
    });
    print("✅ Sample user created");
  '
```

#### 4. Query Data
```bash
kubectl exec -it -n reflection deployment/mongodb -- \
  mongosh "mongodb://admin:reflectionpass123@localhost:27017/admin" \
  --eval '
    db = db.getSiblingDB("Reflection");
    db.users.find().pretty();
  '
```

#### 5. Interactive Shell Access
```bash
kubectl exec -it -n reflection deployment/mongodb -- \
  mongosh "mongodb://admin:reflectionpass123@localhost:27017/admin"
```

Once connected, switch to the Reflection database:
```javascript
use Reflection
db.users.find()
```

### Using Mongo Express GUI

1. **Access Mongo Express:**
   ```bash
   kubectl port-forward -n reflection svc/mongo-express-service 8081:8081
   ```

2. **Open in Browser:**
   ```
   http://localhost:8081
   ```

3. **Login:**
   - Username: `admin`
   - Password: `admin123`

4. **Navigate to Reflection Database:**
   - Click on "Reflection" database
   - View and manage all collections
   - Insert, update, delete documents through the GUI

### Troubleshooting

#### Authentication Failed Error

If you get `MongoServerError: Authentication failed`, ensure you're authenticating against the `admin` database:

❌ **Incorrect:**
```bash
mongosh "mongodb://admin:pass@localhost:27017/Reflection"
```

✅ **Correct:**
```bash
mongosh "mongodb://admin:pass@localhost:27017/admin"
# Then switch to Reflection database
```

Or use the `authSource` parameter:
```bash
mongosh "mongodb://admin:pass@localhost:27017/Reflection?authSource=admin"
```

#### Connection String for Application Configuration

Update your ConfigMap with:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: reflection-config
  namespace: reflection
data:
  MONGODB_URI: "mongodb://admin:reflectionpass123@mongodb-service:27017/Reflection?authSource=admin"
```

### Re-initialization Script

If you need to reinitialize MongoDB (e.g., after data corruption), use the provided script:

```bash
# Copy and execute the initialization script
kubectl cp k8s/init-mongodb.js reflection/$(kubectl get pod -n reflection -l app=mongodb -o jsonpath='{.items[0].metadata.name}'):/tmp/init-mongodb.js

kubectl exec -it -n reflection deployment/mongodb -- \
  mongosh "mongodb://admin:reflectionpass123@localhost:27017/admin" \
  --file /tmp/init-mongodb.js
```

### Security Notes

1. **Change Default Passwords:** Before deploying to production, update the MongoDB credentials in the `mongodb-credentials` secret

2. **Network Isolation:** MongoDB is only accessible within the Kubernetes cluster (ClusterIP service)

3. **Persistent Storage:** Data is stored in `/opt/kubernetes-data/mongodb` with a `Retain` policy, so it survives pod restarts

4. **Backup Recommendations:**
   ```bash
   # Create a backup
   kubectl exec -n reflection deployment/mongodb -- \
     mongodump --uri="mongodb://admin:reflectionpass123@localhost:27017/Reflection?authSource=admin" \
     --out=/tmp/backup
   
   # Copy backup to local machine
   kubectl cp reflection/<pod-name>:/tmp/backup ./mongodb-backup
   ```

### Next Steps

Now that MongoDB is initialized, you can:

1. ✅ Deploy your application microservices
2. ✅ Configure services to use the MongoDB connection string
3. ✅ Test application connectivity to the database
4. ✅ Start using the application

### Reference Files

- MongoDB Deployment: `k8s/mongodb-deployment.yaml`
- MongoDB Service: `k8s/mongodb-service.yaml`
- Initialization Script: `k8s/init-mongodb.js`
- Credentials Secret: `kubectl get secret mongodb-credentials -n reflection`
