# Deploying to kind — full walkthrough

A single-file version of docs/04-06, for when you want to see the whole kind deployment in one pass instead of hopping between files. Covers **two ways to get your images onto the cluster**: pushing to Docker Hub first (the "real" path, matches the pipeline diagram), or loading local images directly into kind (faster, no Docker Hub account needed — good for iterating on the app before you're ready to push).

Prerequisites: `kind` + `kubectl` installed (`python3 scripts/check_prereqs.py` confirms), Docker running, and the 5 images already buildable (`docker-compose build` works).

## 1. Create the cluster

```bash
kind create cluster --name ml-demo
```

Takes 1-2 minutes the first time. Verify:

```bash
kubectl cluster-info --context kind-ml-demo
kubectl get nodes
```

One node, status `Ready`. `kind create cluster` also points `kubectl`'s current context at the new cluster automatically — no separate config step needed.

## 2. Get your images onto the cluster

Pick one:

### Option A — Docker Hub (matches docs/03, the "real" path)

```bash
python3 scripts/push_to_dockerhub.py YOUR_DOCKERHUB_USERNAME
```

This builds, tags, pushes all 5 images, and rewrites `k8s/*.yaml` to reference `YOUR_DOCKERHUB_USERNAME/<service>:v1`. Skip to **Step 3**.

### Option B — Load local images directly (no Docker Hub account needed)

Build the images locally, then load them straight into the kind node:

```bash
docker-compose build
kind load docker-image ml-smile-service:latest ml-glasses-service:latest ml-eyes-service:latest ml-gateway:latest ml-frontend:latest --name ml-demo
```

`kind load docker-image` copies images from your local Docker daemon directly into the cluster's node — no registry involved. The node will report the image as already present rather than trying to pull it.

Since `k8s/*.yaml` still has the `REPLACE_WITH_YOUR_DOCKERHUB_USERNAME` placeholder (or a real registry name if you ran Option A previously), apply the manifests first (Step 3), then point each Deployment at the local image and tell Kubernetes never to try pulling it:

```bash
kubectl set image deployment/smile-service smile-service=ml-smile-service:latest -n ml-demo
kubectl set image deployment/glasses-service glasses-service=ml-glasses-service:latest -n ml-demo
kubectl set image deployment/eyes-service eyes-service=ml-eyes-service:latest -n ml-demo
kubectl set image deployment/gateway gateway=ml-gateway:latest -n ml-demo
kubectl set image deployment/frontend frontend=ml-frontend:latest -n ml-demo

kubectl patch deployment smile-service -n ml-demo -p '{"spec":{"template":{"spec":{"containers":[{"name":"smile-service","imagePullPolicy":"Never"}]}}}}'
kubectl patch deployment glasses-service -n ml-demo -p '{"spec":{"template":{"spec":{"containers":[{"name":"glasses-service","imagePullPolicy":"Never"}]}}}}'
kubectl patch deployment eyes-service -n ml-demo -p '{"spec":{"template":{"spec":{"containers":[{"name":"eyes-service","imagePullPolicy":"Never"}]}}}}'
kubectl patch deployment gateway -n ml-demo -p '{"spec":{"template":{"spec":{"containers":[{"name":"gateway","imagePullPolicy":"Never"}]}}}}'
kubectl patch deployment frontend -n ml-demo -p '{"spec":{"template":{"spec":{"containers":[{"name":"frontend","imagePullPolicy":"Never"}]}}}}'
```

`imagePullPolicy: Never` tells Kubernetes "this image is already on the node, don't try to fetch it" — without it, the default pull policy for a `:latest` tag is `Always`, and the node would fail trying to pull `ml-smile-service:latest` from Docker Hub (where it doesn't exist).

## 3. Apply the manifests

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/smile-deployment.yaml
kubectl apply -f k8s/glasses-deployment.yaml
kubectl apply -f k8s/eyes-deployment.yaml
kubectl apply -f k8s/gateway-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
```

(If you're using Option B, run the `kubectl set image` / `kubectl patch` commands from Step 2 *after* this.)

## 4. Verify it's running

```bash
kubectl get pods -n ml-demo -w
```

Wait for all 5 pods `Running` / `1/1`. Ctrl+C to stop watching.

```bash
kubectl port-forward -n ml-demo service/frontend 5000:5000
```

Open http://localhost:5000 — same UI, same webcam flow, same predictions, now running through real Kubernetes Services instead of Docker Compose's network.

## 5. Prove the self-heal (the actual point of using Kubernetes)

```bash
kubectl get pods -n ml-demo
kubectl delete pod -n ml-demo <any-pod-name-from-above>
kubectl get pods -n ml-demo
```

A replacement pod starts automatically — that's the Deployment controller doing its job. Refresh the app; it still works. Nobody restarted anything by hand.

## 6. Clean up

```bash
kind delete cluster --name ml-demo
```

Deletes the whole cluster in one shot — nothing left behind to clean up manually.

## Troubleshooting

- **`ImagePullBackOff`**: check `kubectl describe pod -n ml-demo <pod-name>`. Usually means either (Option A) the image name in the manifest doesn't match what you actually pushed, or (Option B) you forgot the `imagePullPolicy: Never` patch.
- **Port-forward connection refused**: pod isn't `Running` yet — check `kubectl get pods -n ml-demo` first.
- **Camera doesn't work through port-forward**: same rule as always — browsers only allow webcam access on `localhost`, and `kubectl port-forward ... 5000:5000` does expose it as `localhost:5000`, so this should just work. If it doesn't, confirm you're opening `http://localhost:5000` and not a pod/service IP directly.
