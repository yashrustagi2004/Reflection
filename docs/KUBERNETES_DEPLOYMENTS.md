# Kubernetes Deployment Manifests - Complete Guide

## 📦 Overview

Production-ready Kubernetes deployment and service manifests for all 6 Reflection microservices, following DevOps security best practices.

**Created:** November 13, 2025
**Namespace:** reflection
**Total Services:** 6

---

## 🏗️ Architecture

### Service Topology

```
┌─────────────────────────────────────────────────────────────┐
│                         Internet                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                ┌────────▼─────────┐
                │  LoadBalancer    │
                │  (Port 80)       │
                └────────┬─────────┘
                         │
            ┌────────────▼──────────────┐
            │   Frontend Service        │
            │   (Port 5000)             │
            │   - Web Interface         │
            │   - Session Management    │
            └─┬─────────────────────────┘
              │
    ┌─────────┼─────────────────────────────┐
    │         │                             │
┌───▼────┐ ┌─▼────┐ ┌──────┐ ┌──────┐ ┌──▼──┐
│Login   │ │File  │ │  QA  │ │Speech│ │Res  │
│Mgmt    │ │Parse │ │ Gen  │ │2Text │ │ource│
│:5001   │ │:5002 │ │:5003 │ │:5004 │ │:5005│
└───┬────┘ └──┬───┘ └───┬──┘ └───┬──┘ └──┬──┘
    │         │         │        │        │
    └─────────┴─────────┴────────┴────────┘
                     │
              ┌──────▼───────┐
              │   MongoDB    │
              │   :27017     │
              └──────────────┘
```

---

## 📋 Created Manifests

| Service | File | Type | Replicas | Memory | CPU |
|---------|------|------|----------|--------|-----|
| Frontend | `frontend.yaml` | LoadBalancer | 2 | 512Mi | 500m |
| Login Management | `login-management.yaml` | ClusterIP | 2 | 512Mi | 500m |
| File Parsing | `file-parsing.yaml` | ClusterIP | 2 | 1Gi | 1000m |
| QA Generation | `qa-generation.yaml` | ClusterIP | 2 | 2Gi | 1500m |
| Speech-to-Text | `speechtotext.yaml` | ClusterIP | 2 | 1Gi | 1000m |
| Resources | `resources.yaml` | ClusterIP | 2 | 1.5Gi | 1000m |

**Total Resource Requests:** 
- Memory: ~7Gi
- CPU: ~5.75 cores

---

## 🔒 Security Best Practices Implemented

### 1. Pod Security Context ✅
```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 1000
  seccompProfile:
    type: RuntimeDefault
```

**Benefits:**
- Prevents root execution
- Consistent file permissions
- Secure computing mode enforced

### 2. Container Security Context ✅
```yaml
securityContext:
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: false  # Where appropriate
  runAsNonRoot: true
  runAsUser: 1000
  capabilities:
    drop:
    - ALL
```

**Benefits:**
- No privilege escalation
- Dropped all Linux capabilities
- Minimal attack surface

### 3. Resource Limits ✅
```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

**Benefits:**
- Prevents resource exhaustion
- Fair resource allocation
- Predictable performance

### 4. Health Probes ✅
- **Liveness Probe:** Restart unhealthy containers
- **Readiness Probe:** Remove from service rotation when not ready
- **Startup Probe:** Allow time for initialization

**Benefits:**
- Self-healing
- Zero-downtime deployments
- Prevents cascading failures

### 5. Rolling Updates ✅
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 0
```

**Benefits:**
- Zero-downtime deployments
- Gradual rollout
- Easy rollback

### 6. Network Policies (Recommended)
- Frontend: External access via LoadBalancer
- Backend services: Internal ClusterIP only
- MongoDB: No external access

### 7. Secrets Management ✅
- API keys in Kubernetes Secrets
- Never hardcoded in manifests
- Injected as environment variables

### 8. Image Pull Policy ✅
```yaml
imagePullPolicy: IfNotPresent
```

**Benefits:**
- Uses local images
- Faster deployments
- Consistent versions

