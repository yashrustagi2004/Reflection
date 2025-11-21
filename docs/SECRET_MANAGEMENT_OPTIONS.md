# Secret Management Options

**Date:** November 13, 2025  
**Topic:** Managing Kubernetes Secrets - Combined vs Separate

---

## 🔐 Current Setup (Two Secrets)

### Secret 1: Application Secrets (`reflection-secrets`)

Created in Step 3 with:

```bash
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
```

**Used by:** All application services (frontend, login-management, file-parsing, etc.)

### Secret 2: MongoDB Credentials (`mongodb-credentials`)

Created during MongoDB deployment:

```bash
kubectl create secret generic mongodb-credentials \
  --namespace=reflection \
  --from-literal=MONGO_INITDB_ROOT_USERNAME=admin \
  --from-literal=MONGO_INITDB_ROOT_PASSWORD=reflectionpass123
```

**Used by:** MongoDB and Mongo Express only

---

## 🎯 Option A: Keep Separate (Current Setup)

### Advantages ✅

1. **Better Security**
   - Principle of least privilege
   - Not all pods need DB credentials

2. **Easier Access Control**
   - Can restrict who views DB passwords
   - Different RBAC policies per secret

3. **Independent Lifecycle**
   - Rotate DB password without affecting other secrets
   - Update API keys without touching DB credentials

4. **Clearer Separation**
   - Database vs Application concerns
   - Easier to audit and track

### Disadvantages ❌

1. **More Management**
   - Two secrets to create and maintain
   - Two secrets to backup/restore

2. **Slightly More Complex**
   - Need to remember which secret contains what

### When to Use This Approach

- ✅ **Production environments**
- ✅ **Team environments** (different people manage different secrets)
- ✅ **When compliance/audit is required**
- ✅ **Multi-tenant applications**

---

## 🎯 Option B: Combine Into One Secret

Combine all secrets into a single `reflection-secrets`:

```bash
# Delete existing secrets
kubectl delete secret reflection-secrets mongodb-credentials -n reflection

# Create combined secret
kubectl create secret generic reflection-secrets \
  --namespace=reflection \
  --from-literal=FLASK_SECRET_KEY='<your-flask-secret>' \
  --from-literal=JWT_SECRET='<your-jwt-secret>' \
  --from-literal=GOOGLE_CLIENT_ID='<your-google-client-id>' \
  --from-literal=GOOGLE_CLIENT_SECRET='<your-google-client-secret>' \
  --from-literal=GITHUB_CLIENT_ID='<your-github-client-id>' \
  --from-literal=GITHUB_CLIENT_SECRET='<your-github-client-secret>' \
  --from-literal=GOOGLE_API_KEY='<your-gemini-api-key>' \
  --from-literal=PINECONE_API_KEY='<your-pinecone-api-key>' \
  --from-literal=MONGO_INITDB_ROOT_USERNAME=admin \
  --from-literal=MONGO_INITDB_ROOT_PASSWORD=reflectionpass123
```

### Advantages ✅

1. **Simpler Management**
   - One secret to create
   - One secret to backup/restore

2. **Easier Development**
   - All credentials in one place
   - Simpler to track and update

3. **Consistent Access**
   - All pods use same secret
   - Easier to understand

### Disadvantages ❌

1. **Less Secure**
   - All pods have access to all secrets (even if not needed)
   - Violates principle of least privilege

2. **Harder to Rotate**
   - Updating DB password affects all pods
   - Can't rotate independently

3. **Less Auditable**
   - Can't track DB credential access separately

### When to Use This Approach

- ✅ **Development/Learning environments**
- ✅ **Small projects** (1-2 developers)
- ✅ **When simplicity is priority**
- ✅ **POC/Demo applications**

---

## 🔄 How to Switch Between Options

### Switch from Separate → Combined

