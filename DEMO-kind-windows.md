# Live Demo Guide — Kubernetes (kind) — Windows

Same demo as [DEMO-kind.md](DEMO-kind.md) — `kubectl`/`kind` commands are identical on Windows. Only Docker startup and shell syntax differ (PowerShell doesn't have bash's `for svc in ...; do ... done` loop syntax). Self-contained so you don't need to cross-reference mid-demo.

Assumes students have already seen the Docker Compose demo ([DEMO-windows.md](DEMO-windows.md)) — this doc focuses on what's *new*: pods instead of containers, service discovery, and self-healing.

## 0. Before the session

```powershell
python scripts\check_prereqs.py
```

Confirm `kind` and `kubectl` show OK. Start Docker Desktop from the Start menu, wait for "Engine running." Build the images:

```powershell
docker-compose build
```

## 1. Create the cluster, live

```powershell
kind create cluster --name ml-demo
```

Takes 1-2 minutes. While it runs: **"kind is spinning up a real Kubernetes cluster using Docker containers as the 'nodes' — no cloud account, but it's genuinely Kubernetes, not a simulation."**

```powershell
kubectl get nodes
```

One node, `Ready`. `kubectl` automatically points at the new cluster — no separate login step, unlike a cloud cluster.

## 2. Load the images straight in (skip Docker Hub for the demo)

```powershell
kind load docker-image ml-smile-service:latest ml-glasses-service:latest ml-eyes-service:latest ml-gateway:latest ml-frontend:latest --name ml-demo
```

**Talking point:** in the real pipeline (docs/03) these get pushed to Docker Hub first, and the cluster pulls them from there — that's how a real multi-machine cluster gets images. `kind load` is a shortcut that copies images from your laptop straight into the single-node demo cluster, skipping the registry round-trip for speed. Mention this explicitly so students don't think Docker Hub is optional in production.

## 3. Apply the manifests

```powershell
kubectl apply -f k8s\namespace.yaml
kubectl apply -f k8s\smile-deployment.yaml
kubectl apply -f k8s\glasses-deployment.yaml
kubectl apply -f k8s\eyes-deployment.yaml
kubectl apply -f k8s\gateway-deployment.yaml
kubectl apply -f k8s\frontend-deployment.yaml
```

Then point each Deployment at the locally-loaded image (only needed because we skipped Docker Hub in step 2):

```powershell
foreach ($svc in "smile-service","glasses-service","eyes-service","gateway","frontend") {
    kubectl set image "deployment/$svc" "${svc}=ml-${svc}:latest" -n ml-demo
    # Built as a plain string, not an inline escaped literal — PowerShell's
    # quoting rules for external commands get ambiguous with embedded \"
    # escapes. This way there's nothing to escape wrong.
    $patch = '{"spec":{"template":{"spec":{"containers":[{"name":"' + $svc + '","imagePullPolicy":"Never"}]}}}}'
    kubectl patch deployment $svc -n ml-demo -p $patch
}
```

## 4. Show it come up

```powershell
kubectl get pods -n ml-demo
```

**Talking point:** "5 pods, same 5 images as the Docker Compose demo — nothing about the containers changed, only who's managing them." Open `k8s\gateway-deployment.yaml` next to this and point at the `env` block — `http://smile-service:8000`, same hostname pattern as `docker-compose.yml`, resolved by a completely different mechanism (a `Service` object, not Compose's network) underneath.

## 5. Open the app through Kubernetes

```powershell
kubectl port-forward -n ml-demo service/frontend 5000:5000
```

**http://localhost:5000** — same UI, same webcam flow. Run one quick prediction (smile is fastest) just to prove it's live, then move to the actual point of this demo:

## 6. The self-heal moment (the reason to use Kubernetes at all)

```powershell
kubectl get pods -n ml-demo
```

Pick any pod name, then in front of students:

```powershell
kubectl delete pod -n ml-demo <pod-name>
```

Immediately:

```powershell
kubectl get pods -n ml-demo
```

**Talking point:** "I just killed a running service. Watch — a new pod is already starting, nobody restarted anything." This is the entire value proposition of Kubernetes in one command. Refresh the browser and re-run the prediction for whichever model you killed — it works again, usually within a couple seconds.

Compare explicitly to Docker Compose: if you `docker stop` a container there, it *stays stopped* until someone runs `docker start`. That's the actual delta between "containers" and "orchestrated containers."

## 7. Clean up

```powershell
kind delete cluster --name ml-demo
```

One command, whole cluster gone — no leftover state to explain away before the next demo.

## If something goes wrong mid-demo

- **`ImagePullBackOff`**: you skipped the `kubectl patch ... imagePullPolicy Never` step, or a service name typo. `kubectl describe pod -n ml-demo <name>` shows the exact reason.
- **Port-forward hangs / connection refused**: pod isn't `Running` yet. Check `kubectl get pods -n ml-demo` first — don't port-forward to a pod that's still `ContainerCreating`.
- **Camera won't start**: same rule as the Compose demo — must be `http://localhost:5000`, not an IP address.