---

## 📊 Service Details

### 1. Frontend Service
**File:** `frontend.yaml`
**Type:** LoadBalancer (External Access)
**Port:** 80 → 5000

**Features:**
- 2 replicas for high availability
- Session affinity (sticky sessions)
- External access via LoadBalancer
- Resource limits: 512Mi / 500m

**Health Checks:**
- Liveness: 30s initial, 10s period
- Readiness: 10s initial, 5s period
- Startup: 5s initial, 12 failures max (60s)

**Use Case:** Web interface, user interactions

---

### 2. Login Management Service
**File:** `login-management.yaml`
**Type:** ClusterIP (Internal Only)
**Port:** 5001

**Features:**
- JWT authentication
- OAuth2 integration
- Password hashing (bcrypt)
- MongoDB connection

**Health Checks:**
- Liveness: 30s initial, 10s period
- Readiness: 10s initial, 5s period
- Startup: 5s initial, 12 failures max

**Use Case:** User authentication, session management

---

### 3. File Parsing Service
**File:** `file-parsing.yaml`
**Type:** ClusterIP
**Port:** 5002

**Features:**
- PDF/DOCX parsing
- Vector embeddings
- Pinecone integration
- Volume mount for uploads (5Gi emptyDir)

**Resource Limits:** 1Gi / 1000m (higher for processing)

**Health Checks:**
- Liveness: 30s initial, 15s period
- Readiness: 15s initial, 10s period
- Startup: 10s initial, 20 failures max (100s for ML models)

**Use Case:** Resume/JD processing, vectorization

---

### 4. QA Generation Service
**File:** `qa-generation.yaml`
**Type:** ClusterIP
**Port:** 5003

**Features:**
- Google Gemini AI integration
- LangChain framework
- Pinecone vector search
- Context-aware questions

**Resource Limits:** 2Gi / 1500m (highest for AI workloads)

**Health Checks:**
- Liveness: 60s initial, 20s period (longer for AI)
- Readiness: 30s initial, 10s period
- Startup: 15s initial, 30 failures max (5 minutes)

**Use Case:** AI-powered question generation

---

### 5. Speech-to-Text Service
**File:** `speechtotext.yaml`
**Type:** ClusterIP
**Port:** 5004

**Features:**
- Google Speech Recognition
- FFmpeg audio processing
- Multiple format support
- Memory-backed temp storage (2Gi)

**Resource Limits:** 1Gi / 1000m (CPU intensive)

**Health Checks:**
- Liveness: 30s initial, 15s period
- Readiness: 15s initial, 10s period
- Startup: 10s initial, 20 failures max

**Volume:**
- emptyDir with Memory medium for fast I/O

**Use Case:** Audio transcription

---

### 6. Resources Service
**File:** `resources.yaml`
**Type:** ClusterIP
**Port:** 5005

**Features:**
- Learning resources management
- Document embeddings
- Vector similarity search
- Pinecone integration

**Resource Limits:** 1.5Gi / 1000m (ML embeddings)

**Health Checks:**
- Liveness: 45s initial, 15s period
- Readiness: 20s initial, 10s period
- Startup: 15s initial, 25 failures max (4 minutes)

**Use Case:** Resource recommendations, semantic search

---

## 🚀 Deployment Guide

### Prerequisites

Ensure the following exist:
```bash
# Check namespace
kubectl get namespace reflection

# Check ConfigMap
kubectl get configmap reflection-config -n reflection

# Check Secrets
kubectl get secret reflection-secrets -n reflection

# Check MongoDB
kubectl get deployment mongodb-deployment -n reflection

# Verify Docker images
docker images | grep reflection
```

---

### Quick Deployment

#### Option 1: Automated Script (Recommended)
```bash
./deploy-services.sh
```

**Features:**
- Validates prerequisites
- Deploys in correct order
- Waits for readiness
- Shows status summary
- Provides access information

---