```bash
# 1. Get existing values (if you need to reference them)
kubectl get secret reflection-secrets -n reflection -o yaml > reflection-secrets-backup.yaml
kubectl get secret mongodb-credentials -n reflection -o yaml > mongodb-credentials-backup.yaml

# 2. Delete old secrets
kubectl delete secret reflection-secrets mongodb-credentials -n reflection

# 3. Create combined secret with ALL values
kubectl create secret generic reflection-secrets \
  --namespace=reflection \
  --from-literal=FLASK_SECRET_KEY='<your-value>' \
  --from-literal=JWT_SECRET='<your-value>' \
  --from-literal=GOOGLE_CLIENT_ID='<your-value>' \
  --from-literal=GOOGLE_CLIENT_SECRET='<your-value>' \
  --from-literal=GITHUB_CLIENT_ID='<your-value>' \
  --from-literal=GITHUB_CLIENT_SECRET='<your-value>' \
  --from-literal=GOOGLE_API_KEY='<your-value>' \
  --from-literal=PINECONE_API_KEY='<your-value>' \
  --from-literal=MONGO_INITDB_ROOT_USERNAME=admin \
  --from-literal=MONGO_INITDB_ROOT_PASSWORD=reflectionpass123

# 4. Update MongoDB deployment to use reflection-secrets instead
kubectl edit deployment mongodb -n reflection
# Change secretRef from mongodb-credentials to reflection-secrets

# 5. Update Mongo Express deployment similarly
kubectl edit deployment mongo-express -n reflection
# Change secretRef from mongodb-credentials to reflection-secrets

# 6. Restart deployments to pick up changes
kubectl rollout restart deployment/mongodb -n reflection
kubectl rollout restart deployment/mongo-express -n reflection
```

### Switch from Combined → Separate

```bash
# 1. Backup current secret
kubectl get secret reflection-secrets -n reflection -o yaml > combined-secret-backup.yaml

# 2. Create separate MongoDB credentials secret
kubectl create secret generic mongodb-credentials \
  --namespace=reflection \
  --from-literal=MONGO_INITDB_ROOT_USERNAME=admin \
  --from-literal=MONGO_INITDB_ROOT_PASSWORD=reflectionpass123

# 3. Recreate application secret without MongoDB credentials
kubectl delete secret reflection-secrets -n reflection
kubectl create secret generic reflection-secrets \
  --namespace=reflection \
  --from-literal=FLASK_SECRET_KEY='<your-value>' \
  --from-literal=JWT_SECRET='<your-value>' \
  --from-literal=GOOGLE_CLIENT_ID='<your-value>' \
  --from-literal=GOOGLE_CLIENT_SECRET='<your-value>' \
  --from-literal=GITHUB_CLIENT_ID='<your-value>' \
  --from-literal=GITHUB_CLIENT_SECRET='<your-value>' \
  --from-literal=GOOGLE_API_KEY='<your-value>' \
  --from-literal=PINECONE_API_KEY='<your-value>'

# 4. Update deployments (MongoDB and Mongo Express already use mongodb-credentials)
# No changes needed to deployment YAMLs

# 5. Restart application deployments
kubectl rollout restart deployment -n reflection
```

---

## 📋 Comparison Table

| Feature | Separate Secrets | Combined Secret |
|---------|------------------|-----------------|
| **Security** | ✅ Better | ⚠️ Less secure |
| **Complexity** | ⚠️ More complex | ✅ Simpler |
| **Access Control** | ✅ Granular | ❌ All-or-nothing |
| **Rotation** | ✅ Independent | ⚠️ Affects all |
| **Management** | ⚠️ More work | ✅ Easier |
| **Audit Trail** | ✅ Separate logs | ⚠️ Combined logs |
| **Best For** | Production | Development |

---

## 🎓 Recommendation

### For Your Use Case (Learning/Development):

**Start with COMBINED** (Option B) for simplicity:
- ✅ Easier to manage while learning
- ✅ One place for all credentials
- ✅ Simpler backup/restore
- ✅ Less configuration files

**Switch to SEPARATE** when:
- 📦 Moving to production
- 👥 Multiple developers join
- 🔒 Security requirements increase
- 📊 Need audit trails

---

## 🛠️ Implementation Guide

### If You Want Combined Secret (Recommended for You)

Create this script: `create-combined-secret.sh`

