# Metrics-Server Fix for Docker Desktop

**Issue:** `kubectl top nodes` fails with "Metrics API not available"  
**Solution:** Use patched metrics-server configuration  
**Status:** ✅ FIXED

---

## 🎯 Quick Fix

The standard metrics-server doesn't work with Docker Desktop because of TLS certificate verification issues. Use our patched version:

```bash
# Apply the patched metrics-server
kubectl apply -f k8s/metrics-server-docker-desktop.yaml

# Wait 30 seconds for it to start
sleep 30

# Test it works
kubectl top nodes
```

---

## 🔧 What Was Changed?

The key changes in our patched version:

1. **Added `--kubelet-insecure-tls`** - Skips TLS verification for Docker Desktop
2. **Set `insecureSkipTLSVerify: true`** in APIService - Required for Docker Desktop
3. **Updated image to v0.7.1** - Latest stable version

These changes make metrics-server compatible with Docker Desktop's self-signed certificates.

---

## 📊 Usage Examples

### Check Node Resources

```bash
# View node CPU and memory usage
kubectl top nodes

# Output example:
# NAME                    CPU(cores)   CPU%   MEMORY(bytes)   MEMORY%   
# desktop-control-plane   121m         1%     878Mi           23%       
# desktop-worker          38m          0%     179Mi           4%        
# desktop-worker2         28m          0%     143Mi           3%
```

### Check Pod Resources

```bash
# View pod resources in reflection namespace
kubectl top pods -n reflection

# View all pods
kubectl top pods -A

# Sort by CPU
kubectl top pods -n reflection --sort-by=cpu

# Sort by memory
kubectl top pods -n reflection --sort-by=memory
```

### Monitor in Real-Time

```bash
# Watch node metrics (updates every 2 seconds)
watch -n 2 kubectl top nodes

# Watch pod metrics
watch -n 2 kubectl top pods -n reflection
```

---

## 🔍 Verify Metrics-Server Health

```bash
# Check deployment status
kubectl get deployment metrics-server -n kube-system

# Check pod status
kubectl get pods -n kube-system -l k8s-app=metrics-server

# Check logs if issues
kubectl logs -n kube-system -l k8s-app=metrics-server

# Check API service
kubectl get apiservice v1beta1.metrics.k8s.io
```

---

## 🔄 If Metrics-Server Stops Working

After system restart, if metrics-server isn't working:

```bash
# Check if it's running
kubectl get pods -n kube-system -l k8s-app=metrics-server

# If not running, reapply
kubectl delete -f k8s/metrics-server-docker-desktop.yaml
kubectl apply -f k8s/metrics-server-docker-desktop.yaml

# Wait for it to be ready
kubectl wait --for=condition=ready pod -l k8s-app=metrics-server -n kube-system --timeout=60s
```

---

## 🚨 Troubleshooting

### Error: "Metrics API not available"

**Solution:**
```bash
# Check if metrics-server pod is running
kubectl get pods -n kube-system -l k8s-app=metrics-server

# If not running or crashlooping, check logs
kubectl logs -n kube-system -l k8s-app=metrics-server

# Common fix: reapply the configuration
kubectl apply -f k8s/metrics-server-docker-desktop.yaml
```

### Error: "unable to fully collect metrics"

**Solution:** Wait 30-60 seconds. Metrics-server needs time to collect initial data.

```bash
# Wait and retry
sleep 30
kubectl top nodes
```

### Error: Pod in CrashLoopBackOff

**Solution:** Delete and recreate
```bash
kubectl delete deployment metrics-server -n kube-system
kubectl apply -f k8s/metrics-server-docker-desktop.yaml
```

---

## 📝 Notes

- **Metrics-server persists** across restarts (it's a Kubernetes deployment)
- **Initial data collection** takes 15-30 seconds after startup
- **Metrics update** every 15 seconds (configured via `--metric-resolution=15s`)
- **Not for production** - This configuration skips TLS verification (Docker Desktop only)

For production clusters, use the standard metrics-server without the insecure flags.

---

## 🎓 What is Metrics-Server?

Metrics-server is a cluster-wide aggregator of resource usage data. It collects metrics from:

- **Kubelets** on each node
- **Container runtime** (Docker/containerd)
- **Node-level statistics**

Used by:
- `kubectl top` commands
- Horizontal Pod Autoscaler (HPA)
- Vertical Pod Autoscaler (VPA)
- Dashboard visualizations

---

## ✅ Verification Checklist

After applying metrics-server:

- [ ] Pod is running: `kubectl get pods -n kube-system -l k8s-app=metrics-server`
- [ ] API service available: `kubectl get apiservice v1beta1.metrics.k8s.io`
- [ ] Node metrics work: `kubectl top nodes`
- [ ] Pod metrics work: `kubectl top pods -A`

---

**Last Updated:** November 13, 2025  
**Version:** 1.0  
**File Location:** `k8s/metrics-server-docker-desktop.yaml`
