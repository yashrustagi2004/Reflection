# Kubernetes Dashboard Access Guide

## 🎨 What is Kubernetes Dashboard?

Kubernetes Dashboard is a web-based user interface that allows you to:
- View cluster resources (pods, services, deployments)
- Monitor resource usage (CPU, memory)
- View logs and events
- Create and modify resources
- Troubleshoot applications
- View cluster health

## 🚀 Quick Start

### Method 1: Using the Script (Recommended)
```bash
./start-dashboard.sh
```

This script will:
1. ✅ Check if dashboard is installed
2. ✅ Generate access token
3. ✅ Start port-forward
4. ✅ Show you the URL and token

### Method 2: Manual Access

#### Step 1: Start Port Forward
```bash
kubectl port-forward -n kubernetes-dashboard service/kubernetes-dashboard 8443:443
```

#### Step 2: Get Access Token
```bash
kubectl -n kubernetes-dashboard create token admin-user
```

#### Step 3: Access Dashboard
Open browser: https://localhost:8443

## 🔐 Login Instructions

1. **Open URL**: https://localhost:8443
2. **Accept Security Warning**: 
   - Chrome/Edge: Click "Advanced" → "Proceed to localhost (unsafe)"
   - Firefox: Click "Advanced" → "Accept the Risk and Continue"
3. **Select Token** authentication method
4. **Paste the token** you got from the command
5. **Click Sign In**

## 📊 Dashboard Features

### Overview Page
- Cluster resource usage
- Running workloads
- Recent events
- Namespace overview

### Workloads
- **Pods**: View all pods, their status, and logs
- **Deployments**: Manage deployments, scale replicas
- **ReplicaSets**: View replica sets
- **StatefulSets**: Manage stateful applications
- **DaemonSets**: View daemon sets
- **Jobs/CronJobs**: Manage batch jobs

### Services
- **Services**: View all services and endpoints
- **Ingresses**: Manage ingress rules
- **Network Policies**: View network policies

### Config and Storage
- **ConfigMaps**: View and edit config maps
- **Secrets**: View secrets (values are hidden)
- **Persistent Volumes**: Manage PVs and PVCs

### Cluster
- **Nodes**: View node status and resources
- **Namespaces**: Switch between namespaces
- **Events**: View cluster events
- **Roles**: View RBAC configuration

## 🎯 Common Tasks in Dashboard

### View Pod Logs
1. Go to **Workloads** → **Pods**
2. Select namespace: `reflection`
3. Click on a pod name
4. Click **Logs** icon at the top

### Scale Deployment
1. Go to **Workloads** → **Deployments**
2. Select namespace: `reflection`
3. Click on deployment name
4. Click **Scale** icon
5. Enter new replica count
6. Click **Scale**

### Delete a Pod
1. Go to **Workloads** → **Pods**
2. Select namespace: `reflection`
3. Check the pod you want to delete
4. Click **Delete** icon
5. Confirm deletion

### View Events
1. Go to **Cluster** → **Events**
2. Select namespace: `reflection`
3. View recent events sorted by time

### Execute into Container
1. Go to **Workloads** → **Pods**
2. Click on pod name
3. Click **Exec** icon (terminal icon)
4. Select container (if multiple)
5. Execute commands

### Monitor Resources
1. View CPU/Memory usage on Overview page
2. Click on individual pods/nodes for detailed metrics
3. View resource graphs over time

## 🔄 Token Management

### Create New Token
```bash
kubectl -n kubernetes-dashboard create token admin-user
```

### Create Long-Lived Token (24 hours)
```bash
kubectl -n kubernetes-dashboard create token admin-user --duration=24h
```

### Create Persistent Token (as Secret)
```bash
kubectl create -f - <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: admin-user-token
  namespace: kubernetes-dashboard
  annotations:
    kubernetes.io/service-account.name: admin-user
type: kubernetes.io/service-account-token
EOF

# Get the token
kubectl get secret admin-user-token -n kubernetes-dashboard -o jsonpath='{.data.token}' | base64 --decode
```

## 🛠️ Troubleshooting

### Dashboard Not Loading
```bash
# Check if dashboard pods are running
kubectl get pods -n kubernetes-dashboard

# Check dashboard service
kubectl get svc -n kubernetes-dashboard

# Restart dashboard
kubectl rollout restart deployment/kubernetes-dashboard -n kubernetes-dashboard
```