```bash
#!/bin/bash

# Source your credentials file
source deployment-credentials.txt

# Create combined secret with all credentials
kubectl create secret generic reflection-secrets \
  --namespace=reflection \
  --from-literal=FLASK_SECRET_KEY="$FLASK_SECRET_KEY" \
  --from-literal=JWT_SECRET="$JWT_SECRET" \
  --from-literal=GOOGLE_CLIENT_ID="$GOOGLE_CLIENT_ID" \
  --from-literal=GOOGLE_CLIENT_SECRET="$GOOGLE_CLIENT_SECRET" \
  --from-literal=GITHUB_CLIENT_ID="$GITHUB_CLIENT_ID" \
  --from-literal=GITHUB_CLIENT_SECRET="$GITHUB_CLIENT_SECRET" \
  --from-literal=GOOGLE_API_KEY="$GOOGLE_API_KEY" \
  --from-literal=PINECONE_API_KEY="$PINECONE_API_KEY" \
  --from-literal=MONGO_INITDB_ROOT_USERNAME="admin" \
  --from-literal=MONGO_INITDB_ROOT_PASSWORD="reflectionpass123"

echo "✅ Combined secret created!"
```

Then update `deployment-credentials.txt` to include MongoDB:

```bash
# Add to your deployment-credentials.txt
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=reflectionpass123
```

---

## 🔍 How to Check Current Setup

```bash
# List all secrets
kubectl get secrets -n reflection

# View secret keys (not values)
kubectl describe secret reflection-secrets -n reflection
kubectl describe secret mongodb-credentials -n reflection

# Check which pods use which secrets
kubectl get pods -n reflection -o yaml | grep -A 5 secretRef
```

---

## 💡 Pro Tips

### Keep Secrets in Version Control (Safely)

**NEVER commit actual secrets!** But you can version control the structure:

Create: `k8s/secrets-template.yaml`

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: reflection-secrets
  namespace: reflection
type: Opaque
stringData:
  FLASK_SECRET_KEY: "REPLACE_ME"
  JWT_SECRET: "REPLACE_ME"
  GOOGLE_CLIENT_ID: "REPLACE_ME"
  GOOGLE_CLIENT_SECRET: "REPLACE_ME"
  GITHUB_CLIENT_ID: "REPLACE_ME"
  GITHUB_CLIENT_SECRET: "REPLACE_ME"
  GOOGLE_API_KEY: "REPLACE_ME"
  PINECONE_API_KEY: "REPLACE_ME"
  # Include MongoDB if using combined approach
  MONGO_INITDB_ROOT_USERNAME: "REPLACE_ME"
  MONGO_INITDB_ROOT_PASSWORD: "REPLACE_ME"
```

Then use a script to replace values:

```bash
# create-secrets-from-template.sh
envsubst < k8s/secrets-template.yaml | kubectl apply -f -
```

---

## 🔒 Security Best Practices

Regardless of combined vs separate:

1. **Use Strong Passwords**
   ```bash
   # Generate secure password
   openssl rand -base64 32
   ```

2. **Rotate Regularly**
   ```bash
   # Update secret
   kubectl create secret generic reflection-secrets \
     --from-literal=key=new-value \
     --dry-run=client -o yaml | kubectl apply -f -
   ```

3. **Backup Secrets**
   ```bash
   kubectl get secrets -n reflection -o yaml > secrets-backup.yaml
   ```

4. **Use External Secret Management** (for production)
   - HashiCorp Vault
   - AWS Secrets Manager
   - Azure Key Vault
   - Google Secret Manager

---

## 📝 Summary

### Your Current Setup
```
reflection-secrets      → 8 keys (API keys, OAuth, JWT)
mongodb-credentials     → 2 keys (MongoDB username, password)
```

### My Recommendation for You
```
reflection-secrets      → 10 keys (ALL credentials combined)
# Delete mongodb-credentials
```

**Why?** You're learning, and simplicity helps. You can always split them later when you understand the tradeoffs.

---

**Ready to combine them? See the implementation guide above!**

**Last Updated:** November 13, 2025
