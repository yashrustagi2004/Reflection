# 📋 Kubernetes Log Access - Quick Reference

## 🚀 Easy Scripts (Recommended)

### Monitor All Services
```bash
./monitor-services.sh
```
Shows status and recent logs for all services.

### View Service Logs
```bash
# View all logs
./view-logs.sh <service-name>

# Follow logs in real-time (live tail)
./view-logs.sh <service-name> --follow

# Show last N lines
./view-logs.sh <service-name> --tail 50

# Show logs from last N minutes/hours
./view-logs.sh <service-name> --since 10m
./view-logs.sh <service-name> --since 1h
```

### Available Services
- `frontend`
- `login-management`
- `file-parsing`
- `qa-generation`
- `resources`
- `speechtotext`
- `mongodb`
- `mongo-express`

---

## 🔧 Direct kubectl Commands

### 1. List all pods
```bash
kubectl get pods -n reflection
```

### 2. View logs for a specific pod
```bash
# Get pod name first
kubectl get pods -n reflection

# View logs
kubectl logs -n reflection <pod-name>

# Follow logs (live)
kubectl logs -n reflection <pod-name> --follow

# Last 50 lines
kubectl logs -n reflection <pod-name> --tail 50

# Logs from last 10 minutes
kubectl logs -n reflection <pod-name> --since 10m
```

### 3. View logs for all pods of a service
```bash
# Frontend
kubectl logs -n reflection -l app=frontend --tail 20

# Login Management
kubectl logs -n reflection -l app=login-management --tail 20

# File Parsing
kubectl logs -n reflection -l app=file-parsing --tail 20
```

### 4. View logs from previous container (if crashed)
```bash
kubectl logs -n reflection <pod-name> --previous
```

### 5. Stream logs from multiple pods
```bash
# All frontend pods
kubectl logs -n reflection -l app=frontend --follow --max-log-requests 10
```

### 6. Get detailed pod information
```bash
kubectl describe pod -n reflection <pod-name>
```

### 7. Execute commands inside a container
```bash
# Get a shell
kubectl exec -it -n reflection <pod-name> -- /bin/bash

# Or use sh if bash not available
kubectl exec -it -n reflection <pod-name> -- /bin/sh

# Run a single command
kubectl exec -n reflection <pod-name> -- ls -la
kubectl exec -n reflection <pod-name> -- env
kubectl exec -n reflection <pod-name> -- ps aux
```

### 8. Check container resource usage
```bash
kubectl top pods -n reflection
```

---

## 📊 Real-World Examples

### Example 1: Debug frontend issues
```bash
# Check if frontend is running
kubectl get pods -n reflection -l app=frontend

# View recent logs
./view-logs.sh frontend --tail 50

# Follow live logs
./view-logs.sh frontend --follow
```

### Example 2: Check login failures
```bash
# View login service logs
./view-logs.sh login-management --tail 100

# Filter for errors (in logs)
kubectl logs -n reflection -l app=login-management | grep -i error
```

### Example 3: Monitor file uploads
```bash
# Follow file-parsing logs in real-time
./view-logs.sh file-parsing --follow
```

### Example 4: Check all services at once
```bash
# Quick overview
./monitor-services.sh

# Detailed view of all pods
kubectl get pods -n reflection -o wide
```

### Example 5: Debug crashed pod
```bash
# Check which pods are crashing
kubectl get pods -n reflection | grep -E "Error|CrashLoopBackOff"

# View logs from crashed container
kubectl logs -n reflection <crashed-pod-name> --previous

# Describe to see events
kubectl describe pod -n reflection <crashed-pod-name>
```

---

## 🎯 Quick Tips

1. **Use scripts for quick access**: `./view-logs.sh` and `./monitor-services.sh`
2. **Follow logs when testing**: Use `--follow` to see real-time activity
3. **Check previous logs if crashed**: Use `--previous` flag
4. **Filter logs**: Pipe to `grep` for specific patterns
5. **Save logs to file**: Add `> logs.txt` to any command

### Save logs to file
```bash
./view-logs.sh frontend > frontend-logs.txt
kubectl logs -n reflection <pod-name> > pod-logs.txt
```

### Filter logs
```bash
# Find errors
kubectl logs -n reflection <pod-name> | grep -i error

# Find specific requests
kubectl logs -n reflection <pod-name> | grep "POST"

# Count log lines
kubectl logs -n reflection <pod-name> | wc -l
```

---

## 🔗 Service Status

### Check all services
```bash
kubectl get all -n reflection
```

### Check specific service
```bash
kubectl get service -n reflection frontend-service
kubectl get deployment -n reflection frontend-deployment
kubectl get pods -n reflection -l app=frontend
```

### Check ingress
```bash
kubectl get ingress -n reflection
kubectl describe ingress -n reflection reflection-ingress-simple
```

---

## 📝 Current Status Summary (from monitor)

✅ **Running (5/6 services):**
- Frontend: 2/2 pods
- Login Management: 2/2 pods
- File Parsing: 2/2 pods
- Resources: 2/2 pods
- SpeechToText: 1/2 pods (1 pending)

❌ **Not Running:**
- QA Generation: 0/2 (CrashLoopBackOff - needs v1.0 image)

🌐 **Access:**
- Application: http://localhost:5000
- Ingress Controller: Running with path-based routing