#### Option 2: Manual Deployment
```bash
# Deploy all services
kubectl apply -f k8s/deployments/

# Or deploy individually
kubectl apply -f k8s/deployments/login-management.yaml
kubectl apply -f k8s/deployments/file-parsing.yaml
kubectl apply -f k8s/deployments/resources.yaml
kubectl apply -f k8s/deployments/qa-generation.yaml
kubectl apply -f k8s/deployments/speechtotext.yaml
kubectl apply -f k8s/deployments/frontend.yaml
```

---

### Verify Deployment

```bash
# Check deployments
kubectl get deployments -n reflection

# Check services
kubectl get services -n reflection

# Check pods
kubectl get pods -n reflection -o wide

# Watch pods status
kubectl get pods -n reflection -w

# Check specific deployment
kubectl describe deployment frontend-deployment -n reflection
```

---

### Access Application

#### LoadBalancer Access
```bash
# Get frontend LoadBalancer IP
kubectl get svc frontend-service -n reflection

# Access in browser
http://<EXTERNAL-IP>
```

#### Port-Forward (if LoadBalancer not available)
```bash
# Forward frontend to localhost
kubectl port-forward -n reflection svc/frontend-service 8080:80

# Access in browser
http://localhost:8080
```

---

## 📝 Management Commands

### View Logs

```bash
# All pods of a service
kubectl logs -n reflection -l app=frontend -f

# Specific pod
kubectl logs -n reflection <pod-name> -f

# Previous container (if crashed)
kubectl logs -n reflection <pod-name> --previous

# All containers in pod
kubectl logs -n reflection <pod-name> --all-containers=true
```

### Scale Services

```bash
# Scale up
kubectl scale deployment frontend-deployment -n reflection --replicas=3

# Scale down
kubectl scale deployment frontend-deployment -n reflection --replicas=1

# Auto-scale (HPA)
kubectl autoscale deployment frontend-deployment -n reflection \
  --cpu-percent=70 --min=2 --max=5
```

### Update Services

```bash
# Update image
kubectl set image deployment/frontend-deployment \
  frontend=reflection/frontend:v2 -n reflection

# Edit deployment
kubectl edit deployment frontend-deployment -n reflection

# Apply changes from file
kubectl apply -f k8s/deployments/frontend.yaml
```

### Rollback

```bash
# View rollout history
kubectl rollout history deployment/frontend-deployment -n reflection

# Rollback to previous version
kubectl rollout undo deployment/frontend-deployment -n reflection

# Rollback to specific revision
kubectl rollout undo deployment/frontend-deployment -n reflection --to-revision=2

# Check rollout status
kubectl rollout status deployment/frontend-deployment -n reflection
```

### Restart Services

```bash
# Restart deployment (rolling restart)
kubectl rollout restart deployment/frontend-deployment -n reflection

# Delete pod (will be recreated)
kubectl delete pod <pod-name> -n reflection
```

### Delete Services

```bash
# Delete specific service
kubectl delete -f k8s/deployments/frontend.yaml

# Delete all services
kubectl delete -f k8s/deployments/

# Delete by label
kubectl delete deployment,service -n reflection -l tier=backend
```

---

## 🐛 Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n reflection

# Describe pod for events
kubectl describe pod <pod-name> -n reflection

# Check logs
kubectl logs <pod-name> -n reflection

# Common issues:
# 1. Image pull errors - verify images exist locally
# 2. CrashLoopBackOff - check logs for application errors
# 3. ConfigMap/Secret missing - verify they exist
```

### ImagePullBackOff Error

```bash
# Verify image exists
docker images | grep reflection/frontend

# If missing, build images
./build-all-images.sh

# Check imagePullPolicy
kubectl get deployment frontend-deployment -n reflection -o yaml | grep imagePullPolicy
```

### Service Not Accessible

```bash
# Check service
kubectl get svc -n reflection

# Check endpoints
kubectl get endpoints frontend-service -n reflection

# Port-forward for testing
kubectl port-forward -n reflection svc/frontend-service 8080:80

# Check pod labels match service selector
kubectl get pods -n reflection --show-labels
```

### Pod Crashing

```bash
# View logs
kubectl logs <pod-name> -n reflection