### Token Invalid
```bash
# Create a new token
kubectl -n kubernetes-dashboard create token admin-user
```

### Port Already in Use
```bash
# Use a different port
kubectl port-forward -n kubernetes-dashboard service/kubernetes-dashboard 9443:443

# Access at: https://localhost:9443
```

### Cannot Access After Port Forward
```bash
# Check if port-forward is running
ps aux | grep port-forward

# Kill existing port-forwards
pkill -f "port-forward.*kubernetes-dashboard"

# Restart
kubectl port-forward -n kubernetes-dashboard service/kubernetes-dashboard 8443:443
```

## 🔒 Security Notes

### Current Setup
- ✅ Admin user has **cluster-admin** role (full access)
- ✅ Token-based authentication
- ✅ HTTPS enabled
- ✅ Only accessible via localhost

### For Production
Consider these additional security measures:
1. Create users with limited permissions
2. Use namespace-specific roles
3. Enable audit logging
4. Use a proper ingress with authentication
5. Integrate with OAuth/OIDC

## 📝 Useful Commands

```bash
# Check dashboard status
kubectl get all -n kubernetes-dashboard

# View dashboard logs
kubectl logs -n kubernetes-dashboard -l k8s-app=kubernetes-dashboard

# Describe dashboard service
kubectl describe svc kubernetes-dashboard -n kubernetes-dashboard

# Get dashboard URL (if exposed)
kubectl get svc -n kubernetes-dashboard

# Restart dashboard
kubectl rollout restart deployment/kubernetes-dashboard -n kubernetes-dashboard

# Delete dashboard (if needed)
kubectl delete namespace kubernetes-dashboard

# Reinstall dashboard
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml
```

## 🌐 Alternative Access Methods

### Method 1: NodePort (Not recommended for Docker Desktop)
```bash
# Edit service to use NodePort
kubectl edit service kubernetes-dashboard -n kubernetes-dashboard

# Change type: ClusterIP to type: NodePort
# Access via: https://localhost:<node-port>
```

### Method 2: Ingress (Advanced)
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: dashboard-ingress
  namespace: kubernetes-dashboard
spec:
  rules:
  - host: dashboard.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: kubernetes-dashboard
            port:
              number: 443
```

## 📊 Dashboard vs kubectl

| Task | Dashboard | kubectl |
|------|-----------|---------|
| Visual Overview | ✅ Excellent | ❌ Limited |
| Quick Actions | ✅ Easy | ⚠️ Need commands |
| Automation | ❌ Manual | ✅ Scriptable |
| Learning Curve | ✅ Low | ⚠️ Medium |
| Remote Access | ⚠️ Need setup | ✅ Built-in |
| Resource Usage | ⚠️ Uses resources | ✅ Minimal |

## 🎓 Tips for Using Dashboard

1. **Start with Overview** - Get a quick cluster health check
2. **Use Namespace Filter** - Focus on your application (reflection)
3. **Bookmark Token** - Save it in a password manager
4. **Check Events** - First place to debug issues
5. **Use Logs View** - Easier than kubectl logs
6. **Scale with Caution** - Test in dev first
7. **Watch Resources** - Monitor CPU/Memory usage
8. **Use Search** - Filter long lists quickly

## 📍 Current Reflection Application in Dashboard

After logging in, to view your application:

1. **Select Namespace**: `reflection` (top dropdown)
2. **View Workloads**:
   - Deployments: frontend, login-management, file-parsing, resources, speechtotext
   - Pods: Click to view logs and status
3. **View Services**: All 8 services listed
4. **View Ingress**: reflection-ingress-simple
5. **View ConfigMaps**: reflection-config
6. **View Secrets**: reflection-secrets

## 🔗 Useful Links

- [Official Docs](https://kubernetes.io/docs/tasks/access-application-cluster/web-ui-dashboard/)
- [Dashboard GitHub](https://github.com/kubernetes/dashboard)
- [Dashboard Releases](https://github.com/kubernetes/dashboard/releases)

---

**Access Token Valid For**: 1 hour (default)

**Dashboard URL**: https://localhost:8443

**Admin User**: admin-user (cluster-admin privileges)
