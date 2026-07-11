# 04 — Set up a local Kubernetes cluster

You need a Kubernetes cluster to deploy into. `kind` (Kubernetes-in-Docker) is the easiest local option since you already have Docker installed.

> Want the whole kind deployment (docs 04-06) as one file instead of three, plus a way to skip Docker Hub entirely for local testing? See [docs/kind-deployment.md](kind-deployment.md).

> **Docker beginners:** Kubernetes is a program that runs *many* containers across *many* machines, restarts them when they crash, and gives them stable network names to find each other by. `kind` fakes "many machines" using Docker containers, so you get a real cluster without a cloud account.

## Install kind and kubectl

```bash
# macOS
brew install kind kubectl

# Linux — see https://kind.sigs.k8s.io/docs/user/quick-start/#installation
```

## Create the cluster

```bash
kind create cluster --name ml-demo
```

This takes 1-2 minutes the first time (pulls the kind node image). Verify it's up:

```bash
kubectl cluster-info --context kind-ml-demo
kubectl get nodes
```

You should see one node in `Ready` status.

## Already know Docker/K8s basics?

Skip straight to [05 — Deploy to Kubernetes](05-deploy-k8s.md) — nothing else in this step is specific to this project.

Next: [05 — Deploy to Kubernetes](05-deploy-k8s.md)