# Check previous container logs
kubectl logs <pod-name> -n reflection --previous

# Common issues:
# 1. Missing environment variables
# 2. MongoDB connection failed
# 3. Missing API keys
# 4. Port already in use
```

### High Resource Usage

```bash
# Check resource usage
kubectl top pods -n reflection

# Check resource limits
kubectl describe pod <pod-name> -n reflection | grep -A 5 "Limits:"

# Adjust resources in manifest and reapply
```

### Health Check Failures

```bash
# Check probe configuration
kubectl describe pod <pod-name> -n reflection | grep -A 10 "Liveness:"

# Test health endpoint manually
kubectl exec -it <pod-name> -n reflection -- curl http://localhost:5000/health

# Adjust probe timings if needed
```

---

## 📊 Monitoring & Observability

### Basic Monitoring

```bash
# Resource usage
kubectl top pods -n reflection
kubectl top nodes

# Pod events
kubectl get events -n reflection --sort-by='.lastTimestamp'

# Service endpoints
kubectl get endpoints -n reflection
```

### Recommended Tools

1. **Prometheus + Grafana** - Metrics and dashboards
2. **ELK Stack** - Centralized logging
3. **Jaeger** - Distributed tracing
4. **Kubernetes Dashboard** - Visual interface

---

## 🔧 Performance Tuning

### Resource Optimization

```yaml
# For CPU-bound services (AI/ML)
resources:
  requests:
    cpu: "1000m"
  limits:
    cpu: "2000m"

# For memory-bound services (caching)
resources:
  requests:
    memory: "1Gi"
  limits:
    memory: "2Gi"
```

### Horizontal Pod Autoscaling

```bash
# Create HPA
kubectl autoscale deployment frontend-deployment -n reflection \
  --cpu-percent=70 \
  --min=2 \
  --max=10

# Check HPA status
kubectl get hpa -n reflection

# Describe HPA
kubectl describe hpa frontend-deployment -n reflection
```

### Pod Disruption Budget

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: frontend-pdb
  namespace: reflection
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: frontend
```

---

## 🎯 Production Checklist

Before going to production:

### Security
- [ ] Review and update all resource limits
- [ ] Enable Network Policies
- [ ] Implement Pod Security Policies/Standards
- [ ] Regular security scanning of images
- [ ] Rotate secrets regularly
- [ ] Enable audit logging

### Reliability
- [ ] Configure Horizontal Pod Autoscaling
- [ ] Set up Pod Disruption Budgets
- [ ] Implement proper backup strategy
- [ ] Configure alerting (Prometheus)
- [ ] Document disaster recovery procedures

### Monitoring
- [ ] Set up Prometheus metrics
- [ ] Configure Grafana dashboards
- [ ] Centralized logging (ELK/Loki)
- [ ] Distributed tracing (Jaeger)
- [ ] Health check monitoring

### Performance
- [ ] Load testing completed
- [ ] Resource limits tuned
- [ ] Database indexes optimized
- [ ] Caching strategy implemented
- [ ] CDN for static assets

---

## 📚 Additional Resources

- **Kubernetes Best Practices:** https://kubernetes.io/docs/concepts/configuration/overview/
- **Security Contexts:** https://kubernetes.io/docs/tasks/configure-pod-container/security-context/
- **Resource Management:** https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
- **Health Probes:** https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/

---

## ✨ Summary

**Created:**
- ✅ 6 production-ready deployment manifests
- ✅ 6 service definitions (1 LoadBalancer, 5 ClusterIP)
- ✅ Security best practices implemented
- ✅ Resource limits configured
- ✅ Health probes for all services
- ✅ Rolling update strategy
- ✅ High availability (2 replicas each)
- ✅ Automated deployment script

**Next Steps:**
1. Run `./deploy-services.sh`
2. Wait for pods to be ready
3. Access frontend via LoadBalancer IP
4. Test application end-to-end
5. Monitor logs and metrics

**Status:** 🚀 Ready for Deployment!
