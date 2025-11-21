# Kubernetes Testing Commands - Reflection Application

## 📋 Table of Contents
1. [Basic Cluster Information](#basic-cluster-information)
2. [Pod Management](#pod-management)
3. [Self-Healing Test](#self-healing-test)
4. [Scaling Tests](#scaling-tests)
5. [Rolling Updates](#rolling-updates)
6. [Service & Networking](#service--networking)
7. [Resource Monitoring](#resource-monitoring)
8. [Logs & Debugging](#logs--debugging)
9. [ConfigMaps & Secrets](#configmaps--secrets)
10. [Advanced Testing](#advanced-testing)

---

## Basic Cluster Information

### Check Cluster Nodes
```bash
# List all nodes
kubectl get nodes

# Detailed node information
kubectl get nodes -o wide

# Node resource capacity
kubectl describe nodes
```

### Check All Resources
```bash
# All resources in reflection namespace
kubectl get all -n reflection

# All resources across all namespaces
kubectl get all --all-namespaces

# Specific resource types
kubectl get pods,svc,deployments,rs,ing -n reflection
```

### Namespace Information
```bash
# List all namespaces
kubectl get namespaces

# Get namespace details
kubectl describe namespace reflection
```

---

## Pod Management

### List Pods
```bash
# All pods in reflection namespace
kubectl get pods -n reflection

# Wide output (shows node, IP)
kubectl get pods -n reflection -o wide

# Watch pods in real-time
kubectl get pods -n reflection -w

# Filter by label
kubectl get pods -n reflection -l app=frontend
kubectl get pods -n reflection -l tier=backend
```

### Pod Details
```bash
# Describe a specific pod
kubectl describe pod -n reflection <pod-name>

# Get pod YAML
kubectl get pod -n reflection <pod-name> -o yaml

# Get pod JSON
kubectl get pod -n reflection <pod-name> -o json
```

### Pod Status Check
```bash
# Running pods only
kubectl get pods -n reflection --field-selector=status.phase=Running

# Pending pods
kubectl get pods -n reflection --field-selector=status.phase=Pending

# Failed pods
kubectl get pods -n reflection --field-selector=status.phase=Failed
```

---

## Self-Healing Test

### Test 1: Delete a Single Pod
```bash
# Get current frontend pods
kubectl get pods -n reflection -l app=frontend

# Delete one pod
kubectl delete pod -n reflection <pod-name>

# Watch automatic recreation
kubectl get pods -n reflection -l app=frontend -w

# Verify service still works
curl http://localhost:5000/health
```

### Test 2: Delete All Pods of a Service
```bash
# Delete all frontend pods
kubectl delete pods -n reflection -l app=frontend

# Watch recreation
kubectl get pods -n reflection -l app=frontend -w

# Check deployment status
kubectl get deployment -n reflection frontend-deployment
```

### Test 3: Simulate Crash
```bash
# Get a pod name
kubectl get pods -n reflection -l app=frontend

# Kill the main process inside container
kubectl exec -n reflection <pod-name> -- kill 1

# Watch pod restart
kubectl get pods -n reflection -l app=frontend -w
```

---

## Scaling Tests

### Scale Up
```bash
# Check current replicas
kubectl get deployment -n reflection frontend-deployment

# Scale up to 3 replicas
kubectl scale deployment -n reflection frontend-deployment --replicas=3

# Watch pods being created
kubectl get pods -n reflection -l app=frontend -w

# Verify deployment status
kubectl get deployment -n reflection frontend-deployment
```

### Scale Down
```bash
# Scale down to 1 replica
kubectl scale deployment -n reflection frontend-deployment --replicas=1

# Watch pods terminating
kubectl get pods -n reflection -l app=frontend -w
```

### Scale to Zero (Pause Service)
```bash
# Scale to 0 (stops service)
kubectl scale deployment -n reflection resources-deployment --replicas=0

# Verify no pods running
kubectl get pods -n reflection -l app=resources

# Scale back up
kubectl scale deployment -n reflection resources-deployment --replicas=2
```

### Scale Multiple Services
```bash
# Scale frontend
kubectl scale deployment -n reflection frontend-deployment --replicas=3

# Scale login-management
kubectl scale deployment -n reflection login-management-deployment --replicas=3

# Scale file-parsing
kubectl scale deployment -n reflection file-parsing-deployment --replicas=3

# Check all deployments
kubectl get deployments -n reflection
```

---

## Rolling Updates

### Update Image Version
```bash
# Check current image
kubectl get deployment -n reflection frontend-deployment -o jsonpath='{.spec.template.spec.containers[0].image}'

# Update to new image version
kubectl set image deployment/frontend-deployment -n reflection frontend=frontend:v2.0

# Watch rolling update
kubectl rollout status deployment/frontend-deployment -n reflection

# Check rollout history
kubectl rollout history deployment/frontend-deployment -n reflection
```

### Rollback Update
```bash
# Rollback to previous version
kubectl rollout undo deployment/frontend-deployment -n reflection

# Rollback to specific revision
kubectl rollout undo deployment/frontend-deployment -n reflection --to-revision=1

# Check rollback status
kubectl rollout status deployment/frontend-deployment -n reflection
```

### Pause and Resume Rollout
```bash
# Pause rollout
kubectl rollout pause deployment/frontend-deployment -n reflection

# Resume rollout
kubectl rollout resume deployment/frontend-deployment -n reflection
```

---

## Service & Networking

### List Services
```bash
# All services
kubectl get services -n reflection

# Wide output
kubectl get services -n reflection -o wide

# Specific service details
kubectl describe service -n reflection frontend-service
```

### Test Service Endpoints
```bash
# Get service endpoints
kubectl get endpoints -n reflection

# Describe specific endpoint
kubectl describe endpoints -n reflection frontend-service
```

### Ingress Testing
```bash
# Get ingress
kubectl get ingress -n reflection

# Describe ingress
kubectl describe ingress -n reflection reflection-ingress-simple

# Test ingress rules
curl http://localhost:5000/
curl http://localhost:5000/api/login/health
curl http://localhost:5000/api/resources/health
```

### Port Forwarding Tests
```bash
# Port forward to a specific pod
kubectl port-forward -n reflection <pod-name> 8080:5000

# Port forward to a service
kubectl port-forward -n reflection service/frontend-service 8080:80

# Port forward to deployment
kubectl port-forward -n reflection deployment/frontend-deployment 8080:5000
```

### DNS Resolution Test
```bash
# Execute inside a pod
kubectl exec -it -n reflection <pod-name> -- /bin/sh

# Inside the pod, test DNS
nslookup frontend-service
nslookup login-management-service.reflection.svc.cluster.local
curl http://frontend-service/health
```

---

## Resource Monitoring

### Pod Resource Usage
```bash
# Install metrics-server first (if not installed)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Get pod resource usage
kubectl top pods -n reflection

# Sort by CPU
kubectl top pods -n reflection --sort-by=cpu

# Sort by memory
kubectl top pods -n reflection --sort-by=memory
```

### Node Resource Usage
```bash
# Node resource usage
kubectl top nodes

# Detailed node resources
kubectl describe nodes | grep -A 5 "Allocated resources"
```

### Resource Limits Check
```bash
# Check pod resource limits
kubectl get pods -n reflection -o json | jq '.items[] | {name: .metadata.name, resources: .spec.containers[].resources}'

# Describe deployment resources
kubectl describe deployment -n reflection frontend-deployment | grep -A 10 "Limits"
```

---

## Logs & Debugging

### View Logs
```bash
# View pod logs
kubectl logs -n reflection <pod-name>

# Follow logs (tail -f)
kubectl logs -n reflection <pod-name> --follow

# Last 50 lines
kubectl logs -n reflection <pod-name> --tail=50

# Logs since 10 minutes ago
kubectl logs -n reflection <pod-name> --since=10m

# Logs from previous container (if crashed)
kubectl logs -n reflection <pod-name> --previous
```

### Multiple Pod Logs
```bash
# All frontend pod logs
kubectl logs -n reflection -l app=frontend --tail=20

# Stream logs from all pods
kubectl logs -n reflection -l app=frontend --follow --max-log-requests=10
```

### Execute Commands in Pod
```bash
# Get a shell
kubectl exec -it -n reflection <pod-name> -- /bin/bash

# Or use sh
kubectl exec -it -n reflection <pod-name> -- /bin/sh

# Run single command
kubectl exec -n reflection <pod-name> -- ls -la
kubectl exec -n reflection <pod-name> -- env
kubectl exec -n reflection <pod-name> -- ps aux
kubectl exec -n reflection <pod-name> -- cat /etc/os-release

# Check Python packages
kubectl exec -n reflection <pod-name> -- pip list
```

### Debug Pod Issues
```bash
# Describe pod (shows events)
kubectl describe pod -n reflection <pod-name>

# Check events
kubectl get events -n reflection --sort-by='.lastTimestamp'

# Check events for specific pod
kubectl get events -n reflection --field-selector involvedObject.name=<pod-name>
```

---

## ConfigMaps & Secrets

### ConfigMaps
```bash
# List ConfigMaps
kubectl get configmaps -n reflection

# Describe ConfigMap
kubectl describe configmap -n reflection reflection-config

# Get ConfigMap data
kubectl get configmap -n reflection reflection-config -o yaml

# Edit ConfigMap
kubectl edit configmap -n reflection reflection-config
```

### Secrets
```bash
# List secrets
kubectl get secrets -n reflection

# Describe secret (doesn't show values)
kubectl describe secret -n reflection reflection-secrets

# Get secret values (base64 encoded)
kubectl get secret -n reflection reflection-secrets -o yaml

# Decode secret
kubectl get secret -n reflection reflection-secrets -o jsonpath='{.data.MONGODB_PASSWORD}' | base64 --decode
```

---

## Advanced Testing

### Network Policy Testing
```bash
# Check if network policies exist
kubectl get networkpolicies -n reflection

# Test connectivity between pods
kubectl exec -it -n reflection <frontend-pod> -- curl http://login-management-service:5001/health
```

### Persistent Volume Testing
```bash
# List PVs and PVCs
kubectl get pv
kubectl get pvc -n reflection

# Describe PVC
kubectl describe pvc -n reflection mongodb-pvc

# Check PV status
kubectl get pv -o wide
```

### Stress Testing
```bash
# Create multiple requests
for i in {1..100}; do curl http://localhost:5000/health & done

# Monitor pod CPU/Memory during load
kubectl top pods -n reflection --watch
```

### Pod Disruption Budget
```bash
# Check if PDB exists
kubectl get pdb -n reflection

# Create a simple PDB for testing
kubectl create pdb frontend-pdb --selector=app=frontend --min-available=1 -n reflection
```

### Liveness/Readiness Probe Testing
```bash
# Check probe configuration
kubectl get pod -n reflection <pod-name> -o json | jq '.spec.containers[].livenessProbe'
kubectl get pod -n reflection <pod-name> -o json | jq '.spec.containers[].readinessProbe'

# Simulate probe failure (if possible)
kubectl exec -n reflection <pod-name> -- rm /tmp/healthy
```

### Resource Quota Testing
```bash
# Check resource quotas
kubectl get resourcequota -n reflection

# Describe quota
kubectl describe resourcequota -n reflection
```

---

## Quick Test Scenarios

### Scenario 1: Complete Service Test
```bash
# 1. Check service is running
kubectl get pods -n reflection -l app=frontend

# 2. Test health endpoint
curl http://localhost:5000/health

# 3. Delete pod to test self-healing
kubectl delete pod -n reflection <frontend-pod-name>

# 4. Verify new pod created
kubectl get pods -n reflection -l app=frontend

# 5. Test service still works
curl http://localhost:5000/health
```

### Scenario 2: Scale and Load Balance Test
```bash
# 1. Scale to 3 replicas
kubectl scale deployment -n reflection frontend-deployment --replicas=3

# 2. Verify 3 pods running
kubectl get pods -n reflection -l app=frontend

# 3. Check service endpoints
kubectl get endpoints -n reflection frontend-service

# 4. Test load balancing (make multiple requests)
for i in {1..10}; do curl http://localhost:5000/health; done

# 5. Scale back to 2
kubectl scale deployment -n reflection frontend-deployment --replicas=2
```

### Scenario 3: Rolling Update Test
```bash
# 1. Check current version
kubectl get deployment -n reflection frontend-deployment -o jsonpath='{.spec.template.spec.containers[0].image}'

# 2. Watch pods before update
kubectl get pods -n reflection -l app=frontend -w &

# 3. Update image (simulate update)
kubectl set image deployment/frontend-deployment -n reflection frontend=frontend:v1.1

# 4. Watch rolling update
kubectl rollout status deployment/frontend-deployment -n reflection

# 5. Rollback if needed
kubectl rollout undo deployment/frontend-deployment -n reflection
```

### Scenario 4: Multi-Service Communication Test
```bash
# 1. Get a frontend pod
FRONTEND_POD=$(kubectl get pods -n reflection -l app=frontend -o jsonpath='{.items[0].metadata.name}')

# 2. Test internal service communication
kubectl exec -n reflection $FRONTEND_POD -- curl http://login-management-service:5001/health
kubectl exec -n reflection $FRONTEND_POD -- curl http://resources-service:5004/health

# 3. Test DNS resolution
kubectl exec -n reflection $FRONTEND_POD -- nslookup login-management-service
```

---

## Cleanup Commands

### Delete Specific Resources
```bash
# Delete a deployment
kubectl delete deployment -n reflection <deployment-name>

# Delete a service
kubectl delete service -n reflection <service-name>

# Delete a pod (will be recreated by deployment)
kubectl delete pod -n reflection <pod-name>

# Force delete stuck pod
kubectl delete pod -n reflection <pod-name> --force --grace-period=0
```

### Delete All Application Resources
```bash
# Delete all deployments
kubectl delete deployments -n reflection --all

# Delete all services
kubectl delete services -n reflection --all

# Delete ingress
kubectl delete ingress -n reflection --all
```

### Clean Namespace
```bash
# Delete everything in namespace (careful!)
kubectl delete all --all -n reflection

# Delete namespace entirely
kubectl delete namespace reflection
```

---

## Useful Aliases (Add to ~/.zshrc or ~/.bashrc)

```bash
# Kubectl shortcuts
alias k='kubectl'
alias kgp='kubectl get pods -n reflection'
alias kgs='kubectl get services -n reflection'
alias kgd='kubectl get deployments -n reflection'
alias kl='kubectl logs -n reflection'
alias kd='kubectl describe -n reflection'
alias ke='kubectl exec -it -n reflection'
alias kw='kubectl get pods -n reflection -w'

# Application specific
alias monitor='./monitor-services.sh'
alias logs='./view-logs.sh'
alias ingress='./start-ingress.sh'
```

---

## Tips & Best Practices

1. **Always specify namespace** with `-n reflection` to avoid mistakes
2. **Use labels** for filtering: `-l app=frontend`
3. **Watch mode** is great for seeing changes: `-w`
4. **Use describe** for debugging: `kubectl describe pod <name>`
5. **Check events** when troubleshooting: `kubectl get events`
6. **Use scripts** for common tasks (monitor-services.sh, view-logs.sh)
7. **Test in order**: Basic → Self-Healing → Scaling → Updates
8. **Always verify** services work after changes
9. **Save important outputs** to files for documentation
10. **Use dry-run** for testing commands: `--dry-run=client -o yaml`

---

## Quick Reference Card

| Task | Command |
|------|---------|
| List pods | `kubectl get pods -n reflection` |
| Delete pod | `kubectl delete pod -n reflection <name>` |
| Scale up | `kubectl scale deployment <name> --replicas=3 -n reflection` |
| View logs | `kubectl logs -n reflection <pod-name>` |
| Follow logs | `kubectl logs -n reflection <pod-name> -f` |
| Get shell | `kubectl exec -it -n reflection <pod-name> -- /bin/bash` |
| Describe pod | `kubectl describe pod -n reflection <pod-name>` |
| Check service | `kubectl get svc -n reflection` |
| Port forward | `kubectl port-forward -n reflection <pod-name> 8080:5000` |
| Top pods | `kubectl top pods -n reflection` |

---

## Environment-Specific Information

### Current Reflection Application Setup

**Namespace**: `reflection`

**Services**:
- `frontend` - Port 5000 (via LoadBalancer on 80)
- `login-management` - Port 5001
- `file-parsing` - Port 5002
- `qa-generation` - Port 5003
- `resources` - Port 5004
- `speechtotext` - Port 5005
- `mongodb` - Port 27017
- `mongo-express` - Port 8081

**Access**:
- Application: http://localhost:5000 (via ingress)
- Ingress Controller: Port 5000 → 80

**Deployments**:
- Each service has 2 replicas (except QA Generation)
- Rolling update strategy
- Health probes configured

---

**Last Updated**: November 13, 2025
**Kubernetes Version**: v1.31.1
**Platform**: Docker Desktop
