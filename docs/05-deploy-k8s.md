# 05 — Deploy to Kubernetes

All manifests live in `k8s/`. Each `*-deployment.yaml` defines a `Deployment` (keeps N copies of a container running) and a `Service` (a stable network name + address for those copies) in one file.

> **Docker beginners:** a `Deployment` is "run this image, keep it running, restart it if it crashes." A `Service` is "give whatever's running a fixed DNS name" — Pods get replaced and get new IPs constantly, but the Service name never changes. That's how `gateway` reliably finds `smile-service` even after a restart.

## 1. Create the namespace

```bash
kubectl apply -f k8s/namespace.yaml
```

Everything below lives in the `ml-demo` namespace — keeps this demo isolated from anything else in the cluster.

## 2. Deploy the model services first

```bash
kubectl apply -f k8s/smile-deployment.yaml
kubectl apply -f k8s/glasses-deployment.yaml
kubectl apply -f k8s/eyes-deployment.yaml
```

## 3. Deploy the gateway

```bash
kubectl apply -f k8s/gateway-deployment.yaml
```

Look at the `env` block in this file — it points at `http://smile-service:8000` etc. Those hostnames resolve because of the `Service` objects you just created in step 2. Same names as `docker-compose.yml`, same mechanism, different implementation underneath.

## 4. Deploy the frontend

```bash
kubectl apply -f k8s/frontend-deployment.yaml
```

## 5. Watch it come up

```bash
kubectl get pods -n ml-demo -w
```

Wait for all 5 pods to show `Running` / `1/1`. Ctrl+C to stop watching.

If a pod is stuck in `ImagePullBackOff`: your image name in the manifest doesn't match what you pushed — go back to step 03 and confirm the `sed` command actually ran. Check with:

```bash
kubectl describe pod -n ml-demo <pod-name>
```

Next: [06 — Test the app](06-test-app.md)
