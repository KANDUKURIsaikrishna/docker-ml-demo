# 06 — Test the deployed app

The frontend Service is `NodePort` type, published on port `30500` (see `k8s/frontend-deployment.yaml`). With `kind`, that port isn't automatically reachable from your laptop's browser, so use `port-forward` — the simplest, most reliable path for a local demo:

```bash
kubectl port-forward -n ml-demo service/frontend 5000:5000
```

Leave that running, then open http://localhost:5000 — same UI as the docker-compose test in step 02, same dropdown, same requests. This time every request travels through real Kubernetes Services instead of the Compose network.

## Confirm it's really Kubernetes

```bash
kubectl get pods -n ml-demo
```

Pick any pod and kill it:

```bash
kubectl delete pod -n ml-demo <smile-service-pod-name>
```

Refresh the app, start the camera again, and capture a frame for the smile model — it still works. `kubectl get pods -n ml-demo` shows a new pod already starting to replace the one you deleted. This is the core promise of a Deployment: something restarts what dies, without you doing anything.

## Compare to compose

Run through the same 3 predictions (smile, glasses, eyes) you tried with `docker-compose up` in step 02. Same containers, same code, same results — only the orchestration layer changed. That parity is the whole lesson of this repo.

## Cleaning up

```bash
kind delete cluster --name ml-demo
```

Next: [07 — Bonus: automate the pipeline with CI/CD](07-bonus-cicd.md)
